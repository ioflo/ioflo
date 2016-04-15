"""
httping.py  http async io (nonblocking) support


"""
from __future__ import absolute_import, division, print_function


import sys
import os
from collections import deque
import codecs
import json

if sys.version > '3':
    from urllib.parse import urlsplit, quote, quote_plus, unquote, unquote_plus
else:
    from urlparse import urlsplit
    from urllib import quote, quote_plus, unquote, unquote_plus

try:
    import simplejson as json
except ImportError:
    import json

# Import ioflo libs
from ...aid.sixing import *
from ...aid.odicting import odict, lodict, modict
from ...aid import aiding
from ...aid.consoling import getConsole

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
STATUS_DESCRIPTIONS = {
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

class BadRequestLine(BadStatusLine):
    pass

class BadMethod(HTTPException):
    def __init__(self, method):
        self.args = method,
        self.method = method

class LineTooLong(HTTPException):
    def __init__(self, kind):
        HTTPException.__init__(self, "got more than %d bytes while parsing %s"
                                     % (MAX_LINE_SIZE, kind))

class PrematureClosure(HTTPException):
    def __init__(self, msg):
        self.args = msg,
        self.msg = msg

# Utility functions

def httpDate1123(dt):
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.
    import datetime
    httpDate1123(datetime.datetime.utcnow())
    'Wed, 30 Sep 2015 14:29:18 GMT'
    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)

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

def updateQargsQuery(qargs=None, query=u'',):
    """
    Returns duple of updated (qargs, query)
    Where qargs parameter is odict of query arguments and query parameter is query string
    The returned qargs is updated with query string arguments
    and the returned query string is generated from the updated qargs
    If provided, qargs may have additional fields not in query string
    This allows combining query args from two sources, a dict and a string
    """
    if qargs == None:
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

    qargParts = [u"{0}={1}".format(key, quote_plus(str(val)))
                                   for key, val in qargs.items()]
    query = '&'.join(qargParts)
    return (qargs, query)

def unquoteQuery(query):
    """
    Returns query string with unquoted values
    """
    sep = u'&'
    parts = []
    if u';' in query:
        splits = query.split(u';')
        sep = u';'
    elif u'&' in query:
        splits = query.split(u'&')
    else:
        splits = [query]
    for part in splits:  # this prevents duplicates even if desired
        if part:
            if '=' in part:
                key, val = part.split('=', 1)
                val = unquote(val)
                parts.append(u"{0}={1}".format(key, str(val)))
            else:
                key = part
                parts.append[part]
    query = '&'.join(parts)
    return query


def packHeader(name, *values):
    """
    Format and return a header line.

    For example: h.packHeader('Accept', 'text/html')
    """
    if isinstance(name, unicode):  # not bytes
        name = name.encode('ascii')
    name = name.title()  # make title case
    values = list(values)  # make copy
    for i, value in enumerate(values):
        if isinstance(value, unicode):
            values[i] = value.encode('iso-8859-1')
        elif isinstance(value, int):
            values[i] = str(value).encode('ascii')
    value = b', '.join(values)
    return (name + b': ' + value)

def packChunk(msg):
    """
    Return msg bytes in a chunk
    """
    lines = []
    size = len(msg)
    lines.append(u"{0:x}\r\n".format(size).encode('ascii'))  # convert to bytes
    lines.append(msg)
    lines.append(b'\r\n')
    return (b''.join(lines))

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
        raise BadRequestLine(line)  # connection closed before sending valid msg

    method, path, version, extra = aiding.repack(4, line.split(), default = u'')

    if not version.startswith("HTTP/"):
        raise UnknownProtocol(version)

    if method not in METHODS:
        raise BadMethod(method)

    return (method, path, version)



class EventSource(object):
    """
    Server Sent Event Stream Client parser
    """
    Bom = codecs.BOM_UTF8 # utf-8 encoded bom b'\xef\xbb\xbf'

    def __init__(self, raw=None, events=None, dictable=False):
        """
        Initialize Instance
        raw must be bytearray
        IF events is not None then used passed in deque
            .events will be deque of event odicts
        IF dictable then deserialize event data as json

        """
        self.raw = raw if raw is not None else bytearray()
        self.events = events if events is not None else deque()
        self.dictable = True if dictable else False

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
                    if self.dictable:
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


class Parsent(object):
    """
    Base class for objects that parse HTTP messages
    """
    def __init__(self,
                 msg=None,
                 dictable=None,
                 method=u'GET'):
        """
        Initialize Instance
        msg = bytearray of request msg to parse
        dictable = True If should attempt to convert body to json
        method = method of associated request
        """
        self.msg = msg if msg is not None else bytearray()
        self.dictable = True if dictable else False  # convert body json
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
        self.errored = False  # True when error occurs in response processing
        self.error = None  # Error Description String

        self.headers = None
        self.parms = None  # chunked encoding extension parameters
        self.trails = None  # chunked encoding trailing headers
        self.body = bytearray()  # body data bytearray
        self.text = u''  # body decoded as unicode string
        self.data = None  # content dict deserialized from body json
        self.method = method.upper() if method else u'GET'

        self.makeParser()  # assigns self.msg

    def reinit(self,
               msg=None,
               dictable=None,
               method=u'GET'):
        """
        Reinitialize Instance
        msg = bytearray of request msg to parse
        dictable = Boolean flag If True attempt to convert json body
        method = method verb of associated request
        """
        if msg is not None:
            self.msg = msg
        if dictable is not None:
            self.dictable = True if dictable else False
        if method is not None:
            self.method = method.upper()

    def close(self):
        """
        Assign True to .closed and close parser
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
        self.length = 0
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
        self.errored = False
        self.error = None
        try:
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
        except HTTPException as ex:
            self.errored = True
            self.error = str(ex)

        self.ended = True
        (yield True)
        return

    def makeParser(self, msg=None):
        """
        Make message parser generator and assign to .parser
        Assign msg to .msg If provided
        """
        if msg is not None:
            self.msg = msg
        if self.parser:
            self.parser.close()
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

    def dictify(self):
        """
        Attempt to convert body to dict data if .dictable or json content-type
        """
        # convert body to data based on content-type, and .dictable flag

        if self.jsoned or self.dictable:  # attempt to deserialize json
            try:
                self.data = json.loads(self.body.decode('utf-8'),
                                       encoding='utf-8',
                                       object_pairs_hook=odict)
            except ValueError as ex:
                self.data = None
            else:  # valid json so clear out body
                del self.body[:]  # self.body.clear() python2 bytearrays don't have clear



