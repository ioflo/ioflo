"""
tcp async io (nonblocking) module

"""
from __future__ import absolute_import, division, print_function

import sys
import os
import socket
import errno
import platform
from collections import deque
from binascii import hexlify

try:
    import ssl
except ImportError:
    pass

# Import ioflo libs
from ...aid.sixing import *
from ...aid.odicting import odict
from ...aid.timing import StoreTimer
from ...aid.consoling import getConsole
from ...base import storing

console = getConsole()

def initServerContext(context=None,
                      version=None,
                      certify=None,
                      keypath=None,
                      certpath=None,
                      cafilepath=None
                      ):
    """
    Initialize and return context for TLS Server
    IF context is None THEN create a context

    IF version is None THEN create context using ssl library default
    ELSE create context with version

    If certify is not None then use certify value provided Otherwise use default

    context = context object for tls/ssl If None use default
    version = ssl version If None use default
    certify = cert requirement If None use default
              ssl.CERT_NONE = 0
              ssl.CERT_OPTIONAL = 1
              ssl.CERT_REQUIRED = 2
    keypath = pathname of local server side PKI private key file path
              If given apply to context
    certpath = pathname of local server side PKI public cert file path
              If given apply to context
    cafilepath = Cert Authority file path to use to verify client cert
              If given apply to context
    """
    if context is None:  # create context
        if not version:  # use default context
            context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            context.verify_mode = certify if certify is not None else ssl.CERT_REQUIRED

        else:  # create context with specified protocol version
            context = ssl.SSLContext(version)
            # disable bad protocols versions
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            # disable compression to prevent CRIME attacks (OpenSSL 1.0+)
            context.options |= getattr(ssl._ssl, "OP_NO_COMPRESSION", 0)
            # Prefer the server's ciphers by default fro stronger encryption
            context.options |= getattr(ssl._ssl, "OP_CIPHER_SERVER_PREFERENCE", 0)
            # Use single use keys in order to improve forward secrecy
            context.options |= getattr(ssl._ssl, "OP_SINGLE_DH_USE", 0)
            context.options |= getattr(ssl._ssl, "OP_SINGLE_ECDH_USE", 0)
            # disallow ciphers with known vulnerabilities
            context.set_ciphers(ssl._RESTRICTED_SERVER_CIPHERS)
            context.verify_mode = certify if certify is not None else ssl.CERT_REQUIRED

        if cafilepath:
            context.load_verify_locations(cafile=cafilepath,
                                          capath=None,
                                          cadata=None)
        elif context.verify_mode != ssl.CERT_NONE:
            context.load_default_certs(purpose=ssl.Purpose.CLIENT_AUTH)

        if keypath or certpath:
            context.load_cert_chain(certfile=certpath, keyfile=keypath)
    return context


class Incomer(object):
    """
    Manager class for incoming nonblocking TCP connections.
    """
    Timeout = 0.0  # timeout in seconds

    def __init__(self,
                 name=u'',
                 uid=0,
                 ha=None,
                 bs=None,
                 ca=None,
                 cs=None,
                 wlog=None,
                 store=None,
                 timeout=None,
                 refreshable=True):

        """
        Initialization method for instance.
        name = user friendly name for connection
        uid = unique identifier for connection
        ha = host address duple (host, port) near side of connection
        ca = virtual host address duple (host, port) far side of connection
        cs = connection socket object
        wlog = WireLog object if any
        store = data store reference
        timeout = timeout for .timer
        refreshable = True if tx/rx activity refreshes timer False otherwise
        """
        self.name = name
        self.uid = uid
        self.ha = ha
        self.bs = bs
        self.ca = ca
        self.cs = cs
        self.wlog = wlog
        self.cutoff = False # True when detect connection closed on far side
        self.txes = deque()  # deque of data to send
        self.rxbs = bytearray()  # bytearray of data received
        if self.cs:
            self.cs.setblocking(0)  # linux does not preserve blocking from accept
        self.store = store or storing.Store(stamp=0.0)
        self.timeout = timeout if timeout is not None else self.Timeout
        self.timer = StoreTimer(self.store, duration=self.timeout)
        self.refreshable = refreshable

    def shutdown(self, how=socket.SHUT_RDWR):
        """
        Shutdown connected socket .cs
        """
        if self.cs:
            try:
                self.cs.shutdown(how)  # shutdown socket
            except socket.error as ex:
                pass

    def shutdownSend(self):
        """
        Shutdown send on connected socket .cs
        """
        if self.cs:
            try:
                self.shutdown(how=socket.SHUT_WR)  # shutdown socket
            except socket.error as ex:
                pass

    def shutdownReceive(self):
        """
        Shutdown receive on connected socket .cs
        """
        if self.cs:
            try:
                self.shutdown(how=socket.SHUT_RD)  # shutdown socket
            except socket.error as ex:
                pass

    def shutclose(self):
        """
        Shutdown and close connected socket .cs
        """
        if self.cs:
            self.shutdown()
            self.cs.close()  #close socket
            self.cs = None

    close = shutclose  # alias

    def refresh(self):
        """
        Restart timer
        """
        self.timer.restart()

    def receive(self):
        """
        Perform non blocking receive on connected socket .cs

        If no data then returns None
        If connection closed then returns ''
        Otherwise returns data

        data is string in python2 and bytes in python3
        """
        try:
            data = self.cs.recv(self.bs)
        except socket.error as ex:
            # ex.args[0] is always ex.errno for better compat
            if ex.args[0] in (errno.EAGAIN, errno.EWOULDBLOCK):
                return None
            elif ex.args[0] in (errno.ECONNRESET,
                                errno.ENETRESET,
                                errno.ENETUNREACH,
                                errno.EHOSTUNREACH,
                                errno.ENETDOWN,
                                errno.EHOSTDOWN,
                                errno.ETIMEDOUT,
                                errno.ECONNREFUSED):
                emsg = ("socket.error = {0}: Incomer at {1} while receiving "
                        "from {2}\n".format(ex, self.ca, self.ha))
                console.profuse(emsg)
                self.cutoff = True  # this signals need to close/reopen connection
                return bytes()  # data empty
            else:
                emsg = ("socket.error = {0}: Incomer at {1} while receiving"
                        " from {2}\n".format(ex, self.ha, self.ca))
                console.profuse(emsg)
                raise  # re-raise

        if data:  # connection open
            if console._verbosity >= console.Wordage.profuse:  # faster to check
                try:
                    load = data.decode("UTF-8")
                except UnicodeDecodeError as ex:
                    load = "0x{0}".format(hexlify(data).decode("ASCII"))
                cmsg = ("Incomer at {0}, received from {1}:\n------------\n"
                        "{2}\n\n".format(self.ha, self.ca, load))
                console.profuse(cmsg)

            if self.wlog:  # log over the wire rx
                self.wlog.writeRx(self.ca, data)

            if self.refreshable:
                self.refresh()

        else:  # data empty so connection closed on other end
            self.cutoff = True

        return data

    def serviceReceives(self):
        """
        Service receives until no more
        """
        while not self.cutoff:
            data = self.receive()
            if not data:
                break
            self.rxbs.extend(data)

    def serviceReceiveOnce(self):
        '''
        Retrieve from server only one reception
        '''
        if not self.cutoff:
            data = self.receive()
            if data:
                self.rxbs.extend(data)

    def clearRxbs(self):
        """
        Clear .rxbs
        """
        del self.rxbs[:]

    def catRxbs(self):
        """
        Return copy and clear .rxbs
        """
        rx = self.rxbs[:]
        self.clearRxbs()
        return rx

    def tailRxbs(self, index):
        """
        Returns duple of (bytes(self.rxbs[index:]), len(self.rxbs))
        slices the tail from index to end and converts to bytes
        also the length of .rxbs to be used to update index
        """
        return (bytes(self.rxbs[index:]), len(self.rxbs))

    def send(self, data):
        """
        Perform non blocking send on connected socket .cs.
        Return number of bytes sent

        data is string in python2 and bytes in python3
        """
        try:
            result = self.cs.send(data) #result is number of bytes sent
        except socket.error as ex:
            # ex.args[0] is always ex.errno for better compat
            if ex.args[0] in (errno.EAGAIN, errno.EWOULDBLOCK):
                result = 0  # blocked try again
            elif ex.args[0] in (errno.ECONNRESET,
                                errno.ENETRESET,
                                errno.ENETUNREACH,
                                errno.EHOSTUNREACH,
                                errno.ENETDOWN,
                                errno.EHOSTDOWN,
                                errno.ETIMEDOUT,
                                errno.ECONNREFUSED):
                emsg = ("socket.error = {0}: Outgoer at {1} while sending "
                        "to {2} \n".format(ex, self.ca, self.ha))
                console.profuse(emsg)
                self.cutoff = True  # this signals need to close/reopen connection
                result = 0
            else:
                emsg = ("socket.error = {0}: Incomer at {1} while "
                        "sending to {2}\n".format(ex, self.ha, self.ca))
                console.profuse(emsg)
                raise

        if result:
            if console._verbosity >=  console.Wordage.profuse:
                try:
                    load = data[:result].decode("UTF-8")
                except UnicodeDecodeError as ex:
                    load = "0x{0}".format(hexlify(data[:result]).decode("ASCII"))
                cmsg = ("Incomer at {0}, sent {1} bytes to {2}:\n------------\n"
                        "{3}\n\n".format(self.ha, result, self.ca, load))
                console.profuse(cmsg)

            if self.wlog:
                self.wlog.writeTx(self.ca, data[:result])

            if self.refreshable:
                self.refresh()

        return result

    def tx(self, data):
        '''
        Queue data onto .txes
        '''
        self.txes.append(data)

    def serviceTxes(self):
        """
        Service transmits
        For each tx if all bytes sent then keep sending until partial send
        or no more to send
        If partial send reattach and return
        """
        while self.txes and not self.cutoff:
            data = self.txes.popleft()
            count = self.send(data)
            if count < len(data):  # put back unsent portion
                self.txes.appendleft(data[count:])
                break  # try again later


class IncomerTls(Incomer):
    """
    Incomer with Nonblocking TLS/SSL support
    Manager class for incoming nonblocking TCP connections.
    """
    def __init__(self,
                 context=None,
                 version=None,
                 certify=None,
                 keypath=None,
                 certpath=None,
                 cafilepath=None,
                 **kwa):

        """
        Initialization method for instance.
        context = context object for tls/ssl If None use default
        version = ssl version If None use default
        certify = cert requirement If None use default
                  ssl.CERT_NONE = 0
                  ssl.CERT_OPTIONAL = 1
                  ssl.CERT_REQUIRED = 2
        keypath = pathname of local server side PKI private key file path
                  If given apply to context
        certpath = pathname of local server side PKI public cert file path
                  If given apply to context
        cafilepath = Cert Authority file path to use to verify client cert
                  If given apply to context
        """
        super(IncomerTls, self).__init__(**kwa)

        self.connected = False  # True once ssl handshake completed

        self.context = initServerContext(context=context,
                                    version=version,
                                    certify=certify,
                                    keypath=keypath,
                                    certpath=certpath,
                                    cafilepath=cafilepath
                                  )
        self.wrap()

    def shutclose(self):
        """
        Shutdown and close connected socket .cs
        """
        if self.cs:
            self.shutdown()
            self.cs.close()  #close socket
            self.cs = None
            self.connected = False

    close = shutclose  # alias

    def wrap(self):
        """
        Wrap socket .cs in ssl context
        """
        self.cs = self.context.wrap_socket(self.cs,
                                           server_side=True,
                                           do_handshake_on_connect=False)

    def handshake(self):
        """
        Attempt nonblocking ssl handshake to .ha
        Returns True if successful
        Returns False if not so try again later
        """
        try:
            self.cs.do_handshake()
        except ssl.SSLError as ex:
            if ex.errno in (ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE):
                return False
            elif ex.errno in (ssl.SSL_ERROR_EOF, ):
                self.shutclose()
                raise   # should give up here nicely
            else:
                self.shutclose()
                raise
        except OSError as ex:
            self.shutclose()
            if ex.errno in (errno.ECONNABORTED, ):
                raise  # should give up here nicely
            raise
        except Exception as ex:
            self.shutclose()
            raise

        self.connected = True
        return True

    def serviceHandshake(self):
        """
        Service connection and handshake attempt
        If not already accepted and handshaked  Then
             make nonblocking attempt
        Returns .handshaked
        """
        if not self.connected:
            self.handshake()

        return self.connected

    def receive(self):
        """
        Perform non blocking receive on connected socket .cs

        If no data then returns None
        If connection closed then returns ''
        Otherwise returns data

        data is string in python2 and bytes in python3
        """
        try:
            data = self.cs.recv(self.bs)
        except socket.error as ex:  # ssl.SSLError is a subtype of socket.error
            # ex.args[0] is always ex.errno for better compat
            if  ex.args[0] in (ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE):
                return None  # blocked waiting for data
            elif ex.args[0] in (errno.ECONNRESET,
                                errno.ENETRESET,
                                errno.ENETUNREACH,
                                errno.EHOSTUNREACH,
                                errno.ENETDOWN,
                                errno.EHOSTDOWN,
                                errno.ETIMEDOUT,
                                errno.ECONNREFUSED,
                                ssl.SSLEOFError):
                emsg = ("socket.error = {0}: IncomerTLS at {1} while receiving"
                        " from {2}\n".format(ex, self.ha, self.ca))
                console.profuse(emsg)
                self.cutoff = True  # this signals need to close/reopen connection
                return bytes()  # data empty
            else:
                emsg = ("socket.error = {0}: IncomerTLS at {1} while receiving"
                        " from {2}\n".format(ex, self.ha, self.ca))
                console.profuse(emsg)
                raise  # re-raise

        if data:  # connection open
            if console._verbosity >= console.Wordage.profuse:  # faster to check
                try:
                    load = data.decode("UTF-8")
                except UnicodeDecodeError as ex:
                    load = "0x{0}".format(hexlify(data).decode("ASCII"))
                cmsg = ("Incomer at {0}, received from {1}:\n------------\n"
                        "{2}\n\n".format(self.ha, self.ca, load))
                console.profuse(cmsg)

            if self.wlog:  # log over the wire rx
                self.wlog.writeRx(self.ca, data)

        else:  # data empty so connection closed on other end
            self.cutoff = True

        return data

    def send(self, data):
        """
        Perform non blocking send on connected socket .cs.
        Return number of bytes sent

        data is string in python2 and bytes in python3
        """
        try:
            result = self.cs.send(data) #result is number of bytes sent
        except socket.error as ex:  # ssl.SSLError is a subtype of socket.error
            # ex.args[0] is always ex.errno for better compat
            if ex.args[0] in (ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE):
                result = 0  # blocked try again
            elif ex.args[0] in (errno.ECONNRESET,
                                errno.ENETRESET,
                                errno.ENETUNREACH,
                                errno.EHOSTUNREACH,
                                errno.ENETDOWN,
                                errno.EHOSTDOWN,
                                errno.ETIMEDOUT,
                                errno.ECONNREFUSED,
                                ssl.SSLEOFError):
                emsg = ("socket.error = {0}: IncomerTLS at {1} while "
                        "sending to {2}\n".format(ex, self.ha, self.ca))
                console.profuse(emsg)
                self.cutoff = True  # this signals need to close/reopen connection
                result = 0
            else:
                emsg = ("socket.error = {0}: IncomerTLS at {1} while "
                        "sending to {2}\n".format(ex, self.ha, self.ca))
                console.profuse(emsg)
                raise

        if result:
            if console._verbosity >=  console.Wordage.profuse:
                try:
                    load = data[:result].decode("UTF-8")
                except UnicodeDecodeError as ex:
                    load = "0x{0}".format(hexlify(data[:result]).decode("ASCII"))
                cmsg = ("Incomer at {0}, sent {1} bytes to {2}:\n------------\n"
                        "{3}\n\n".format(self.ha, result, self.ca, load))
                console.profuse(cmsg)

            if self.wlog:
                self.wlog.writeTx(self.ca, data[:result])

        return result


class Acceptor(object):
    """
    Nonblocking TCP Socket Acceptor Class.
    Listen socket for incoming TCP connections
    """

    def __init__(self,
                 name=u'',
                 ha=None,
                 host=u'',
                 port=56000,
                 eha=None,
                 bufsize=8096,
                 wlog=None):
        """
        Initialization method for instance.
        name = user friendly name string for Acceptor
        ha = host address duple (host, port) for listen socket
        host = host address for listen socket, '' means any interface on host
        port = socket port for listen socket
        eha = external destination address for incoming connections used in tls
        bufsize = buffer size
        wlog = WireLog object if any
        """
        self.name = name
        self.ha = ha or (host, port)  # ha = host address
        eha = eha or self.ha
        if eha:
            host, port = eha
            host = socket.gethostbyname(host)
            if host in ['0.0.0.0', '']:
                host = '127.0.0.1'
            eha = (host, port)
        self.eha = eha
        self.bs = bufsize
        self.wlog = wlog

        self.ss = None  # listen socket for accepts
        self.axes = deque()  # deque of duple (ca, cs) accepted connections
        self.opened = False

    def actualBufSizes(self):
        """
        Returns duple of the the actual socket send and receive buffer size
        (send, receive)
        """
        if not self.ss:
            return (0, 0)

        return (self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF),
                self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))

    def open(self):
        """
        Opens binds listen socket in non blocking mode.

        if socket not closed properly, binding socket gets error
           socket.error: (48, 'Address already in use')
        """
        #create server socket ss to listen on
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # make socket address reusable.
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in
        # TIME_WAIT state, without waiting for its natural timeout to expire.
        self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Linux TCP allocates twice the requested size
        if sys.platform.startswith('linux'):
            bs = 2 * self.bs  # get size is twice the set size
        else:
            bs = self.bs

        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) < bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bs)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bs)

        self.ss.setblocking(0) #non blocking socket

        try:  # bind to listen socket (host, port) to receive connections
            self.ss.bind(self.ha)
            self.ss.listen(5)
        except socket.error as ex:
            console.terse("socket.error = {0}\n".format(ex))
            return False

        self.ha = self.ss.getsockname()  # get resolved ha after bind
        self.opened = True
        return True

    def reopen(self):
        """
        Idempotently opens listen socket
        """
        self.close()
        return self.open()

    def close(self):
        """
        Closes listen socket.
        """
        if self.ss:
            try:
                self.ss.shutdown(socket.SHUT_RDWR)  # shutdown socket
            except socket.error as ex:
                #console.terse("socket.error = {0}\n".format(ex))
                pass
            self.ss.close()  #close socket
            self.ss = None
            self.opened = False

    def accept(self):
        """
        Accept new connection nonblocking
        Returns duple (cs, ca) of connected socket and connected host address
        Otherwise if no new connection returns (None, None)
        """
        # accept new virtual connected socket created from server socket
        try:
            cs, ca = self.ss.accept()  # virtual connection (socket, host address)
        except socket.error as ex:
            if ex.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return (None, None)  # nothing yet
            emsg = ("socket.error = {0}: server at {1} while "
                    "accepting \n".format(ex, self.ha))
            console.profuse(emsg)
            raise  # re-raise

        return (cs, ca)

    def serviceAccepts(self):
        """
        Service any accept requests
        Adds to .cxes odict key by ca
        """
        while True:
            cs, ca = self.accept()
            if not cs:
                break
            self.axes.append((cs, ca))


class Server(Acceptor):
    """
    Nonblocking TCP Socket Server Class.
    Listen socket for incoming TCP connections
    Incomer sockets for accepted connections
    """
    Timeout = 1.0  # timeout in seconds

    def __init__(self,
                 store=None,
                 timeout=None,
                 **kwa):
        """
        Initialization method for instance.

        store = data store reference if any
        timeout = default timeout for incoming connections
        """
        super(Server, self).__init__(**kwa)
        self.store = store or storing.Store(stamp=0.0)
        self.timeout = timeout if timeout is not None else self.Timeout

        self.ixes = odict()  # ready to rx tx incoming connections, Incomer instances

    def serviceAxes(self):
        """
        Service axes

        For each newly accepted connection in .axes create Incomer
        and add to .ixes keyed by ca
        """
        self.serviceAccepts()  # populate .axes
        while self.axes:
            cs, ca = self.axes.popleft()
            if ca != cs.getpeername() or self.eha != cs.getsockname():
                raise ValueError("Accepted socket host addresses malformed for "
                                 "peer ha {0} != {1}, ca {2} != {3}\n".format(
                                     self.ha, cs.getsockname(), ca, cs.getpeername()))
            incomer = Incomer(ha=cs.getsockname(),
                              bs=self.bs,
                              ca=cs.getpeername(),
                              cs=cs,
                              wlog=self.wlog,
                              store=self.store,
                              timeout=self.timeout)
            if ca in self.ixes and self.ixes[ca] is not incomer:
                self.shutdownIx[ca]
            self.ixes[ca] = incomer

    def serviceConnects(self):
        """
        Service connects is method name to be used
        """
        self.serviceAxes()

    def shutdownIx(self, ca, how=socket.SHUT_RDWR):
        """
        Shutdown incomer given by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        self.ixes[ca].shutdown(how=how)

    def shutdownSendIx(self, ca):
        """
        Shutdown send on incomer given by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        self.ixes[ca].shutdownSend()

    def shutdownReceiveIx(self, ca):
        """
        Shutdown send on incomer given by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        self.ixes[ca].shutdownReceive()

    def closeIx(self, ca):
        """
        Shutdown and close incomer given by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        self.ixes[ca].close()

    def closeAllIx(self):
        """
        Shutdown and close all incomer connections
        """
        for ix in self.ixes.values():
            ix.close()

    def closeAll(self):
        """
        Close all sockets
        """
        self.close()
        self.closeAllIx()

    def removeIx(self, ca, shutclose=True):
        """
        Remove incomer given by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        if shutclose:
            self.ixes[ca].shutclose()
        del self.ixes[ca]

    def catRxbsIx(self, ca):
        """
        Return  copy and clear rxbs for incomer given by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        return (self.ixes[ca].catRxbs())

    def serviceReceivesIx(self, ca):
        """
        Service receives for incomer by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        self.ixes[ca].serviceReceives()

    def serviceReceivesAllIx(self):
        """
        Service receives for all incomers in .ixes
        """
        for ix in self.ixes.values():
            ix.serviceReceives()

    def transmitIx(self, data, ca):
        '''
        Queue data onto .txes for incomer given by connection address ca
        '''
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        self.ixes[ca].tx(data)

    def serviceTxesAllIx(self):
        """
        Service transmits for all incomers in .ixes
        """
        for ix in self.ixes.values():
            ix.serviceTxes()

    def serviceAll(self):
        """
        Service connects and service receives and txes for all ix.
        """
        self.serviceConnects()
        self.serviceReceivesAllIx()
        self.serviceTxesAllIx()


class ServerTls(Server):
    """
    Server with Nonblocking TLS/SSL support
    Nonblocking TCP Socket Server Class.
    Listen socket for incoming TCP connections
    IncomerTLS sockets for accepted connections
    """
    def __init__(self,
                 context=None,
                 version=None,
                 certify=None,
                 keypath=None,
                 certpath=None,
                 cafilepath=None,
                 **kwa):
        """
        Initialization method for instance.
        """
        super(ServerTls, self).__init__(**kwa)

        self.cxes = odict()  # accepted incoming connections, IncomerTLS instances

        self.context = context
        self.version = version
        self.certify = certify
        self.keypath = keypath
        self.certpath = certpath
        self.cafilepath = cafilepath

        self.context = initServerContext(context=context,
                                         version=version,
                                         certify=certify,
                                         keypath=keypath,
                                         certpath=certpath,
                                         cafilepath=cafilepath
                                        )

    def serviceAxes(self):
        """
        Service accepteds

        For each new accepted connection create IncomerTLS and add to .cxes
        Not Handshaked
        """
        self.serviceAccepts()  # populate .axes
        while self.axes:
            cs, ca = self.axes.popleft()
            if ca != cs.getpeername() or self.eha != cs.getsockname():
                raise ValueError("Accepted socket host addresses malformed for "
                                 "peer ha {0} != {1}, ca {2} != {3}\n".format(
                                     self.ha, cs.getsockname(), ca, cs.getpeername()))
            incomer = IncomerTls(ha=cs.getsockname(),
                                 bs=self.bs,
                                 ca=cs.getpeername(),
                                 cs=cs,
                                 wlog=self.wlog,
                                 store=self.store,
                                 timeout=self.timeout,
                                 context=self.context,
                                 version=self.version,
                                 certify=self.certify,
                                 keypath=self.keypath,
                                 certpath=self.certpath,
                                 cafilepath=self.cafilepath,
                                )

            self.cxes[ca] = incomer

    def serviceCxes(self):
        """
        Service handshakes for every incomer in .cxes
        If successful move to .ixes
        """
        for ca, cx in self.cxes.items():
            if cx.serviceHandshake():
                self.ixes[ca] = cx
                del self.cxes[ca]

    def serviceConnects(self):
        """
        Service accept and handshake attempts
        If not already accepted and handshaked  Then
             make nonblocking attempt
        For each successful handshaked add to .ixes
        Returns handshakeds
        """
        self.serviceAxes()
        self.serviceCxes()


class Peer(Server):
    """
    Nonblocking TCP Socket Peer Class.
    Supports both incoming and outgoing connections.
    """
    def __init__(self, **kwa):
        """
        Initialization method for instance.
        """
        super(Peer, self).init(**kwa)

        self.oxes = odict()  # outgoers indexed by ha




