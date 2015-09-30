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
from .sixing import *
from .odicting import odict, lodict
from ..base import excepting
from ..base import storing
from . import aiding
from .nonblocking import Outgoer, OutgoerTls, Server, ServerTls

from ..base.consoling import getConsole
console = getConsole()

CRLF = b"\r\n"
LF = b"\n"
CR = b"\r"
MAX_LINE_SIZE = 65536
MAX_HEADERS = 100

HTTP_PORT = 80
HTTPS_PORT = 443
HTTP_11_VERSION_STRING = u'HTTP/1.1'  # http v1.1 version string

# status codes
# informational
CONTINUE = 100

# These constants are here for potential backwards compatibility
# currently most are unused
# status codes
# informational

SWITCHING_PROTOCOLS = 101
PROCESSING = 102

# successful
OK = 200
CREATED = 201
ACCEPTED = 202
NON_AUTHORITATIVE_INFORMATION = 203
NO_CONTENT = 204
RESET_CONTENT = 205
PARTIAL_CONTENT = 206
MULTI_STATUS = 207
IM_USED = 226

# redirection
MULTIPLE_CHOICES = 300
MOVED_PERMANENTLY = 301
FOUND = 302
SEE_OTHER = 303
NOT_MODIFIED = 304
USE_PROXY = 305
TEMPORARY_REDIRECT = 307

# client error
BAD_REQUEST = 400
UNAUTHORIZED = 401
PAYMENT_REQUIRED = 402
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
NOT_ACCEPTABLE = 406
PROXY_AUTHENTICATION_REQUIRED = 407
REQUEST_TIMEOUT = 408
CONFLICT = 409
GONE = 410
LENGTH_REQUIRED = 411
PRECONDITION_FAILED = 412
REQUEST_ENTITY_TOO_LARGE = 413
REQUEST_URI_TOO_LONG = 414
UNSUPPORTED_MEDIA_TYPE = 415
REQUESTED_RANGE_NOT_SATISFIABLE = 416
EXPECTATION_FAILED = 417
UNPROCESSABLE_ENTITY = 422
LOCKED = 423
FAILED_DEPENDENCY = 424
UPGRADE_REQUIRED = 426
PRECONDITION_REQUIRED = 428
TOO_MANY_REQUESTS = 429
REQUEST_HEADER_FIELDS_TOO_LARGE = 431

# server error
INTERNAL_SERVER_ERROR = 500
NOT_IMPLEMENTED = 501
BAD_GATEWAY = 502
SERVICE_UNAVAILABLE = 503
GATEWAY_TIMEOUT = 504
HTTP_VERSION_NOT_SUPPORTED = 505
INSUFFICIENT_STORAGE = 507
NOT_EXTENDED = 510
NETWORK_AUTHENTICATION_REQUIRED = 511

# Mapping status codes to official W3C names
responses = {
    100: 'Continue',
    101: 'Switching Protocols',

    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',

    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: '(Unused)',
    307: 'Temporary Redirect',

    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    428: 'Precondition Required',
    429: 'Too Many Requests',
    431: 'Request Header Fields Too Large',

    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    511: 'Network Authentication Required',
}

METHODS = (u'GET', u'HEAD', u'PUT', u'PATCH', u'POST', u'DELETE',
           u'OPTIONS', u'TRACE', u'CONNECT' )

# maximal amount of data to read at one time in _safe_read
MAXAMOUNT = 1048576

# maximal line length when calling readline().
_MAXLINE = 65536
_MAXHEADERS = 100

class HTTPException(Exception):
    # Subclasses that define an __init__ must call Exception.__init__
    # or define self.args.  Otherwise, str() will fail.
    pass

class InvalidURL(HTTPException):
    pass


class UnknownProtocol(HTTPException):
    def __init__(self, version):
        self.args = version,
        self.version = version

class BadStatusLine(HTTPException):
    def __init__(self, line):
        if not line:
            line = repr(line)
        self.args = line,
        self.line = line

class BadStartLine(BadStatusLine):
    pass

class BadMethod(HTTPException):
    def __init__(self, method):
        self.args = method,
        self.method = method

class LineTooLong(HTTPException):
    def __init__(self, kind):
        HTTPException.__init__(self, "got more than %d bytes while parsing %s"
                                     % (MAX_LINE_SIZE, kind))


# Utility functions

def normalizeHostPort(host, port=None, defaultPort=80):
    """
    Given hostname host which could also be netloc which includes port
    and or port
    generate and return tuple (hostname, port)
    priority is if port is provided in hostname as host:port then use
    otherwise use port otherwise use defaultPort
    """
    if port is None:
        port = defaultPort

    # rfind  returns -1 if not found
    # ipv6
    i = host.rfind(u':')  # is port included in hostname
    j = host.rfind(u']')  # ipv6 addresses have [...]
    if i > j:  # means ':' is found
        if host[i+1:]:  # non empty after ':' since 'hostname:' == 'hostname'
            port = host[i+1:]
        host = host[:i]

    if host and host[0] == u'[' and host[-1] == u']':  # strip of ipv6 brackets
        host = host[1:-1]

    try:
        port = int(port)
    except ValueError:
        raise InvalidURL("Nonnumeric port: '{0}'".format(port))

    return (host, port)


def parseLine(raw, eols=(CRLF, LF, CR ), kind="event line"):
    """
    Generator to parse  line from raw bytearray
    Each line demarcated by one of eols
    kind is line type string for error message

    Yields None If waiting for more to parse
    Yields line Otherwise

    Consumes parsed portions of raw bytearray

    Raise error if eol not found before MAX_LINE_SIZE
    """
    while True:
        for eol in eols:  # loop over eols unless found
            index = raw.find(eol)  # not found index == -1
            if index >= 0:
                break

        if index < 0:  # not found
            if len(raw) > MAX_LINE_SIZE:
                raise LineTooLong(kind)
            else:
                (yield None)  # more data needed not done parsing header
                continue

        if index > MAX_LINE_SIZE:  # found but line too long
            raise LineTooLong(kind)

        line = raw[:index]
        index += len(eol)  # strip eol
        del raw[:index] # remove used bytes
        (yield line)
    return

def parseLeader(raw, eols=(CRLF, LF), kind="leader header line", headers=None):
    """
    Generator to parse entire leader of header lines from raw bytearray
    Each line demarcated by one of eols
    Yields None If more to parse
    Yields lodict of headers Otherwise as indicated by empty headers

    Raise error if eol not found before  MAX_LINE_SIZE
    """
    headers = headers if headers is not None else lodict()
    while True:  # loop until entire heading indicated by empty line
        for eol in eols:  # loop over eols unless found
            index = raw.find(eol)  # not found index == -1
            if index >= 0:
                break

        if index < 0:  # not found
            if len(raw) > MAX_LINE_SIZE:
                raise LineTooLong(kind)
            else:
                (yield None)  # more data needed not done parsing header
                continue

        if index > MAX_LINE_SIZE:  # found but line too long
            raise LineTooLong(kind)

        line = raw[:index]
        index += len(eol)  # strip eol
        del raw[:index] # remove used bytes
        if line:
            line = line.decode('iso-8859-1')  # convert to unicode string
            key, value = line.split(': ', 1)
            headers[key] = value

        if len(headers) > MAX_HEADERS:
            raise HTTPException("Too many headers, more than {0}".format(MAX_HEADERS))

        if not line:  # empty line so entire leader done
            (yield headers) # leader done
    return

def parseChunk(raw):  # reading transfer encoded raw
    """
    Generator to parse next chunk from raw bytearray
    Consumes used portions of raw
    Yields None If waiting for more bytes
    Yields tuple (size, parms, trails, chunk) Otherwise
    Where:
        size is int size of the chunk
        parms is dict of chunk extension parameters
        trails is dict of chunk trailer headers (only on last chunk if any)
        chunk is chunk if any or empty if not

    Chunked-Body   = *chunk
                last-chunk
                trailer
                CRLF
    chunk          = chunk-size [ chunk-extension ] CRLF
                     chunk-data CRLF
    chunk-size     = 1*HEX
    last-chunk     = 1*("0") [ chunk-extension ] CRLF
    chunk-extension= *( ";" chunk-ext-name [ "=" chunk-ext-val ] )
    chunk-ext-name = token
    chunk-ext-val  = token | quoted-string
    chunk-data     = chunk-size(OCTET)
    trailer        = *(entity-header CRLF)
    """
    size = 0
    parms = odict()
    trails = lodict()
    chunk = bytearray()

    lineParser = parseLine(raw=raw, eols=(CRLF, ), kind="chunk size line")
    while True:
        line = next(lineParser)
        if line is not None:
            lineParser.close()  # close generator
            break
        (yield None)

    size, sep, exts = line.partition(b';')
    try:
        size = int(size.strip().decode('ascii'), 16)
    except ValueError:  # bad size
        raise

    if exts:  # parse extensions parameters
        exts = exts.split(b';')
        for ext in exts:
            ext = ext.strip()
            name, sep, value = ext.partition(b'=')
            parms[name.strip()] = value.strip() or None

    if size == 0:  # last chunk so parse trailing headers if any
        leaderParser = parseLeader(raw=raw,
                                   eols=(CRLF, LF),
                                   kind="trailer header line")
        while True:
            headers = next(leaderParser)
            if headers is not None:
                leaderParser.close()
                break
            (yield None)
        trails.update(headers)

    else:
        while len(raw) < size:  # need more for chunk
            (yield None)

        chunk = raw[:size]
        del raw[:size]  # remove used bytes

        lineParser = parseLine(raw=raw, eols=(CRLF, ), kind="chunk end line")
        while True:
            line = next(lineParser)
            if line is not None:
                lineParser.close()  # close generator
                break
            (yield None)

        if line:  # not empty so raise error
            raise ValueError("Chunk end error. Expected empty got "
                     "'{0}' instead".format(line.decode('iso-8859-1')))

    (yield (size, parms, trails, chunk))
    return

def parseBom(raw, bom=codecs.BOM_UTF8):
    """
    Generator to parse bom from raw bytearray
    Yields None If waiting for more to parse
    Yields bom If found
    Yields empty bytearray Otherwise
    Consumes parsed portions of raw bytearray
    """
    size = len(bom)
    while True:
        if len(raw) >= size:  # enough bytes for bom
            if raw[:size] == bom: # bom present
                del raw[:size]
                (yield bom)
                break
            (yield raw[0:0])  # bom not present so yield empty bytearray
            break
        (yield None)  # not enough bytes yet
    return

def parseStatusLine(line):
    """
    Parse the response status line
    """
    line = line.decode("iso-8859-1")
    if not line:
        raise BadStatusLine(line) # connection closed before sending valid msg

    version, status, reason = aiding.repack(3, line.split(), default = u'')
    reason = u" ".join(reason)

    if not version.startswith("HTTP/"):
        raise BadStatusLine(line)

    # The status code is a three-digit number
    try:
        status = int(status)
        if status < 100 or status > 999:
            raise BadStatusLine(line)
    except ValueError:
        raise BadStatusLine(line)
    return (version, status, reason)

def parseRequestLine(line):
    """
    Parse the request start line
    """
    line = line.decode("iso-8859-1")
    if not line:
        raise BadStartLine(line)  # connection closed before sending valid msg

    method, path, version = aiding.repack(3, line.split(), default = u'')

    if not version.startswith("HTTP/"):
        raise UnkownProtocol(version)

    if method not in METHODS:
        raise BadMethod(method)

    return (method, path, version)


#  Class Definitions

class Requester(object):
    """
    Nonblocking HTTP Client Request class
    """
    HttpVersionString = HTTP_11_VERSION_STRING  # http version string
    Port = HTTP_PORT  # default port

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
        self.hostname, self.port = normalizeHostPort(hostname, port, 80)
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
        self.lines = []
        self.head = b""
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
        if query:
            if u';' in query:
                querySplits = query.split(u';')
            elif u'&' in query:
                querySplits = query.split(u'&')
            else:
                querySplits = [query]
            for queryPart in querySplits:  # this prevents duplicates even if desired
                if queryPart:
                    if '=' in queryPart:
                        key, val = queryPart.split('=', 1)
                        val = unquote(val)
                    else:
                        key = queryPart
                        val = u'true'
                    self.qargs[key] = val

        qargParts = [u"{0}={1}".format(key, quote_plus(str(val)))
                                       for key, val in self.qargs.items()]
        query = '&'.join(qargParts)

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

            self.lines.append(self.packHeader('Host', value))

        # we only want a Content-Encoding of "identity" since we don't
        # support encodings such as x-gzip or x-deflate.
        if u'accept-encoding' not in self.headers:
            self.lines.append(self.packHeader(u'Accept-Encoding', u'identity'))

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
            self.lines.append(self.packHeader(u'Content-Length', str(len(body))))

        for name, value in self.headers.items():
            self.lines.append(self.packHeader(name, value))

        self.lines.extend((b"", b""))
        self.head = CRLF.join(self.lines)  # b'/r/n'

        self.msg = self.head + body
        return self.msg

    def packHeader(self, name, *values):
        """
        Format and return a request header line.

        For example: h.packHeader('Accept', 'text/html')
        """
        if isinstance(name, unicode):  # not bytes
            name = name.encode('ascii')
        name = name.title()
        values = list(values)  # make copy
        for i, value in enumerate(values):
            if isinstance(value, unicode):
                values[i] = value.encode('iso-8859-1')
            elif isinstance(value, int):
                values[i] = str(value).encode('ascii')
        value = b', '.join(values)
        value = value.lower()
        return (name + b': ' + value)


class EventSource(object):
    """
    Server Sent Event Stream Client parser
    """
    Bom = codecs.BOM_UTF8 # utf-8 encoded bom b'\xef\xbb\xbf'

    def __init__(self, raw=None, events=None, dictify=False):
        """
        Initialize Instance
        raw must be bytearray
        IF events is not None then used passed in deque
            .events will be deque of event odicts
        IF dictify then deserialize event data as json

        """
        self.raw = raw if raw is not None else bytearray()
        self.events = events if events is not None else deque()
        self.dictify = True if dictify else False

        self.parser = None
        self.leid = None  # last event id
        self.bom = None  # bom if any
        self.retry = None  # reconnection time in milliseconds
        self.ended = None
        self.closed = None

        self.makeParser()

    def close(self):
        """
        Assign True to .closed
        """
        self.closed = True

    def parseEvents(self):
        """
        Generator to parse events from .raw bytearray and append to .events
        Each event is odict with the following items:
             id: event id utf-8 decoded or empty
           name: event name utf-8 decoded or empty
           data: event data utf-8 decoded
           json: event data deserialized to odict when applicable pr None

        assigns .retry if any

        Yields None If waiting for more bytes
        Yields True When done


        event         = *( comment / field ) end-of-line
        comment       = colon *any-char end-of-line
        field         = 1*name-char [ colon [ space ] *any-char ] end-of-line
        end-of-line   = ( cr lf / cr / lf / eof )
        eof           = < matches repeatedly at the end of the stream >
        lf            = \n 0xA
        cr            = \r 0xD
        space         = 0x20
        colon         = 0x3A
        bom           = \uFEFF when encoded as utf-8 b'\xef\xbb\xbf'
        name-char     = a Unicode character other than LF, CR, or :
        any-char      = a Unicode character other than LF or CR
        Event streams in this format must always be encoded as UTF-8. [RFC3629]
        """
        eid = self.leid
        ename = u''
        edata = u''
        parts = []
        ejson = None
        lineParser = parseLine(raw=self.raw, eols=(CRLF, LF, CR ), kind="event line")
        while True:
            line = next(lineParser)
            if line is None:
                (yield None)
                continue

            if not line or self.closed:  # empty line or closed so attempt dispatch
                if parts:
                    edata = u'\n'.join(parts)
                if edata:  # data so dispatch event by appending to .events
                    if self.dictify:
                        try:
                            ejson = json.loads(edata, encoding='utf-8', object_pairs_hook=odict)
                        except ValueError as ex:
                            ejson = None
                        else:  # valid json set edata to ejson
                            edata = ejson

                    self.events.append(odict([('id', eid),
                                              ('name', ename),
                                              ('data', edata),
                                             ]))
                if self.closed:  # all done
                    lineParser.close()  # close generator
                    break
                ename = u''
                edata = u''
                parts = []
                ejson = None
                continue  # parse another event if any

            field, sep, value = line.partition(b':')
            if sep:  # has colon
                if not field:  # comment so ignore
                    # may need to update retry timer here
                    continue

            field = field.decode('UTF-8')
            if value and value[0:1] == b' ':
                del value[0]
            value = value.decode('UTF-8')

            if field == u'event':
                ename = value
            elif field == u'data':
                parts.append(value)
            elif field == u'id':
                self.leid = eid = value
            elif field == u'retry':  #
                try:
                    value = int(value)
                except ValueError as ex:
                    pass  # ignore
                else:
                    self.retry = value

        (yield (eid, ename, edata))
        return

    def parseEventStream(self):
        """
        Generator to parse event stream from .raw bytearray stream
        appends each event to .events deque.
        assigns .bom if any
        assigns .retry if any
        Parses until connection closed

        Each event is odict with the following items:
              id: event id utf-8 decoded or empty
            name: event name utf-8 decoded or empty
            data: event data utf-8 decoded
            json: event data deserialized to odict when applicable pr None

        Yields None If waiting for more bytes
        Yields True When completed and sets .ended to True
        If BOM present at beginning of event stream then assigns to .bom and
        deletes.
        Consumes bytearray as it parses

        stream        = [ bom ] *event
        event         = *( comment / field ) end-of-line
        comment       = colon *any-char end-of-line
        field         = 1*name-char [ colon [ space ] *any-char ] end-of-line
        end-of-line   = ( cr lf / cr / lf / eof )
        eof           = < matches repeatedly at the end of the stream >
        lf            = \n 0xA
        cr            = \r 0xD
        space         = 0x20
        colon         = 0x3A
        bom           = \uFEFF when encoded as utf-8 b'\xef\xbb\xbf'
        name-char     = a Unicode character other than LF, CR, or :
        any-char      = a Unicode character other than LF or CR
        Event streams in this format must always be encoded as UTF-8. [RFC3629]
        """
        self.bom = None
        self.retry = None
        self.leid = None
        self.ended = None
        self.closed = None

        bomParser = parseBom(raw=self.raw, bom=self.Bom)
        while True:  # parse bom if any
            bom = next(bomParser)
            if bom is not None:
                bomParser.close()  # close generator
                self.bom = bom.decode('UTF-8')
                break

            if self.closed:  # no more data so finish
                bomParser.close()
                break
            (yield None)

        eventsParser = self.parseEvents()
        while True:  # parse event(s) so far if any
            result = next(eventParser)
            if result is not None:
                eventsParser.close()
                break
            (yield None)

        (yield True)
        return

    def makeParser(self, raw=None):
        """
        Make event stream parser generator and assign to .parser
        Assign msg to .msg If provided
        """
        if raw:
            self.raw = raw
        self.parser = self.parseEvents()  # make generator

    def parse(self):
        """
        Service the event stream parsing
        must call .makeParser to setup parser
        When done parsing,
           .parser is None
           .ended is True
        """
        if self.parser:
            result = next(self.parser)
            if result is not None:
                self.parser.close()
                self.parser = None


class Parsery(object):
    """
    Base class for objects that parse HTTP messages
    """
    def __init__(self,
                 msg=None,
                 wlog=None,
                 dictify=None,
                 method=u'GET'):
        """
        Initialize Instance
        msg = bytearray of request msg to parse
        wlog = WireLog instance if any
        dictify = True If should attempt to convert body to json
        method = method of associated request
        """
        self.msg = msg if msg is not None else bytearray()
        self.wlog = wlog
        self.dictify = True if dictify else False  # convert body json
        self.parser = None  # response parser generator
        self.version = None # HTTP-Version from status line
        self.length = None     # content length of body in request
        self.chunked = None    # is transfer encoding "chunked" being used?
        self.jsoned = None    # is content application/json
        self.encoding = 'ISO-8859-1'  # encoding charset if provided else default
        self.persisted = None   # persist connection until client closes
        self.headed = None    # head completely parsed
        self.bodied =  None   # body completely parsed
        self.ended = None     # response from server has ended no more remaining
        self.closed = None  # True when connection closed

        self.headers = None
        self.parms = None  # chunked encoding extension parameters
        self.trails = None  # chunked encoding trailing headers
        self.body = bytearray()  # body data bytearray
        self.text = u''  # body decoded as unicode string
        self.data = None  # content dict deserialized from body json
        self.method = method.upper() if method else u'GET'

        self.makeParser(msg=msg)  # assigns self.msg

    def reinit(self,
               msg=None,
               dictify=None,
               method=u'GET'):
        """
        Reinitialize Instance
        msg = bytearray of request msg to parse
        dictify = Boolean flag If True attempt to convert json body
        method = method verb of associated request
        """
        if msg is not None:
            self.msg = msg
        if dictify is not None:
            self.dictify = True if dictify else False
        if method is not None:
            self.method = method.upper()

    def close(self):
        """
        Assign True to .closed
        """
        self.closed = True

    def checkPersisted(self):
        """
        Checks headers to determine if connection should be kept open until
        client closes it
        Sets the .persisted flag
        """
        self.persisted = False

    def parseHead(self):
        """
        Generator to parse headers in heading of .msg
        Yields None if more to parse
        Yields True if done parsing
        """
        if self.headed:
            return  # already parsed the head
        self.headers = lodict()
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
        self.bodied = True
        (yield True)
        return

    def parseMessage(self):
        """
        Generator to parse message bytearray.
        Parses msg if not None
        Otherwise parse .msg
        """
        self.headed = False
        self.bodied = False
        self.ended = False
        self.closed = False

        headParser = self.parseHead()
        while True:
            result = next(headParser)
            if result is not None:
                headParser.close()
                break
            (yield None)

        bodyParser = self.parseBody()
        while True:
            result = next(bodyParser)
            if result is not None:
                bodyParser.close()
                break
            (yield None)

        self.ended = True
        (yield True)
        return

    def makeParser(self, msg=None):
        """
        Make message parser generator and assign to .parser
        Assign msg to .msg If provided
        """
        if msg:
            self.msg = msg
        self.parser = self.parseMessage()  # make generator

    def parse(self):
        """
        Service the message parsing
        must call .makeParser to setup parser
        When done parsing,
           .parser is None
           .ended is True
        """
        if self.parser:
            result = next(self.parser)
            if result is not None:
                self.parser.close()
                self.parser = None


class Respondent(Parsery):
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
        self.eventSource = None  # EventSource instance when .evented

    def reinit(self,
               redirectable=None,
               **kwa):
        """
        Reinitialize Instance
        See super class
        dictify = Boolean flag If True attempt to convert json body
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
        if self.version == 11:  # rules for http v1.1
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

        elif self.version == 10:
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
        lineParser = parseLine(raw=self.msg, eols=(CRLF, LF), kind="status line")
        while True:  # parse until we get a non-100 status
            line = next(lineParser)
            if line is None:
                (yield None)
                continue
            lineParser.close()  # close generator

            version, status, reason = parseStatusLine(line)
            if status != CONTINUE:  # 100 continue (with request or ignore)
                break

            leaderParser = parseLeader(raw=self.msg,
                                            eols=(CRLF, LF),
                                            kind="continue header line")
            while True:
                headers = next(leaderParser)
                if headers is not None:
                    leaderParser.close()
                    break
                (yield None)

        self.code = self.status = status
        self.reason = reason.strip()
        if version in ("HTTP/1.0", "HTTP/0.9"):
            # Some servers might still return "0.9", treat it as 1.0 anyway
            self.version = 10
        elif version.startswith("HTTP/1."):
            self.version = 11   # use HTTP/1.1 code for HTTP/1.x where x>=1
        else:
            raise UnknownProtocol(version)

        leaderParser = parseLeader(raw=self.msg,
                                   eols=(CRLF, LF),
                                   kind="leader header line")
        while True:
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
        if ((self.status == NO_CONTENT or self.status == NOT_MODIFIED) or
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
                self.eventSource = EventSource(raw=self.body,
                                           events=self.events,
                                           dictify=self.dictify)
            else:
                self.evented = False

            if 'application/json' in contentType.lower():
                self.jsoned = True
            else:
                self.jsoned = False

        # Should connection be kept open until server closes
        self.checkPersisted()  # sets .persisted

        if self.status in (MULTIPLE_CHOICES,
                           MOVED_PERMANENTLY,
                           FOUND,
                           SEE_OTHER,
                           TEMPORARY_REDIRECT):
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

        if self.chunked:  # chunked takes precedence over length
            self.parms = odict()
            while True:  # parse all chunks here
                chunkParser = parseChunk(raw=self.msg)
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

        # convert body to data based on content-type, and .dictify flag
        # only gets to here once content length has become finite
        # closed, not chunked/streamed, or chunking/streaming has ended
        if self.jsoned or self.dictify:  # attempt to deserialize json
            try:
                self.data = json.loads(self.body.decode('utf-8'), encoding='utf-8', object_pairs_hook=odict)
            except ValueError as ex:
                self.data = None
            else:  # valid json so clear out body
                del self.body[:]  # self.body.clear() python2 bytearrays don't have clear

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
                 dictify=None,
                 events=None,
                 requests=None,
                 responses=None,
                 redirectable=True,
                 redirects=None,
                 **kwa):
        """
        Initialization method for instance.
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
        dictify = Boolean flag If True attempt to convert body from json
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
            if isinstance(connector, OutgoerTls):
                if scheme and scheme != u'https':
                    raise  ValueError("Provided scheme '{0}' incompatible with connector".format(scheme))
                secured = True
                scheme = u'https'
                defaultPort = 443
            elif isinstance(connector, Outgoer):
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
        hostname, port = normalizeHostPort(host=hostname, port=port, defaultPort=defaultPort)
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
                connector = OutgoerTls(store=self.store,
                                       name=name,
                                       uid=uid,
                                       host=hostname,
                                       port=port,
                                       bufsize=bufsize,
                                       wlog=wlog,
                                       **kwa)
            else:
                connector = Outgoer(store=self.store,
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
        if query:
            if u';' in query:
                querySplits = query.split(u';')
            elif u'&' in query:
                querySplits = query.split(u'&')
            else:
                querySplits = [query]

            for queryPart in querySplits:  # this prevents duplicates even if desired
                if queryPart:
                    if '=' in queryPart:
                        key, val = queryPart.split('=')
                    else:
                        key = queryPart
                        val = True
                    qargs[key] = val

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
                                    dictify=dictify,
                                    events=self.events,
                                    redirectable=redirectable,
                                    redirects=self.redirects,
                                    wlog=wlog,)
        else:
            # do we need to assign the events, redirects, wlog as well?
            respondent.reinit(msg=self.connector.rxbs,
                              method=method,
                              dictify=dictify,
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
            hostname, port = normalizeHostPort(hostname, port=port, defaultPort=defaultPort)
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
                    connector = OutgoerTls(store=self.connector.store,
                                           name=self.connector.name,
                                           uid=self.connector.uid,
                                           ha=(hostname, port),
                                           bufsize=self.connector.bs,
                                           wlog=self.connector.wlog,
                                           context=context)
                else:
                    connector = Outgoer(store=self.connector.store,
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
            if query:
                if u';' in query:
                    querySplits = query.split(u';')
                elif u'&' in query:
                    querySplits = query.split(u'&')
                else:
                    querySplits = [query]
                for queryPart in querySplits:  # this prevents duplicates even if desired
                    if queryPart:
                        if '=' in queryPart:
                            key, val = queryPart.split('=', 1)
                            val = unquote(val)
                        else:
                            key = queryPart
                            val = u'true'
                        qargs[key] = val

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
            self.respondent.parse()

            if self.respondent.ended:
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

    def serviceAllTx(self):
        """
        service the tx side of request
        """
        self.serviceRequests()
        self.connector.serviceTxes()

    def serviceAll(self):
        """
        Service request response
        """
        if self.connector.cutoff and self.connector.reconnectable:
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

        self.serviceAllTx()
        self.serviceResponse()


class Requestant(Parsery):
    """
    Nonblocking HTTP Server Requestant class
    Parses request msg
    """

    def __init__(self, **kwa):
        """
        Initialize Instance

        """
        super(Requestant, self).__init__(**kwa)
        self.path = u''

    def checkPersisted(self):
        """
        Checks headers to determine if connection should be kept open until
        client closes it
        Sets the .persisted flag
        """
        connection = self.headers.get("connection")  # check connection header
        if self.version == 11:  # rules for http v1.1
            self.persisted = True  # connections default to persisted
            connection = self.headers.get("connection")
            if connection and "close" in connection.lower():
                self.persisted = False  # unless connection set to close.

            # non-chunked but persistent connections should have non None for
            # content-length Otherwise assume not persisted
            elif (not self.chunked and self.length is None):
                self.persisted = False

        elif self.version == 10:  # rules for http v1.0
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
        lineParser = parseLine(raw=self.msg, eols=(CRLF, LF), kind="status line")
        while True:  # parse until we get full start line
            line = next(lineParser)
            if line is None:
                (yield None)
                continue
            lineParser.close()  # close generator
            break

        method, path, version = parseRequestLine(line)

        self.method = method
        self.path = path.strip()

        if not version.startswith(u"HTTP/1."):
            raise UnknownProtocol(version)

        if version.startswith(u"HTTP/1.0"):
            self.version = 10
        else:
            self.version = 11  # use HTTP/1.1 code for HTTP/1.x where x>=1

        leaderParser = parseLeader(raw=self.msg,
                                   eols=(CRLF, LF),
                                   kind="leader header line")
        while True:
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
                chunkParser = parseChunk(raw=self.msg)
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
                (yield None)

            self.body = self.msg[:self.length]
            del self.msg[:self.length]

        else:  # unknown content length so parse forever until closed
            while True:
                if self.msg:
                    self.body.extend(self.msg[:])
                    del self.msg[:]  # python2 bytearrays dont have clear self.msg.clear()

                if self.closed:  # no more data so finish
                    break

                (yield None)

        # convert body to data based on content-type, and .dictify flag
        # only gets to here once content length has become finite
        # closed or not chunked or chunking has ended
        if self.jsoned or self.dictify:  # attempt to deserialize json
            try:
                self.data = json.loads(self.body.decode('utf-8'), encoding='utf-8', object_pairs_hook=odict)
            except ValueError as ex:
                self.data = None
            else:  # valid json so clear out body
                del self.body[:]  # self.body.clear() python2 bytearrays don't have clear

        self.bodied = True
        (yield True)
        return


class Valet(object):
    """
    Valet class nonblocking HTTP server connection manager
    """
    def __init__(self,
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
                 **kwa):
        """
        Initialization method for instance.
        servant = instance of Server or ServerTls or None
        responder = instance of Responder or None

        if either of servant, or responder instances are not provided (None)
        some or all of these parameters will be used for initialization

        name = user friendly name for servant
        bufsize = buffer size
        wlog = WireLog instance if any
        ha = host address duple (host, port) for local servant listen socket
        host = host address for local servant listen socket, '' means any interface on host
        port = socket port for local servant listen socket
        eha = external destination address for incoming connections used in TLS
        scheme = http scheme u'http' or u'https' or empty
        requestants = odict of Requestant instances keyed by ca
        responders = odict of Responder instances keyed by ca
        """
        self.store = store or storing.Store(stamp=0.0)
        self.requestants = odict()
        self.responder = odict()

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
        else:
            if secured:
                servant = ServerTls(store=self.store,
                                       name=name,
                                       ha=ha,
                                       eha=eha,
                                       bufsize=bufsize,
                                       wlog=wlog,
                                       **kwa)
            else:
                servant = Server(store=self.store,
                                 name=name,
                                 ha=ha,
                                 eha=eha,
                                 bufsize=bufsize,
                                 wlog=wlog,
                                 **kwa)


        self.secured = secured
        self.servant = servant

    def serviceConnects(self):
        """
        Service new connections
        Create requestants
        Timeout stale connections
        """
        self.servant.serviceConnects()
        for ca, ix in self.servant.ixes.items():
            if ca not in self.requestants:
                requestant = Requestant()


    def serviceRequests(self):
        """
        Service requests deque of incoming requests
        """
        #for
        #requestant.parse()
        #if requestant.ended:
            #requestant.makeParser()  #set up for next time

    def serviceResponses(self):
        """
        Service responses deque of outgoing responses
        """
        pass

    def serviceAllTx(self):
        """
        service the tx side of response
        """
        self.serviceResponses()
        self.servant.serviceTxesAllIx()

    def serviceAllRx(self):
        """
        service the tx side of response
        """
        self.servant.serviceReceivesAllIx()
        #ixClient = server.ixes.values()[0]
        #msgIn = bytes(ixClient.rxbs)
        self.serviceRequests()

    def serviceAll(self):
        """
        Service request response
        """
        self.servant.serviceConnects()
        self.serviceAllRx()
        self.serviceAllTx()

