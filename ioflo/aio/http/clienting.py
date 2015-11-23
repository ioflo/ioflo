"""
httping.py

nonblocking http classes


"""
from __future__ import absolute_import, division, print_function


import sys
import os
import socket
import errno
import io
from collections import deque
import codecs
import json
import ssl
import copy
import random
import datetime

if sys.version > '3':
    from urllib.parse import urlsplit, quote, quote_plus, unquote, unquote_plus
else:
    from urlparse import urlsplit
    from urllib import quote, quote_plus, unquote, unquote_plus

try:
    import simplejson as json
except ImportError:
    import json

from email.parser import HeaderParser

# Import ioflo libs
from ...aid.sixing import *
from ...aid import aiding
from ...aid.odicting import odict, lodict, modict
from ...aid.consoling import getConsole
from ...base import excepting, storing

from ..tcp import Client, ClientTls, Server, ServerTls
from . import httping


console = getConsole()

CRLF = b"\r\n"
LF = b"\n"
CR = b"\r"

#  Class Definitions

class Requester(object):
    """
    Nonblocking HTTP Client Request class
    """
    HttpVersionString = httping.HTTP_11_VERSION_STRING  # http version string
    Port = httping.HTTP_PORT  # default port

    def __init__(self,
                 hostname='127.0.0.1',
                 port=None,
                 scheme=u'http',
                 method=u'GET',  # unicode
                 path=u'/',  # unicode
                 qargs=None,
                 fragment=u'', #unicode
                 headers=None,
                 body=b'',
                 data=None,
                 fargs=None):
        """
        Initialize Instance

        hostname = remote server hostname (may include port as hostname:port)
        port = remote server port
        scheme = http scheme 'http' or 'https' usually
        method = http request method verb
        path = http url path
        qargs = http query args
        fragment = http fragment
        headers = http request headers
        body = http request body
        data = dict to jsonify as body if provided
        fargs = dict to url form encode as body if provided
        """
        self.hostname, self.port = httping.normalizeHostPort(hostname, port, 80)
        self.scheme = scheme
        self.method = method.upper() if method else u'GET'
        self.path = path or u'/'
        self.qargs = qargs if qargs is not None else odict()
        self.fragment = fragment
        self.headers = lodict(headers) if headers else lodict()
        if body and isinstance(body, unicode):  # use default
            # RFC 2616 Section 3.7.1 default charset of iso-8859-1.
            body = body.encode('iso-8859-1')
        self.body = body or b''
        self.data = data
        self.fargs = fargs

        self.lines = []  # keep around for testing
        self.head = b""  # keep around for testing
        self.msg = b""

    def reinit(self,
               hostname=None,
               port=None,
               scheme=None,
               method=None,  # unicode
               path=None,  # unicode
               qargs=None,
               fragment=None,
               headers=None,
               body=None,
               data=None,
               fargs=None):
        """
        Reinitialize anything that is not None
        This enables creating another request on a connection to the same host port
        """
        if hostname is not None: # may need to renormalize host port
            self.hostname = hostname
        if port is not None:
            self.port = port
        if scheme is not None:
            self.scheme = scheme
        if method is not None:
            self.method = method.upper()
        if path is not None:
            self.path = path
        if qargs is not None:
            self.qargs = qargs
        if fragment is not None:
            self.fragment = fragment
        if headers is not None:
            self.headers = lodict(headers)
        if body is not None:  # body should be bytes
            if isinstance(body, unicode):
                # RFC 2616 Section 3.7.1 default charset of iso-8859-1.
                body = body.encode('iso-8859-1')
            self.body = body
        else:
            self.body = b''
        if data is not None:
            self.data = data
        else:
            self.data = None
        if fargs is not None:
            self.fargs = fargs
        else:
            self.fargs = None

    def build(self,
              method=None,
              path=None,
              qargs=None,
              fragment=None,
              headers=None,
              body=None,
              data=None,
              fargs=None):
        """
        Build and return request message

        """
        self.reinit(method=method,
                    path=path,
                    qargs=qargs,
                    fragment=fragment,
                    headers=headers,
                    body=body,
                    data=data,
                    fargs=fargs)
        self.lines = []

        # need to check for proxy as the start line is different if proxied

        pathSplits = urlsplit(self.path)  # path should not include scheme host port
        path = pathSplits.path
        self.path = path
        path = quote(path)

        scheme = pathSplits.scheme
        if scheme and scheme != self.scheme:
            raise  ValueError("Already open connection attempt to change scheme  "
                              " to '{0}'".format(scheme))

        port = pathSplits.port
        if port and port != self.port:
            raise  ValueError("Already open connection attempt to change port  "
                              " to '{0}'".format(port))

        hostname = pathSplits.hostname
        if hostname and hostname != self.hostname:
            raise  ValueError("Already open connection attempt to change hostname  "
                                  " to '{0}'".format(hostname))

        query = pathSplits.query
        self.qargs, query = httping.updateQargsQuery(self.qargs, query)

        fragment = pathSplits.fragment
        if fragment:
            self.fragment = fragment
        # we should quote the fragment  here

        combine = u"{0}?{1}#".format(path, query, fragment)
        combine = urlsplit(combine).geturl()  # strips blank parts

        startLine = "{0} {1} {2}".format(self.method, combine, self.HttpVersionString)
        try:
            startLine = startLine.encode('ascii')
        except UnicodeEncodeError:
            startLine = startLine.encode('idna')
        self.lines.append(startLine)

        if u'host' not in self.headers:  # create Host header
            host = self.hostname
            port = self.port

            # As per RFC 273, IPv6 address should be wrapped with []
            # when used as Host header
            if host.find(u':') >= 0:
                host = u'[' + host + u']'

            value = "{0}:{1}".format(host, port)

            try:
                value = value.encode("ascii")
            except UnicodeEncodeError:
                value = value.encode("idna")

            self.lines.append(httping.packHeader('Host', value))

        # we only want a Content-Encoding of "identity" since we don't
        # support encodings such as x-gzip or x-deflate.
        if u'accept-encoding' not in self.headers:
            self.lines.append(httping.packHeader(u'Accept-Encoding', u'identity'))

        if self.method == u"GET":  # do not send body on GET
                body = b''
        else:
            if self.data is not None:
                body = ns2b(json.dumps(self.data, separators=(',', ':')))
                self.headers[u'content-type'] = u'application/json; charset=utf-8'
            elif self.fargs is not None:
                if ((u'content-type' in self.headers and
                        self.headers[u'content-type'].startswith(u'multipart/form-data'))):
                    boundary = '____________{0:012x}'.format(random.randint(123456789,
                                                            0xffffffffffff))

                    formParts = []
                    # mime parts always start with --
                    for key, val in  self.fargs.items():
                        formParts.append('\r\n--{0}\r\nContent-Disposition: '
                                         'form-data; name="{1}"\r\n'
                                         'Content-Type: text/plain; charset=utf-8\r\n'
                                         '\r\n{2}'.format(boundary, key, val))
                    formParts.append('\r\n--{0}--'.format(boundary))
                    form = "".join(formParts)
                    body = form.encode(encoding='utf-8')
                    self.headers[u'content-type'] = u'multipart/form-data; boundary={0}'.format(boundary)
                else:
                    formParts = [u"{0}={1}".format(key, val) for key, val in self.fargs.items()]
                    form = u'&'.join(formParts)
                    form = quote_plus(form, '&=')
                    body = form.encode(encoding='utf-8')
                    self.headers[u'content-type'] = u'application/x-www-form-urlencoded; charset=utf-8'
            else:
                body = self.body

        if body and (u'content-length' not in self.headers):
            self.lines.append(httping.packHeader(u'Content-Length', str(len(body))))

        for name, value in self.headers.items():
            self.lines.append(httping.packHeader(name, value))

        self.lines.extend((b"", b""))
        self.head = CRLF.join(self.lines)  # b'/r/n'

        self.msg = self.head + body
        return self.msg


class Respondent(httping.Parsent):
    """
    Nonblocking HTTP Client Response class
    """
    Retry = 100  # retry timeout in milliseconds if evented

    def __init__(self,
                 redirects=None,
                 redirectable=True,
                 events=None,
                 retry=None,
                 leid=None,
                 **kwa):
        """
        Initialize Instance:

        redirects = list of redirects if any
        redirectable = Boolean allow redirects
        events = deque of events if any
        retry = retry timeout in seconds if any if evented
        leid = last event id if any if evented
        """
        super(Respondent, self).__init__(**kwa)

        self.status = None  # Status-Code from status line
        self.reason = None  # Reason-Phrase from status line

        self.redirectant = None  # Boolean True if received redirect status, need to redirect
        self.redirected = None  # attempted a redirection
        self.redirects = redirects if redirects is not None else []
        self.redirectable = True if redirectable else False

        self.evented = None   # are server sent events being used
        self.events = events if events is not None else deque()
        self.retry = retry if retry is not None else self.Retry  # retry timeout in milliseconds if evented
        self.leid = None  # non None if evented with event ids sent
        self.eventSource = None  # httping.EventSource instance when .evented

    def reinit(self,
               redirectable=None,
               **kwa):
        """
        Reinitialize Instance
        See super class
        redirectable means allow redirection
        """
        super(Respondent, self).reinit(**kwa)
        if redirectable is not None:
            self.redirectable = True if redirectable else False

    def close(self):
        """
        Assign True to .closed
        Close event source
        """
        super(Respondent, self).close()
        if self.eventSource:  # assign True to .eventSource.closed
            self.eventSource.close()

    def checkPersisted(self):
        """
        Checks headers to determine if connection should be kept open until
        server closes it
        Sets the .persisted flag
        """
        connection = self.headers.get("connection")  # check connection header
        if self.version == (1, 1):  # rules for http v1.1
            self.persisted = True  # connections default to persisted
            # An HTTP/1.1 proxy is assumed to stay open unless
            # explicitly closed.
            connection = self.headers.get("connection")
            if connection and "close" in connection.lower():
                self.persisted = False

            # non-chunked but persistent connections should have non None for
            # content-length Otherwise assume not persisted
            elif (not self.chunked and self.length is None):
                self.persisted = False

        elif self.version == (1, 0):
            self.persisted = False  # connections default to non-persisted
            # Some HTTP/1.0 implementations have support for persistent
            # connections, using rules different than HTTP/1.1.

            if self.evented:  # server sent events
                self.persisted = True

            # For older HTTP, Keep-Alive indicates persistent connection.
            elif self.headers.get("keep-alive"):
                self.persisted = True

            # At least Akamai returns a "Connection: Keep-Alive" header,
            # which was supposed to be sent by the client.
            elif connection and "keep-alive" in connection.lower():
                self.persisted = True

            else:  # Proxy-Connection is a netscape hack.
                proxy = self.headers.get("proxy-connection")
                if proxy and "keep-alive" in proxy.lower():
                    self.persisted = True

    def parseHead(self):
        """
        Generator to parse headers in heading of .msg
        Yields None if more to parse
        Yields True if done parsing
        """
        if self.headed:
            return  # already parsed the head

        self.headers = lodict()

        # create generator
        lineParser = httping.parseLine(raw=self.msg, eols=(CRLF, LF), kind="status line")
        while True:  # parse until we get a non-100 status
            if self.closed:  # connection closed prematurely
                raise httping.PrematureClosure("Connection closed unexpectedly"
                                               " while parsing response start line")

            line = next(lineParser)
            if line is None:
                (yield None)
                continue
            lineParser.close()  # close generator

            version, status, reason = httping.parseStatusLine(line)
            if status != httping.CONTINUE:  # 100 continue (with request or ignore)
                break

            leaderParser = httping.parseLeader(raw=self.msg,
                                            eols=(CRLF, LF),
                                            kind="continue header line")
            while True:
                if self.closed:  # connection closed prematurely
                    raise httping.PrematureClosure("Connection closed "
                            "unexpectedly while parsing response header")
                headers = next(leaderParser)
                if headers is not None:
                    leaderParser.close()
                    break
                (yield None)

        self.code = self.status = status
        self.reason = reason.strip()
        if version in ("HTTP/1.0", "HTTP/0.9"):
            # Some servers might still return "0.9", treat it as 1.0 anyway
            self.version = (1, 0)
        elif version.startswith("HTTP/1."):
            self.version = (1, 1)  # use HTTP/1.1 code for HTTP/1.x where x>=1
        else:
            raise httping.UnknownProtocol(version)

        leaderParser = httping.parseLeader(raw=self.msg,
                                   eols=(CRLF, LF),
                                   kind="leader header line")
        while True:
            if self.closed:  # connection closed prematurely
                raise httping.PrematureClosure("Connection closed unexpectedly"
                                               " while parsing response header")
            headers = next(leaderParser)
            if headers is not None:
                leaderParser.close()
                break
            (yield None)
        self.headers.update(headers)

        # are we using the chunked-style of transfer encoding?
        transferEncoding = self.headers.get("transfer-encoding")
        if transferEncoding and transferEncoding.lower() == "chunked":
            self.chunked = True
        else:
            self.chunked = False

        # NOTE: RFC 2616, S4.4, #3 says ignore if transfer-encoding is "chunked"
        contentLength = self.headers.get("content-length")
        if contentLength and not self.chunked:
            try:
                self.length = int(contentLength)
            except ValueError:
                self.length = None
            else:
                if self.length < 0:  # ignore nonsensical negative lengths
                    self.length = None
        else:
            self.length = None

        # does the body have a fixed length? (of zero)
        if ((self.status == httping.NO_CONTENT or self.status == httping.NOT_MODIFIED) or
                (100 <= self.status < 200) or      # 1xx codes
                (self.method == "HEAD")):
            self.length = 0

        contentType = self.headers.get("content-type")
        if contentType:
            if u';' in contentType: # should also parse out charset for decoding
                contentType, sep, encoding = contentType.rpartition(u';')
                if encoding:
                    self.encoding = encoding

            if 'text/event-stream' in contentType.lower():
                self.evented = True
                self.eventSource = httping.EventSource(raw=self.body,
                                           events=self.events,
                                           dictable=self.dictable)
            else:
                self.evented = False

            if 'application/json' in contentType.lower():
                self.jsoned = True
            else:
                self.jsoned = False

        # Should connection be kept open until server closes
        self.checkPersisted()  # sets .persisted

        if self.status in (httping.MULTIPLE_CHOICES,
                           httping.MOVED_PERMANENTLY,
                           httping.FOUND,
                           httping.SEE_OTHER,
                           httping.TEMPORARY_REDIRECT):
            self.redirectant = True

        self.headed = True
        yield True
        return

    def parseBody(self):
        """
        Parse body
        """
        if self.bodied:
            return  # already parsed the body

        if self.length and self.length < 0:
            raise ValueError("Invalid content length of {0}".format(self.length))

        del self.body[:]  # self.body.clear() clear body python2 bytearrays don't clear

        if self.chunked:  # content-length is ignored if chunked
            self.parms = odict()
            while True:  # parse all chunks here
                chunkParser = httping.parseChunk(raw=self.msg)
                while True:  # parse another chunk
                    if self.closed:  # connection closed prematurely
                        raise httping.PrematureClosure("Connection closed "
                                "unexpectedly while parsing response body chunk")
                    result = next(chunkParser)
                    if result is not None:
                        chunkParser.close()
                        break
                    (yield None)

                size, parms, trails, chunk = result

                if parms:  # chunk extension parms
                    self.parms.update(parms)

                if size:  # size non zero so append chunk but keep iterating
                    self.body.extend(chunk)
                    if self.evented:
                        self.eventSource.parse()  # parse events here
                        if (self.eventSource.retry is not None and
                                self.retry != self.eventSource.retry):
                            self.retry = self.eventSource.retry
                        if (self.eventSource.leid is not None and
                                self.leid != self.eventSource.leid):
                            self.leid = self.eventSource.leid

                    if self.closed:  # no more data so finish
                        chunkParser.close()
                        break

                else:  # last chunk when empty chunk so done
                    if trails:
                        self.trails = trails
                    chunkParser.close()
                    break

        elif self.length != None:  # known content length
            while len(self.msg) < self.length:
                if self.closed:  # connection closed prematurely
                    raise httping.PrematureClosure("Connection closed unexpectedly"
                                                   " while parsing response body")
                (yield None)

            self.body = self.msg[:self.length]
            del self.msg[:self.length]

        else:  # unknown content length so parse forever until closed
            while True:
                if self.msg:
                    self.body.extend(self.msg[:])
                    del self.msg[:]  # python2 bytearrays dont have clear self.msg.clear()

                if self.evented:
                    self.eventSource.parse()  # parse events here
                    if (self.eventSource.retry is not None and
                            self.retry != self.eventSource.retry):
                        self.retry = self.eventSource.retry
                    if (self.eventSource.leid is not None and
                            self.leid != self.eventSource.leid):
                        self.leid = self.eventSource.leid

                if self.closed:  # no more data so finish
                    break

                (yield None)

        # only gets to here once content length has become finite
        # closed, not chunked/streamed, or chunking/streaming has ended
        self.length = len(self.body)
        self.bodied = True
        (yield True)
        return


class Patron(object):
    """
    Patron class nonblocking HTTP client connection manager
    """
    def __init__(self,
                 connector=None,
                 requester=None,
                 respondent=None,
                 store=None,
                 name='',
                 uid=0,
                 bufsize=8096,
                 wlog=None,
                 hostname='127.0.0.1',
                 port=None,
                 scheme=u'',
                 method=u'GET',  # unicode
                 path=u'/',  # unicode
                 headers=None,
                 qargs=None,
                 fragment=u'',
                 body=b'',
                 data=None,
                 fargs=None,
                 msg=None,
                 dictable=None,
                 events=None,
                 requests=None,
                 responses=None,
                 redirectable=True,
                 redirects=None,
                 **kwa):
        """
        Initialization method for instance.
        kwa needed to pass other init parameters to connector

        connector = instance of Outgoer or OutgoerTls or None
        requester = instance of Requester or None
        respondent = instance of Respondent or None

        if either of requester, respondent instances are not provided (None)
        some or all of these parameters will be used for initialization

        name = user friendly name for connection
        uid = unique identifier for connection
        bufsize = buffer size
        wlog = WireLog instance if any
        host = host address or hostname of remote server
        port = socket port of remote server
        scheme = http scheme
        method = http request method verb unicode
        path = http url path section in unicode
               path may include scheme and netloc which takes priority
        qargs = dict of http query args
        fragment = http fragment
        headers = dict of http headers
        body = byte or binary array of request body bytes or bytearray
        data = dict of request body json if any
        fargs = dict of request body form args if any
        msg = bytearray of response msg to parse
        dictable = Boolean flag If True attempt to convert body from json
        events = deque of events if any
        requests = deque of requests if any each request is dict
        responses = deque of responses if any each response is dict
        redirectable = Boolean is allow redirects
        redirects = list of redirects if any each redirect is dict
        """
        # .requests is deque of dicts of request data
        self.requests = requests if requests is not None else deque()
        # .responses is deque of dicts of response data
        self.responses = responses if responses is not None else deque()
        # .redicrest is list of dicts of response data when response is redirect
        self.redirects = redirects if redirects is not None else list()
        # .events is deque of dicts of response server sent event data
        self.events = events if events is not None else deque()
        self.waited = False  # Boolean True If sent request but waiting for response
        self.request = None  # current request odict from .requests in process if any
        self.store = store or storing.Store(stamp=0.0)

        # see if path also includes scheme, netloc, query, fragment
        splits = urlsplit(path)
        scheme = splits.scheme or scheme  # is scheme provided
        scheme = scheme.lower()

        if connector:
            if isinstance(connector, ClientTls):
                if scheme and scheme != u'https':
                    raise  ValueError("Provided scheme '{0}' incompatible with connector".format(scheme))
                secured = True
                scheme = u'https'
                defaultPort = 443
            elif isinstance(connector, Client):
                if scheme and scheme != u'http':
                    raise  ValueError("Provided scheme '{0}' incompatible with connector".format(scheme))
                secured = False
                scheme = 'http'
                defaultPort = 80
            else:
                raise ValueError("Invalid connector type {0}".format(type(connector)))
        else:
            scheme = u'https' if scheme == u'https' else u'http'
            if scheme == u'https':
                secured = True  # use tls socket connection
                defaultPort = 443
            else:
                secured = False # non tls socket connection
                defaultPort = 80

        hostname = splits.hostname or hostname  # is host or port provided
        port = splits.port or port  # is port provided
        hostname, port = httping.normalizeHostPort(host=hostname, port=port, defaultPort=defaultPort)
        host = socket.gethostbyname(hostname)
        ha = (host, port)

        if connector:
            if connector.hostname != hostname:
                ValueError("Provided hostname '{0}' incompatible with connector".format(hostname))
            if connector.ha != ha:
                ValueError("Provided ha '{0}' incompatible with connector".format(hostname))
            # at some point may want to support changing the hostname and ha of provided connector
        else:
            if secured:
                connector = ClientTls(store=self.store,
                                       name=name,
                                       uid=uid,
                                       host=hostname,
                                       port=port,
                                       bufsize=bufsize,
                                       wlog=wlog,
                                       **kwa)
            else:
                connector = Client(store=self.store,
                                    name=name,
                                    uid=uid,
                                    host=hostname,
                                    port=port,
                                    bufsize=bufsize,
                                    wlog=wlog,
                                    **kwa)

        self.secured = secured
        self.connector = connector

        path = splits.path  # only path component

        query = splits.query  # is query in original path
        qargs = qargs or odict()
        qargs, query = httping.updateQargsQuery(qargs, query)

        fragment = splits.fragment or fragment  # fragment in path prioritized


        if requester is None:
            requester = Requester(hostname=self.connector.hostname,
                                  port=self.connector.port,
                                  scheme=scheme,
                                  method=method,
                                  path=path,  # unicode
                                  headers=headers,
                                  qargs=qargs,
                                  fragment=fragment,
                                  body=body,
                                  data=data,
                                  fargs=fargs)
        else:
            requester.reinit(hostname=self.connector.hostname,
                             port=self.connector.port,
                             scheme=scheme,
                             method=method,
                             path=path,
                             qargs=qargs,
                             fragment=fragment,
                             headers=headers,
                             body=body,
                             data=data,
                             fargs=fargs)
        self.requester = requester

        if respondent is None:
            respondent = Respondent(msg=self.connector.rxbs,
                                    method=method,
                                    dictable=dictable,
                                    events=self.events,
                                    redirectable=redirectable,
                                    redirects=self.redirects)
        else:
            # do we need to assign the events, redirects also?
            respondent.reinit(msg=self.connector.rxbs,
                              method=method,
                              dictable=dictable,
                              redirectable=redirectable)
        self.respondent = respondent

    def transmit(self,
                 method=None,
                 path=None,
                 qargs=None,
                 fragment=None,
                 headers=None,
                 body=None,
                 data=None,
                 fargs=None):
        """
        Build and transmit request
        Add jsoned parameter
        """
        self.waited = True
        # build calls reinit
        request = self.requester.build(method=method,
                                       path=path,
                                       qargs=qargs,
                                       fragment=fragment,
                                       headers=headers,
                                       body=body,
                                       data=data,
                                       fargs=fargs)
        self.connector.tx(request)
        self.respondent.reinit(method=method)

    def redirect(self):
        """
        Perform redirect
        """
        if self.redirects:
            redirect = self.redirects[-1]
            location = redirect['headers'].get('location')
            path, sep, query = location.partition('?')
            path = unquote(path)
            if sep:
                location = sep.join([path, query])
            else:
                location = path
            splits = urlsplit(location)
            hostname = splits.hostname
            port = splits.port
            scheme = splits.scheme
            scheme = 'https' if scheme.lower() == 'https' else 'http'
            if scheme == 'https':
                secured = True  # use tls socket connection
                defaultPort = 443
            else:
                secured = False # non tls socket connection
                defaultPort = 80
            hostname, port = httping.normalizeHostPort(hostname, port=port, defaultPort=defaultPort)
            path = splits.path
            query = splits.query
            fragment = splits.fragment

            method = redirect.get('method')

            host = socket.gethostbyname(hostname)
            ha = (host, port)
            if ha != self.connector.ha or scheme != self.requester.scheme:
                if self.requester.scheme == 'https' and scheme != 'https':
                    raise  ValueError("Attempt to redirect to non secure "
                                      "host '{0}'".format(location))
                self.connector.close()
                if secured:
                    context = getattr(self.connector, 'context')
                    connector = ClientTls(store=self.connector.store,
                                           name=self.connector.name,
                                           uid=self.connector.uid,
                                           ha=(hostname, port),
                                           bufsize=self.connector.bs,
                                           wlog=self.connector.wlog,
                                           context=context)
                else:
                    connector = Client(store=self.connector.store,
                                        name=self.connector.name,
                                        uid=self.connector.uid,
                                        ha=(hostname, port),
                                        bufsize=self.connector.bs,
                                        wlog=self.connector.wlog,)

                self.secured = secured
                self.connector = connector
                self.connector.reopen()
                self.requester.reinit(hostname=hostname,
                                      port=port,
                                      scheme=scheme)
                self.respondent.reinit(msg=self.connector.rxbs,
                                       method=method)

            qargs = odict()
            qargs, query = httping.updateQargsQuery(qargs, query)

            self.transmit(method=method, path=path, qargs=qargs, fragment=fragment)

            self.respondent.redirectant = False
            self.respondent.redirected = True
            self.respondent.ended = False  # since redirecting not done

    def serviceRequests(self):
        """
        Service requests deque
        """
        if not self.waited:
            if self.requests:
                self.request = request = self.requests.popleft()
                # future check host port scheme if need to reconnect on new ha
                # reconnect here
                self.transmit(method=request.get('method'),
                             path=request.get('path'),
                             qargs=request.get('qargs'),
                             fragment=request.get('fragment'),
                             headers=request.get('headers'),
                             body=request.get('body'),
                             data=request.get('data'),
                             fargs=request.get('fargs'))

    def serviceResponse(self):
        """
        Service Rx on connection and parse
        """
        self.connector.serviceReceives()
        if self.waited:
            try:
                self.respondent.parse()
            except httping.HTTPException as ex:
                self.respondent.errored = True
                self.respondent.error = str(ex)
                self.respondent.ended = True

            if self.respondent.ended:
                self.respondent.dictify()

                if not self.respondent.evented:
                    if self.request:  # use saved request attribute
                        request = copy.copy(self.request)
                        request.update([
                                        ('host', self.requester.hostname),
                                        ('port', self.requester.port),
                                        ('scheme', self.requester.scheme),
                                        ('method', self.requester.method),
                                        ('path', self.requester.path),
                                        ('fragment', self.requester.fragment),
                                        ('qargs', copy.copy(self.requester.qargs)),
                                        ('headers', copy.copy(self.requester.headers)),
                                        ('body', self.requester.body),
                                        ('data', self.requester.data),
                                        ('fargs', copy.copy(self.requester.fargs)),
                                       ])
                        self.request = None
                    else:
                        request = odict([
                                         ('host', self.requester.hostname),
                                         ('port', self.requester.port),
                                         ('scheme', self.requester.scheme),
                                         ('method', self.requester.method),
                                         ('path', self.requester.path),
                                         ('fragment', self.requester.fragment),
                                         ('qargs', copy.copy(self.requester.qargs)),
                                         ('headers', copy.copy(self.requester.headers)),
                                         ('body', self.requester.body),
                                         ('data', self.requester.data),
                                         ('fargs', copy.copy(self.requester.fargs)),
                                        ])
                    response = odict([('version', self.respondent.version),
                                      ('status', self.respondent.status),
                                      ('reason', self.respondent.reason),
                                      ('headers', copy.copy(self.respondent.headers)),
                                      ('body', self.respondent.body),
                                      ('data', self.respondent.data),
                                      ('request', request),
                                      ('errored', self.respondent.errored),
                                      ('error', self.respondent.error),
                                     ])
                    if self.respondent.redirectable and self.respondent.redirectant:
                        self.redirects.append(copy.copy(response))
                        self.redirect()
                    else:
                        if self.redirects:
                            response['redirects'] = copy.copy(self.redirects)
                        self.redirects = []
                        self.responses.append(response)
                        self.waited = False
                self.respondent.makeParser()  #set up for next time

    def serviceAll(self):
        """
        Service request response
        """
        if self.connector.cutoff:
            if self.respondent:
                self.respondent.close()  # close any pending or current response parsing

            if self.connector.reconnectable:
                if self.connector.timeout > 0.0 and self.connector.timer.expired:  # timed out
                    self.connector.reopen()
                    if self.respondent.evented:
                        duration = float(self.respondent.retry) / 1000.0 # convert to seconds
                    else:
                        duration = None  # reused current duration
                    self.connector.timer.restart(duration=duration)

        if not self.connector.connected:
            self.connector.serviceConnect()
            if self.connector.connected:
                if self.respondent:
                    if self.respondent.evented and self.respondent.leid is not None:  # update Last-Event-ID header
                        self.requester.headers['Last-Event-ID'] = self.respondent.leid
                        self.transmit()  # rebuilds and queues up most recent http request here
                        self.connector.txes.rotate()  # ensure first request in txes

        self.serviceRequests()
        self.connector.serviceTxes()
        self.serviceResponse()


