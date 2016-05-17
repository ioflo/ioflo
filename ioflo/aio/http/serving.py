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
from ...aid.odicting import odict, lodict, modict
from ...aid import aiding
from ...aid.consoling import getConsole
from ...base import excepting, storing

from ..tcp import Server, ServerTls
from . import httping


console = getConsole()

CRLF = b"\r\n"
LF = b"\n"
CR = b"\r"


#  Class Definitions

class Requestant(httping.Parsent):
    """
    Nonblocking HTTP Server Requestant class
    Parses request msg
    """

    def __init__(self, incomer=None, **kwa):
        """
        Initialize Instance
        Parameters:
            incomer = Incomer connection instance

        """
        super(Requestant, self).__init__(**kwa)
        self.incomer = incomer
        self.url = u''   # full path in request line either relative or absolute
        self.scheme = u''  # scheme used in request line path
        self.hostname = u''  # hostname used in request line path
        self.port = u''  # port used in request line path
        self.path = u''  # partial path in request line without scheme host port query fragment
        self.query = u'' # query string from full path
        self.fragment = u''  # fragment from full path

    def checkPersisted(self):
        """
        Checks headers to determine if connection should be kept open until
        client closes it
        Sets the .persisted flag
        """
        connection = self.headers.get("connection")  # check connection header
        if self.version == (1, 1):  # rules for http v1.1
            self.persisted = True  # connections default to persisted
            connection = self.headers.get("connection")
            if connection and "close" in connection.lower():
                self.persisted = False  # unless connection set to close.

            # non-chunked but persistent connections should have non None for
            # content-length Otherwise assume not persisted
            elif (not self.chunked and self.length is None):
                self.persisted = False

        elif self.version == (1, 0):  # rules for http v1.0
            self.persisted = False  # connections default to non-persisted
            # HTTP/1.0  Connection: keep-alive indicates persistent connection.
            if connection and "keep-alive" in connection.lower():
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
        while True:  # parse until we get full start line
            if self.closed:  # connection closed prematurely
                raise httping.PrematureClosure("Connection closed unexpectedly "
                                               "while parsing request start line")

            line = next(lineParser)
            if line is None:
                (yield None)
                continue
            lineParser.close()  # close generator
            break

        method, url, version = httping.parseRequestLine(line)

        self.method = method
        self.url = url.strip()

        if not version.startswith(u"HTTP/1."):
            raise httping.UnknownProtocol(version)

        if version.startswith(u"HTTP/1.0"):
            self.version = (1, 0)
        else:
            self.version = (1, 1)  # use HTTP/1.1 code for HTTP/1.x where x>=1


        pathSplits = urlsplit(self.url)
        self.path = unquote(pathSplits.path)  # unquote non query path portion here
        self.scheme = pathSplits.scheme
        self.hostname = pathSplits.hostname
        self.port = pathSplits.port
        self.query = httping.unquoteQuery(pathSplits.query)  # unquote only the values
        self.fragment = pathSplits.fragment

        leaderParser = httping.parseLeader(raw=self.msg,
                                   eols=(CRLF, LF),
                                   kind="leader header line")
        while True:
            if self.closed:  # connection closed prematurely
                raise httping.PrematureClosure("Connection closed unexpectedly "
                                               "while parsing request header")

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
        if not self.chunked:
            if contentLength:
                try:
                    self.length = int(contentLength)
                except ValueError:
                    self.length = None
                else:
                    if self.length < 0:  # ignore nonsensical negative lengths
                        self.length = None
            else:  # if no body then neither content-length or chunked required
                self.length = 0  # assume no body so length 0
        else: # ignore content-length if chunked
            self.length = None

        contentType = self.headers.get("content-type")
        if contentType:
            if u';' in contentType: # should also parse out charset for decoding
                contentType, sep, encoding = contentType.rpartition(u';')
                if encoding:
                    self.encoding = encoding

            if 'application/json' in contentType.lower():
                self.jsoned = True
            else:
                self.jsoned = False

        # Should connection be kept open until client closes
        self.checkPersisted()  # sets .persisted

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

        if self.chunked:  # chunked takes precedence over length
            self.parms = odict()
            while True:  # parse all chunks here
                if self.closed:  # connection closed prematurely
                    raise httping.PrematureClosure("Connection closed unexpectedly"
                                                   " while parsing request body chunk")

                chunkParser = httping.parseChunk(raw=self.msg)
                while True:  # parse another chunk
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
                                                   " while parsing request body")

                (yield None)

            self.body = self.msg[:self.length]
            del self.msg[:self.length]

        else:  # unknown content length invalid
            raise httping.HTTPException("Invalid body, content-length not provided!")

        # only gets to here once content length has become finite
        # closed or not chunked or chunking has ended
        self.length = len(self.body)
        self.bodied = True
        (yield True)
        return


class Responder(object):
    """
    Nonblocking HTTP WSGI Responder class

    """
    HttpVersionString = httping.HTTP_11_VERSION_STRING  # http version string
    Delay = 1.0

    def __init__(self,
                 incomer,
                 app,
                 environ,
                 chunkable=False,
                 delay=None):
        """
        Initialize Instance
        Parameters:
            incomer = incomer connection instance
            app = wsgi app callable
            environ = wsgi environment dict
            chunkable = True if may send body in chunks
        """
        self.incomer = incomer
        self.app = app
        self.environ = environ
        self.chunkable = True if chunkable else False

        self.started = False  # True once start called (start_response)
        self.headed = False  # True once headers sent
        self.chunked = False  # True if should send in chunks
        self.ended = False  # True if response body completely sent
        self.closed = False  # True if connection closed by far side
        self.iterator = None  # iterator on application body
        self.status = 200  # integer or string with reason
        self.headers = lodict()  # headers
        self.length = None  # if content-length provided must not exceed
        self.size = 0  # number of body bytes sent so far
        self.evented = False  # True if response is event-stream

    def close(self):
        """
        Close any resources
        """
        self.closed = True

    def reset(self, environ, chunkable=None):
        """
        Reset attributes for another request-response
        """
        self.environ = environ

        if self.chunkable is not None:
            self.chunkable = chunkable

        self.started = False
        self.headed = False
        self.chunked = False
        self.ended = False
        self.iterator = None
        self.status = 200
        self.headers = lodict()
        self.length = None
        self.size = 0

    def build(self):
        """
        Return built head bytes from .status and .headers

        """
        lines = []

        if isinstance(self.status, (int, long)):
            status = "{0} {1}".format(self.status, httping.STATUS_DESCRIPTIONS[self.status])
        else:
            status = self.status

        startLine = "{0} {1}".format(self.HttpVersionString, status)
        try:
            startLine = startLine.encode('ascii')
        except UnicodeEncodeError:
            startLine = startLine.encode('idna')
        lines.append(startLine)

        if u'server' not in self.headers:  # create Server header
            self.headers[u'server'] = "Ioflo WSGI Server"

        if u'date' not in self.headers:  # create Date header
            self.headers[u'date'] = httping.httpDate1123(datetime.datetime.utcnow())

        if self.chunkable and 'transfer-encoding' not in self.headers:
            self.chunked = True
            self.headers[u'transfer-encoding'] = u'chunked'

        for name, value in self.headers.items():
            lines.append(httping.packHeader(name, value))

        lines.extend((b"", b""))
        head = CRLF.join(lines)  # b'/r/n'

        return head

    def write(self, msg):
        """
        WSGI write callback This writes out the headers the first time its called
        otherwise writes the msg bytes
        """
        if not self.started:
            raise AssertionError("WSGI write() before start_response()")

        if not self.headed:  # head not written yet
            head = self.build()
            self.incomer.tx(head)
            self.headed = True

        if self.chunked:
            msg = httping.packChunk(msg)

        if self.length is not None:  # limit total size to length
            size = self.size + len(msg)
            if size > self.length:
                msg = msg[:self.length - size]
            self.size += len(msg)

        if msg:
            self.incomer.tx(msg)

    def start(self, status, response_headers, exc_info=None):
        """
        WSGI application start_response callable

        Parameters:

        status is string of status code and status reason '200 OK'

        response_headers is list of tuples of strings of the form (field, value)
                          one tuple for each header example:
                          [
                              ('Content-type', 'text/plain'),
                              ('X-Some-Header', 'value')
                          ]

        exc_info is optional exception info if exception occurred while
                    processing request in wsgi application
                    If exc_info is supplied, and no HTTP headers have been output yet,
                    start_response should replace the currently-stored
                    HTTP response headers with the newly-supplied ones,
                    thus allowing the application to "change its mind" about
                    the output when an error has occurred.

                    However, if exc_info is provided, and the HTTP headers
                    have already been sent, start_response must raise an error,
                    and should re-raise using the exc_info tuple. That is:

                    raise exc_info[1].with_traceback(exc_info[2]) (python3)
                    raise exc_info[0], exc_info[1], exc_info[2] (python2)
                    Use six.reraise to work for both

        """
        if exc_info:
            try:
                if self.headed:
                    # Re-raise original exception if headers sent
                    reraise(*exc_info)  # sixing.reraise
            finally:
                exc_info = None         # avoid dangling circular ref
        elif self.started:  # may not call start_response again without exc_info
            raise AssertionError("Already started!")

        self.status = status
        self.headers = lodict(response_headers)

        if u'content-length' in self.headers:
            self.length = int(self.headers['content-length'])
            self.chunkable = False  # cannot use chunking with finite content-length
        else:
            self.length = None

            if u'content-type' in self.headers:
                if self.headers['content-type'].startswith('text/event-stream'):
                    self.evented = True

        self.started = True
        return self.write

    def service(self):
        """
        Service application
        """
        if not self.closed and not self.ended:
            if self.iterator is None:  # initiate application
                self.iterator = iter(self.app(self.environ, self.start))

            try:
                msg = next(self.iterator)
            except StopIteration:
                self.write(b'')  # if chunked send empty chunk to terminate
                self.ended = True
            except Exception as ex:  # handle http exceptions not caught by app
                if not self.headed and hasattr(ex, 'status'):
                    # assumes exception looks like bottle HTTPError
                    headers = lodict()
                    if hasattr(ex, 'headerlist'):
                        headers.update(ex.headerlist)
                    if 'content-type' not in headers:
                        headers['content-type'] = 'text/plain'
                    msg = b''
                    if hasattr(ex, 'body'):
                        msg = ex.body
                        if isinstance(msg, unicode):
                            msg = msg.encode('iso-8859-1')
                    headers['content-length'] = str(len(msg))
                    self.start(ex.status, headers.items(), sys.exc_info())
                    self.write(msg)
                    self.ended = True
                else:
                    raise

            else:
                if msg:
                    self.write(msg)
                    if self.length is not None and self.size >= self.length:
                        self.ended = True


class Valet(object):
    """
    Valet WSGI Server Class
    """
    Timeout = 5.0  # default server connection timeout

    def __init__(self,
                 app=None,
                 reqs=None,
                 reps=None,
                 servant=None,
                 store=None,
                 name='',
                 bufsize=8096,
                 wlog=None,
                 ha=None,
                 host=u'',
                 port=None,
                 eha=None,
                 scheme=u'',
                 timeout=None,
                 **kwa):
        """
        Initialization method for instance.
        app = wsgi application callable
        reqs = odict of Requestant instances keyed by ca
        reps = odict of running Wsgi Responder instances keyed by ca
        servant = instance of Server or ServerTls or None
        store = Datastore for timers

        kwa needed to pass additional parameters to servant

        if servantinstances are not provided (None)
        some or all of these parameters will be used for initialization

        name = user friendly name for servant
        bufsize = buffer size
        wlog = WireLog instance if any
        ha = host address duple (host, port) for local servant listen socket
        host = host address for local servant listen socket, '' means any interface on host
        port = socket port for local servant listen socket
        eha = external destination address for incoming connections used in TLS
        scheme = http scheme u'http' or u'https' or empty

        """
        self.app = app
        self.reqs = reqs if reqs is not None else odict()
        self.reps = reps if reps is not None else odict()
        self.store = store or storing.Store(stamp=0.0)
        if not name:
            name = "Ioflo_WSGI_server"
        self.timeout = timeout if timeout is not None else self.Timeout

        ha = ha or (host, port)  # ha = host address takes precendence over host, port
        if servant:
            if isinstance(servant, ServerTls):
                if scheme and scheme != u'https':
                    raise  ValueError("Provided scheme '{0}' incompatible with servant".format(scheme))
                secured = True
                scheme = u'https'
                defaultPort = 443
            elif isinstance(servant, Server):
                if scheme and scheme != u'http':
                    raise  ValueError("Provided scheme '{0}' incompatible with servant".format(scheme))
                secured = False
                scheme = 'http'
                defaultPort = 80
            else:
                raise ValueError("Invalid servant type {0}".format(type(servant)))
        else:
            scheme = u'https' if scheme == u'https' else u'http'
            if scheme == u'https':
                secured = True  # use tls socket connection
                defaultPort = 443
            else:
                secured = False # non tls socket connection
                defaultPort = 80

        self.scheme = scheme
        host, port = ha
        port = port or  defaultPort  # if port not specified
        ha = (host, port)

        if servant:
            if servant.ha != ha:
                ValueError("Provided ha '{0}:{1}' incompatible with servant".format(ha[0], ha[1]))
            # at some point may want to support changing the ha of provided servant

        else:  # what about timeouts for servant connections
            if secured:
                servant = ServerTls(store=self.store,
                                    name=name,
                                    ha=ha,
                                    eha=eha,
                                    bufsize=bufsize,
                                    wlog=wlog,
                                    timeout=self.timeout,
                                    **kwa)
            else:
                servant = Server(store=self.store,
                                 name=name,
                                 ha=ha,
                                 eha=eha,
                                 bufsize=bufsize,
                                 wlog=wlog,
                                 timeout=self.timeout,
                                 **kwa)


        self.secured = secured
        self.servant = servant

    def idle(self):
        """
        Returns True if no connections have requests in process
        Useful for debugging
        """
        idle = True
        for requestant in self.reqs.values():
            if not requestant.ended:
                idle = False
                break
        if idle:
            for responder in self.reps.values():
                if not responder.ended:
                    idle = False
                    break
        return idle

    def buildEnviron(self, requestant):
        """
        Returns wisgi environment dictionary for supplied requestant
        """
        environ = odict()  # maybe should be modict for cookies or other repeated headers

        # WSGI variables
        environ['wsgi.version'] = (1, 0)
        environ['wsgi.url_scheme'] = self.scheme
        environ['wsgi.input'] = io.BytesIO(requestant.body)
        environ['wsgi.errors'] = sys.stderr
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = False
        environ['wsgi.run_once'] = False
        environ["wsgi.server_name"] = self.servant.name
        environ["wsgi.server_version"] = (1, 0)

        # Required CGI variables
        environ['REQUEST_METHOD'] = requestant.method      # GET
        environ['SERVER_NAME'] = self.servant.eha[0]      # localhost
        environ['SERVER_PORT'] = str(self.servant.eha[1])  # 8888
        environ['SERVER_PROTOCOL'] = "HTTP/{0}.{1}".format(*requestant.version)  # used by request http/1.1
        environ['SCRIPT_NAME'] = u''
        environ['PATH_INFO'] = requestant.path        # /hello?name=john

        # Optional CGI variables
        environ['QUERY_STRING'] = requestant.query        # name=john
        environ['REMOTE_ADDR'] = requestant.incomer.ca
        environ['CONTENT_TYPE'] = requestant.headers.get('content-type', '')
        if requestant.length is not None:
            environ['CONTENT_LENGTH'] = str(requestant.length)

        # recieved http headers mapped to all caps with HTTP_ prepended
        for key, value in requestant.headers.items():
            key = "HTTP_" + key.replace("-", "_").upper()
            environ[key] = value

        return environ

    def closeConnection(self, ca):
        """
        Close and remove connection given by ca
        """
        self.servant.removeIx(ca)
        if ca in self.reqs:
            self.reqs[ca].close()  # this signals request parser
            del self.reqs[ca]
        if ca in self.reps:
            self.reps[ca].close()  # this signals response handler
            del self.reps[ca]

    def serviceConnects(self):
        """
        Service new incoming connections
        Create requestants
        Timeout stale connections
        """
        self.servant.serviceConnects()
        for ca, ix in self.servant.ixes.items():
            if ix.cutoff:
                self.closeConnection(ca)
                continue

            if ca not in self.reqs:
                self.reqs[ca] = Requestant(msg=ix.rxbs, incomer=ix)

            if ix.timeout > 0.0 and ix.timer.expired:
                self.closeConnection(ca)

    def serviceReqs(self):
        """
        Service pending requestants
        """
        for ca, requestant in self.reqs.items():
            if requestant.parser:
                try:
                    requestant.parse()
                except httping.HTTPException as ex:  # this may be superfluous
                    #requestant.errored = True
                    #requestant.error = str(ex)
                    #requestant.ended = True
                    sys.stderr.write(str(ex))
                    self.closeConnection(ca)
                    continue

                if requestant.ended:
                    if requestant.errored:  # parse may swallow error but set .errored and .error
                        sys.stderr.write(requestant.error)
                        self.closeConnection(ca)
                        continue

                    console.concise("Parsed Request:\n{0} {1} {2}\n"
                                    "{3}\n{4}\n".format(requestant.method,
                                                        requestant.path,
                                                        requestant.version,
                                                        requestant.headers,
                                                        requestant.body))
                    # create or restart wsgi app responder here
                    environ = self.buildEnviron(requestant)
                    if ca not in self.reps:
                        chunkable = True if requestant.version >= (1, 1) else False
                        responder = Responder(incomer=requestant.incomer,
                                                  app=self.app,
                                                  environ=environ,
                                                  chunkable=chunkable)
                        self.reps[ca] = responder
                    else:  # reuse
                        responder = self.reps[ca]
                        responder.reset(environ=environ)

    def serviceReps(self):
        """
        Service pending responders
        """
        for ca, respondent in self.reps.items():
            if respondent.closed:
                self.closeConnection(ca)
                continue

            if not respondent.ended:
                respondent.service()

            if respondent.ended:
                requestant = self.reqs[ca]
                if requestant.persisted:
                    if requestant.parser is None:  # reuse
                        requestant.makeParser()  # resets requestant parser
                else:  # not persistent so close and remove requestant and responder
                    ix = self.servant.ixes[ca]
                    if not ix.txes:  # wait for outgoing txes to be empty
                        self.closeConnection(ca)

    def serviceAll(self):
        """
        Service request response
        """
        self.serviceConnects()
        self.servant.serviceReceivesAllIx()
        self.serviceReqs()
        self.serviceReps()
        self.servant.serviceTxesAllIx()


class CustomResponder(object):
    """
    Nonblocking HTTP Server Response class

    HTTP/1.1 200 OK\r\n
    Content-Length: 122\r\n
    Content-Type: application/json\r\n
    Date: Thu, 30 Apr 2015 19:37:17 GMT\r\n
    Server: IoBook.local\r\n\r\n
    """
    HttpVersionString = httping.HTTP_11_VERSION_STRING  # http version string

    def __init__(self,
                 steward=None,
                 status=200,  # integer
                 headers=None,
                 body=b'',
                 data=None):
        """
        Initialize Instance
        steward = managing Steward instance
        status = response status code
        headers = http response headers
        body = http response body
        data = dict to jsonify as body if provided
        """
        self.steward = steward
        self.status = status
        self.headers = lodict(headers) if headers else lodict()
        if body and isinstance(body, unicode):  # use default
            # RFC 2616 Section 3.7.1 default charset of iso-8859-1.
            body = body.encode('iso-8859-1')
        self.body = body or b''
        self.data = data

        self.ended = False  # True if response generated completed

        self.msg = b""  # for debugging
        self.lines = []  # for debugging
        self.head = b""  # for debugging


    def reinit(self,
               status=None,  # integer
               headers=None,
               body=None,
               data=None):
        """
        Reinitialize anything that is not None
        This enables creating another response on a connection
        """
        if status is not None:
            self.status = status
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

    def build(self,
              status=None,
              headers=None,
              body=None,
              data=None):
        """
        Build and return response message

        """
        self.reinit(status=status,
                    headers=headers,
                    body=body,
                    data=data)
        self.lines = []

        startLine = "{0} {1} {2}".format(self.HttpVersionString,
                                         self.status,
                                         httping.STATUS_DESCRIPTIONS[self.status])
        try:
            startLine = startLine.encode('ascii')
        except UnicodeEncodeError:
            startLine = startLine.encode('idna')
        self.lines.append(startLine)

        if u'server' not in self.headers:  # create Server header
            self.headers[u'server'] = "Ioflo Server"

        if u'date' not in self.headers:  # create Date header
            self.headers[u'date'] = httping.httpDate1123(datetime.datetime.utcnow())

        if self.data is not None:
            body = ns2b(json.dumps(self.data, separators=(',', ':')))
            self.headers[u'content-type'] = u'application/json; charset=utf-8'
        else:
            body = self.body

        if body and (u'content-length' not in self.headers):
            self.headers[u'content-length'] = str(len(body))

        for name, value in self.headers.items():
            self.lines.append(httping.packHeader(name, value))

        self.lines.extend((b"", b""))
        self.head = CRLF.join(self.lines)  # b'/r/n'

        self.msg = self.head + body
        self.ended = True
        return self.msg

class Steward(object):
    """
    Manages the associated requestant and responder for an incoming connection
    """
    def __init__(self,
                 incomer,
                 requestant=None,
                 responder=None,
                 dictable=False):
        """
        incomer = Incomer instance for connection
        requestant = Requestant instance for connection
        responder = Responder instance for connection
        dictable = True if should attempt to convert request body as json
        """
        self.incomer = incomer
        if requestant is None:
            requestant = Requestant(msg=self.incomer.rxbs,
                                    incomer=incomer,
                                    dictable=dictable)
        self.requestant = requestant

        if responder is None:
            responder = CustomResponder(steward=self)
        self.responder = responder
        self.waited = False  # True if waiting for reponse to finish
        self.msg = b""  # outgoing msg bytes

    def refresh(self):
        """
        Restart incomer timer
        """
        incomer.timer.restart()

    def respond(self):
        """
        Respond to request  Override in subclass
        Echo request
        """
        console.concise("Responding to Request:\n{0} {1} {2}\n"
                                "{3}\n{4}\n".format(self.requestant.method,
                                                    self.requestant.path,
                                                    self.requestant.version,
                                                    self.requestant.headers,
                                                    self.requestant.body))
        data = odict()
        data['version'] = "HTTP/{0}.{1}".format(*self.requestant.version)
        data['method'] = self.requestant.method

        pathSplits = urlsplit(unquote(self.requestant.url))
        path = pathSplits.path
        data['path'] = path

        query = pathSplits.query
        qargs = odict()
        qargs, query = httping.updateQargsQuery(qargs, query)
        data['qargs'] = qargs

        fragment = pathSplits.fragment
        data['fragment'] = fragment

        data['headers'] = copy.copy(self.requestant.headers)  # make copy
        data['body'] = self.requestant.body.decode('utf-8')
        data['data'] = copy.copy(self.requestant.data)  # make copy

        msg = self.responder.build(status=200, data=data)
        self.incomer.tx(msg)
        self.waited = not self.responder.ended

    def pour(self):
        """
        Run generator to stream response message

        """

        # putnext generator here

        if self.responder.ended:
            self.waited = False
        else:
            self.refresh()


class Porter(object):
    """
    Porter class nonblocking HTTP server
    """
    Timeout = 5.0  # default server connection timeout

    def __init__(self,
                 servant=None,
                 store=None,
                 stewards=None,
                 name='',
                 bufsize=8096,
                 wlog=None,
                 ha=None,
                 host=u'',
                 port=None,
                 eha=None,
                 scheme=u'',
                 dictable=False,
                 timeout=None,
                 **kwa):
        """
        Initialization method for instance.
        servant = instance of Server or ServerTls or None
        store = Datastore for timers
        stewards = odict of Steward instances
        kwa needed to pass additional parameters to servant

        if servantinstances are not provided (None)
        some or all of these parameters will be used for initialization

        name = user friendly name for servant
        bufsize = buffer size
        wlog = WireLog instance if any
        ha = host address duple (host, port) for local servant listen socket
        host = host address for local servant listen socket, '' means any interface on host
        port = socket port for local servant listen socket
        eha = external destination address for incoming connections used in TLS
        scheme = http scheme u'http' or u'https' or empty
        dictable = Boolean flag If True attempt to convert body from json for requestants

        """
        self.store = store or storing.Store(stamp=0.0)
        self.stewards = stewards if stewards is not None else odict()
        self.dictable = True if dictable else False  # for stewards
        self.timeout = timeout if timeout is not None else self.Timeout

        ha = ha or (host, port)  # ha = host address takes precendence over host, port
        if servant:
            if isinstance(servant, ServerTls):
                if scheme and scheme != u'https':
                    raise  ValueError("Provided scheme '{0}' incompatible with servant".format(scheme))
                secured = True
                scheme = u'https'
                defaultPort = 443
            elif isinstance(servant, Server):
                if scheme and scheme != u'http':
                    raise  ValueError("Provided scheme '{0}' incompatible with servant".format(scheme))
                secured = False
                scheme = 'http'
                defaultPort = 80
            else:
                raise ValueError("Invalid servant type {0}".format(type(servant)))
        else:
            scheme = u'https' if scheme == u'https' else u'http'
            if scheme == u'https':
                secured = True  # use tls socket connection
                defaultPort = 443
            else:
                secured = False # non tls socket connection
                defaultPort = 80

        host, port = ha
        port = port or  defaultPort  # if port not specified
        ha = (host, port)

        if servant:
            if servant.ha != ha:
                ValueError("Provided ha '{0}:{1}' incompatible with servant".format(ha[0], ha[1]))
            # at some point may want to support changing the ha of provided servant

        else:  # what about timeouts for servant connections
            if secured:
                servant = ServerTls(store=self.store,
                                    name=name,
                                    ha=ha,
                                    eha=eha,
                                    bufsize=bufsize,
                                    wlog=wlog,
                                    timeout=self.timeout,
                                    **kwa)
            else:
                servant = Server(store=self.store,
                                 name=name,
                                 ha=ha,
                                 eha=eha,
                                 bufsize=bufsize,
                                 wlog=wlog,
                                 timeout=self.timeout,
                                 **kwa)


        self.secured = secured
        self.servant = servant

    def idle(self):
        """
        Returns True if no connections have requests in process
        Useful for debugging
        """
        idle = True
        for steward in self.stewards.values():
            if not steward.requestant.ended:
                idle = False
                break
        return idle

    def closeConnection(self, ca):
        """
        Close and remove connection and associated steward given by ca
        """
        self.servant.removeIx(ca)
        del self.stewards[ca]

    def serviceConnects(self):
        """
        Service new incoming connections
        Create requestants
        Timeout stale connections
        """
        self.servant.serviceConnects()
        for ca, ix in self.servant.ixes.items():
            # check for and handle cutoff connections by client here

            if ca not in self.stewards:
                self.stewards[ca] = Steward(incomer=ix, dictable=self.dictable)

            if ix.timeout > 0.0 and ix.timer.expired:
                self.closeConnection(ca)

    def serviceStewards(self):
        """
        Service pending requestants and responders
        """
        for ca, steward in self.stewards.items():
            if not steward.waited:
                steward.requestant.parse()

                if steward.requestant.ended:
                    steward.requestant.dictify()
                    console.concise("Parsed Request:\n{0} {1} {2}\n"
                                    "{3}\n{4}\n".format(steward.requestant.method,
                                                        steward.requestant.path,
                                                        steward.requestant.version,
                                                        steward.requestant.headers,
                                                        steward.requestant.body))
                    steward.respond()

            if steward.waited:
                steward.pour()

            if not steward.waited and steward.requestant.ended:
                if steward.requestant.persisted:
                    steward.requestant.makeParser()  #set up for next time
                else:  # remove and close connection
                    self.closeConnection(ca)

    def serviceAll(self):
        """
        Service request response
        """
        self.serviceConnects()
        self.servant.serviceReceivesAllIx()
        self.serviceStewards()
        self.servant.serviceTxesAllIx()

