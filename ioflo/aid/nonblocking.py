"""
nonblocking.py

"""
#print("module {0}".format(__name__))

from __future__ import division

import sys
import os
import socket
import time
import errno
import io
from collections import deque

try:
    import win32file
except ImportError:
    pass

# Import ioflo libs
from ..base.globaling import *
from ..base.odicting import odict
from ..base import excepting
from ..base import storing
from ..base.aiding import StoreTimer


from ..base.consoling import getConsole
console = getConsole()


class SerialNb(object):
    """
    Class to manage non blocking io on serial port.

    Opens non blocking read file descriptor on serial port
    Use instance method close to close file descriptor
    Use instance methods get & put to read & write to serial device
    Needs os module
    """

    def __init__(self):
        """Initialization method for instance.

        """
        self.fd = None #serial port device file descriptor, must be opened first

    def open(self, device = '', speed = None, canonical = True):
        """
        Opens fd on serial port in non blocking mode.

        device is the serial device path name or
        if '' then use os.ctermid() which
        returns path name of console usually '/dev/tty'

        canonical sets the mode for the port. Canonical means no characters
        available until a newline

        os.O_NONBLOCK makes non blocking io
        os.O_RDWR allows both read and write.
        os.O_NOCTTY don't make this the controlling terminal of the process
        O_NOCTTY is only for cross platform portability BSD never makes it the
        controlling terminal

        Don't use print at same time since it will mess up non blocking reads.

        Default is canonical mode so no characters available until newline
        need to add code to enable  non canonical mode

        It appears that canonical mode is default only applies to the console.
        For other serial devices the characters are available immediately so
        have to explicitly set termios to canonical mode.
        """
        if not device:
            device = os.ctermid() #default to console

        self.fd = os.open(device,os.O_NONBLOCK | os.O_RDWR | os.O_NOCTTY)

        system = platform.system()

        if (system == 'Darwin') or (system == 'Linux'): #use termios to set values

            iflag, oflag, cflag, lflag, ispeed, ospeed, cc = range(7)

            settings = termios.tcgetattr(self.fd)
            #print(settings)

            #ignore carriage returns on input
            settings[iflag] = (settings[iflag] | (termios.IGNCR)) #ignore cr

            settings[lflag] = (settings[lflag] & ~(termios.ECHO)) #no echo

                #8N1 8bit word no parity one stop bit nohardware handshake ctsrts
            #to set size have to mask out(clear) CSIZE bits and or in size
            settings[cflag] = ((settings[cflag] & ~termios.CSIZE) | termios.CS8)
            # no parity clear PARENB
            settings[cflag] = (settings[cflag] & ~termios.PARENB)
            #one stop bit clear CSTOPB
            settings[cflag] = (settings[cflag] & ~termios.CSTOPB)
            #no hardware handshake clear crtscts
            settings[cflag] = (settings[cflag] & ~termios.CRTSCTS)

            if canonical:
                settings[lflag] = (settings[lflag] | termios.ICANON)
            else:
                settings[lflag] = (settings[lflag] &  ~(termios.ICANON))

            if speed: #in linux the speed flag does not equal value
                speedattr = "B{0}".format(speed) #convert numeric speed to attribute name string
                speed = getattr(termios, speedattr)
                settings[ispeed] = speed
                settings[ospeed] = speed

            termios.tcsetattr(self.fd, termios.TCSANOW, settings)
            #print(settings)

    def close(self):
        """Closes fd.

        """
        if self.fd:
            os.close(self.fd)

    def get(self,bs = 80):
        """Gets nonblocking characters from serial device up to bs characters
           including newline.

           Returns empty string if no characters available else returns all available.
           In canonical mode no chars are available until newline is entered.
        """
        line = ''
        try:
            line = os.read(self.fd, bs)  #if no chars available generates exception
        except OSError as ex1:  #ex1 is the target instance of the exception
            if ex1.errno == errno.EAGAIN: #BSD 35, Linux 11
                pass #No characters available
            else:
                raise #re raise exception ex1

        return line

    def put(self, data = '\n'):
        """Writes data string to serial device.

        """
        os.write(self.fd, data)

class ConsoleNb(object):
    """
    Class to manage non blocking io on console.

    Opens non blocking read file descriptor on console
    Use instance method close to close file descriptor
    Use instance methods getline & put to read & write to console
    Needs os module
    """

    def __init__(self):
        """Initialization method for instance.

        """
        self.fd = None #console file descriptor needs to be opened

    def open(self, port='', canonical=True):
        """
        Opens fd on terminal console in non blocking mode.

        port is the serial port or if '' then use os.ctermid() which
        returns path name of console usually '/dev/tty'

        canonical sets the mode for the port. Canonical means no characters
        available until a newline

        os.O_NONBLOCK makes non blocking io
        os.O_RDWR allows both read and write.
        os.O_NOCTTY don't make this the controlling terminal of the process
        O_NOCTTY is only for cross platform portability BSD never makes it the
        controlling terminal

        Don't use print at same time since it will mess up non blocking reads.

        Default is canonical mode so no characters available until newline
        need to add code to enable  non canonical mode

        It appears that canonical mode only applies to the console. For other
        serial ports the characters are available immediately
        """
        if not port:
            port = os.ctermid() #default to console

        try:
            self.fd = os.open(port, os.O_NONBLOCK | os.O_RDWR | os.O_NOCTTY)
        except OSError as ex:
            console.terse("os.error = {0}\n".format(ex))
            return False
        return True

    def close(self):
        """Closes fd.

        """
        if self.fd:
            os.close(self.fd)
            self.fd = None

    def getLine(self,bs = 80):
        """Gets nonblocking line from console up to bs characters including newline.

           Returns empty string if no characters available else returns line.
           In canonical mode no chars available until newline is entered.
        """
        line = ''
        try:
            line = os.read(self.fd, bs)
        except OSError as ex1:  #if no chars available generates exception
            try: #need to catch correct exception
                errno = ex1.args[0] #if args not sequence get TypeError
                if errno == 35:
                    pass #No characters available
                else:
                    raise #re raise exception ex1
            except TypeError as ex2:  #catch args[0] mismatch above
                raise ex1 #ignore TypeError, re-raise exception ex1

        return line

    def put(self, data = '\n'):
        """Writes data string to console.

        """
        return(os.write(self.fd, data))

class WireLog(object):
    """
    Provides log files for logging 'over the wire' network tx and rx
    for non blocking transports for debugging purposes
    in addition to the standard console logging capability
    """
    def __init__(self,
                 path='',
                 prefix='',
                 midfix='',
                 rx=True,
                 tx=True,
                 same=False,
                 buffify=False):
        """
        Initialization method for instance.
        path = directory for log files
        prefix = prefix to include in log name if provided
        midfix = another more prefix for log name if provided
        rx = Boolean create rx log file if True
        tx = Boolean create tx log file if True
        same = Boolean use same log file for both rx and tx
        buffify = Boolean use BytesIO in memory buffer instead of File object
        """
        self.path = path  # path to directory where log files go must end in /
        self.prefix = prefix
        self.midfix = midfix
        self.rx = True if rx else False
        self.tx = True if tx else False
        self.same = True if same else False
        self.rxLog = None  # receive log file
        self.txLog = None  # transmit log file
        self.buffify = True if buffify else False

    def reopen(self, path='', prefix='', midfix=''):
        """
        Close and then open log files on path if given otherwise self.path
        Use ha in log file name if given
        """
        self.close()

        if path:
            self.path = path

        if prefix:
            self.prefix = prefix

        if midfix:
            self.midfix = midfix

        prefix = "{0}_".format(self.prefix) if self.prefix else ""
        midfix = "{0}_".format(self.midfix) if self.midfix else ""

        date = time.strftime('%Y%m%d_%H%M%S', time.gmtime(time.time()))

        if self.same and (self.rx or self.tx):
            if not self.buffify:
                name = "{0}{1}{2}.txt".format(prefix, midfix, date)
                path = os.path.join(self.path, name)
                try:
                    log = io.open(path, mode='wb+')
                    if self.rx:
                        self.rxLog = log
                    if self.tx:
                        self.txLog = log
                except IOError:
                    self.rxLog = self.txLog = None
                    return False
            else:
                try:
                    log = io.BytesIO()
                    if self.rx:
                        self.rxLog = log
                    if self.tx:
                        self.txLog = log
                except IOError:
                    self.rxLog = self.txLog = None
                    return False

        else:
            if self.rx:
                if not self.buffify:
                    name = "{0}{1}{2}_rx.txt".format(prefix, midfix, date)
                    path = os.path.join(self.path, name)
                    try:
                        self.rxLog = io.open(path, mode='wb+')
                    except IOError:
                        self.rxLog = None
                        return False
                else:
                    try:
                        self.rxLog = io.BytesIO()
                    except IOError:
                        self.rxLog = None
                        return False

            if self.tx:
                if not self.buffify:
                    name = "{0}{1}{2}_tx.txt".format(prefix, midfix, date)
                    path = os.path.join(self.path, name)
                    try:
                        self.txLog = io.open(path, mode='wb+')
                    except IOError:
                        self.txLog = None
                        return False
                else:
                    try:
                        self.txLog = io.BytesIO()
                    except IOError:
                        self.txLog = None
                        return False

        return True

    def close(self):
        """
        Close log files
        """
        if self.txLog and not self.txLog.closed:
            self.txLog.close()
        if self.rxLog and not self.rxLog.closed:
            self.rxLog.close()

    def getRx(self):
        """
        Returns rx string buffer value if .buffify else None
        """
        if self.buffify and self.rxLog and not self.rxLog.closed:
            return (self.rxLog.getvalue())
        return None

    def getTx(self):
        """
        Returns tx string buffer value if .buffify else None
        """
        if self.buffify and self.txLog and not self.txLog.closed:
            return (self.txLog.getvalue())
        return None

    def writeRx(self, sa, data):
        """
        Write bytes data received from source address sa,
        """
        if self.rx and self.rxLog:
            self.rxLog.write(ns2b("RX {0}\n".format(sa)))
            self.rxLog.write(data)
            self.rxLog.write(b'\n')

    def writeTx(self, da, data):
        """
        Write bytes data transmitted to destination address da,
        """
        if self.tx and self.txLog:
            self.txLog.write(ns2b("TX {0}\n".format(da)))
            self.txLog.write(data)
            self.txLog.write(b'\n')


class SocketUdpNb(object):
    """
    Class to manage non blocking I/O on UDP socket.
    """

    def __init__(self,
                 ha=None,
                 host = '',
                 port = 55000,
                 bufsize = 1024,
                 wlog=None):
        """
        Initialization method for instance.

        ha = host address duple (host, port)
        host = '' equivalant to any interface on host
        port = socket port
        bs = buffer size
        path = path to log file directory
        wlog = WireLog reference for debug logging or over the wire tx and rx
        """
        self.ha = ha or (host,port) #ha = host address
        self.bs = bufsize
        self.wlog = wlog

        self.ss = None #server's socket needs to be opened

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
        Opens socket in non blocking mode.

        if socket not closed properly, binding socket gets error
           socket.error: (48, 'Address already in use')
        """
        #create socket ss = server socket
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # make socket address reusable. doesn't seem to have an effect.
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in
        # TIME_WAIT state, without waiting for its natural timeout to expire.
        self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) <  self.bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bs)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < self.bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bs)
        self.ss.setblocking(0) #non blocking socket

        #bind to Host Address Port
        try:
            self.ss.bind(self.ha)
        except socket.error as ex:
            console.terse("socket.error = {0}\n".format(ex))
            return False

        self.ha = self.ss.getsockname() #get resolved ha after bind

        return True

    def reopen(self):
        """
        Idempotently open socket
        """
        self.close()
        return self.open()

    def close(self):
        """
        Closes  socket and logs if any
        """
        if self.ss:
            self.ss.close() #close socket
            self.ss = None

    def receive(self):
        """
        Perform non blocking read on  socket.

        returns tuple of form (data, sa)
        if no data then returns (b'',None)
        but always returns a tuple with two elements
        """
        try:
            #sa = source address tuple (sourcehost, sourceport)
            data, sa = self.ss.recvfrom(self.bs)
        except socket.error as ex:
            if ex.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return (b'', None) #receive has nothing empty string for data
            else:
                emsg = "socket.error = {0}: receiving at {1}\n".format(ex, self.ha)
                console.profuse(emsg)
                raise #re raise exception ex1

        if console._verbosity >= console.Wordage.profuse:  # faster to check
            cmsg = ("\nServer at {0}, received from {1}:\n------------\n"
                       "{2}\n".format(self.ha, sa, data.decode("UTF-8")))
            console.profuse(cmsg)

        if self.wlog:  # log over the wire rx
            self.wlog.writeRx(sa, data)

        return (data, sa)

    def send(self, data, da):
        """
        Perform non blocking send on  socket.

        data is string in python2 and bytes in python3
        da is destination address tuple (destHost, destPort)
        """
        try:
            result = self.ss.sendto(data, da) #result is number of bytes sent
        except socket.error as ex:
            emsg = "socket.error = {0}: sending from {1} to {2}\n".format(ex, self.ha, da)
            console.profuse(emsg)
            result = 0
            raise

        if console._verbosity >=  console.Wordage.profuse:
            cmsg = ("\nServer at {0}, sent {1} bytes to {2}:\n------------\n"
                    "{3}\n".format(self.ha, result, da, data[:result].decode('UTF-8')))
            console.profuse(cmsg)

        if self.wlog:
            self.wlog.writeTx(da, data[:result])

        return result

class SocketUxdNb(object):
    """
    Class to manage non blocking io on UXD (unix domain) socket.
    Use instance method .close() to close socket
    """

    def __init__(self, ha=None, umask=None, bufsize = 1024, wlog=None):
        """
        Initialization method for instance.

        ha = uxd file name
        umask = umask for uxd file
        bufsize = buffer size
        """
        self.ha = ha  # uxd host address string name
        self.umask = umask
        self.bs = bufsize
        self.wlog = wlog

        self.ss = None  # server's socket needs to be opened

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
        Opens socket in non blocking mode.

        if socket not closed properly, binding socket gets error
            socket.error: (48, 'Address already in use')
        """
        #create socket ss = server socket
        self.ss = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

        # make socket address reusable.
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in
        # TIME_WAIT state, without waiting for its natural timeout to expire.
        self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) <  self.bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bs)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < self.bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bs)
        self.ss.setblocking(0) #non blocking socket

        oldumask = None
        if self.umask is not None: # change umask for the uxd file
            oldumask = os.umask(self.umask) # set new and return old

        #bind to Host Address Port
        try:
            self.ss.bind(self.ha)
        except socket.error as ex:
            if not ex.errno == errno.ENOENT: # No such file or directory
                console.terse("socket.error = {0}\n".format(ex))
                return False
            try:
                os.makedirs(os.path.dirname(self.ha))
            except OSError as ex:
                console.terse("OSError = {0}\n".format(ex))
                return False
            try:
                self.ss.bind(self.ha)
            except socket.error as ex:
                console.terse("socket.error = {0}\n".format(ex))
                return False

        if oldumask is not None: # restore old umask
            os.umask(oldumask)

        self.ha = self.ss.getsockname() #get resolved ha after bind

        return True

    def reopen(self):
        """
        Idempotently open socket by closing first if need be
        """
        self.close()
        return self.open()

    def close(self):
        """
        Closes  socket.
        """
        if self.ss:
            self.ss.close() #close socket
            self.ss = None

        try:
            os.unlink(self.ha)
        except OSError:
            if os.path.exists(self.ha):
                raise

    def receive(self):
        """
        Perform non blocking receive on  socket.
        Returns tuple of form (data, sa)
        If no data then returns ('',None)
        """
        try:
            #sa = source address tuple (sourcehost, sourceport)
            data, sa = self.ss.recvfrom(self.bs)
        except socket.error as ex:
            if ex.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return (b'', None) #receive has nothing empty string for data
            else:
                emsg = "socket.error = {0}: receiving at {1}\n".format(ex, self.ha)
                console.profuse(emsg)
                raise #re raise exception ex1

        if console._verbosity >= console.Wordage.profuse:  # faster to check
            cmsg = ("\nServer at {0}, received from {1}:\n------------\n"
                       "{2}\n".format(self.ha, sa, data.decode("UTF-8")))
            console.profuse(cmsg)

        if self.wlog:
            self.wlog.writeRx(sa, data)

        return (data, sa)

    def send(self, data, da):
        """Perform non blocking send on  socket.

           data is string in python2 and bytes in python3
           da is destination address tuple (destHost, destPort)
        """
        try:
            result = self.ss.sendto(data, da) #result is number of bytes sent
        except socket.error as ex:
            emsg = "socket.error = {0}: sending from {1} to {2}\n".format(ex, self.ha, da)
            console.profuse(emsg)
            result = 0
            raise

        if console._verbosity >=  console.Wordage.profuse:
            cmsg = ("Server at {0} sent to {1}, {2} bytes\n"
                    "{3}\n".format(self.ha, da, result, data[:result].decode('UTF-8')))
            console.profuse(cmsg)

        if self.wlog:
            self.wlog.writeTx(da, data)

        return result

class WinMailslotNb(object):
    """
    Class to manage non-blocking io on a Windows Mailslot

    Opens a non-blocking mailslot
    Use instance method to close socket

    Needs Windows Python Extensions
    """

    def __init__(self, ha=None, bufsize=1024, wlog=None):
        """
        Init method for instance
        ha = basename for mailslot path.
        bufsize = default mailslot buffer size
        wlog = over the wire log

        """
        self.ha = ha
        self.bs = bufsize
        self.wlog = wlog

        self.ms = None   # Mailslot needs to be opened

    def open(self):
        """
        Opens mailslot in nonblocking mode
        """
        try:
            self.ms = win32file.CreateMailslot(self.ha, 0, 0, None)
            # ha = path to mailslot
            # 0 = MaxMessageSize, 0 for unlimited
            # 0 = ReadTimeout, 0 to not block
            # None = SecurityAttributes, none for nothing special
        except win32file.error as ex:
            console.terse('mailslot.error = {0}'.format(ex))
            return False

        return True

    def reopen(self):
        """
        Clear the ms and reopen
        """
        self.close()
        return self.open()

    def close(self):
        '''
        Close the mailslot
        '''
        if self.ms:
            win32file.CloseHandle(self.ms)
            self.ms = None

    def receive(self):
        """
        Perform a non-blocking read on the mailslot

        Returns tuple of form (data, sa)
        if no data, returns ('', None)
          but always returns a tuple with 2 elements

        Note win32file.ReadFile returns a tuple: (errcode, data)

        """
        try:
            errcode, data = win32file.ReadFile(self.ms, self.bs)

            # Mailslots don't send their source address
            # We can assign this in a higher level of the stack if needed
            sa = None

            if console._verbosity >= console.Wordage.profuse:  # faster to check
                cmsg = ("Server at {0} received from {1}\n"
                           "{2}\n".format(self.ha, sa, data.decode("UTF-8")))
                console.profuse(cmsg)

            if self.wlog:
                self.wlog.writeRx(sa, data)

            return (data, sa)

        except win32file.error:
            return (b'', None)

    def send(self, data, destmailslot):
        """
        Perform a non-blocking write on the mailslot
        data is string in python2 and bytes in python3
        da is destination mailslot path
        """

        try:
            f = win32file.CreateFile(destmailslot,
                                     win32file.GENERIC_WRITE | win32file.GENERIC_READ,
                                     win32file.FILE_SHARE_READ,
                                     None, win32file.OPEN_ALWAYS, 0, None)
        except win32file.error as ex:
            emsg = 'mailslot.error = {0}: opening mailslot from {1} to {2}\n'.format(
                ex, self.ha, destmailslot)
            console.terse(emsg)
            result = 0
            raise

        try:  # WriteFile returns a tuple, we only care about the number of bytes
            errcode, result = win32file.WriteFile(f, data)
        except win32file.error as ex:
            emsg = 'mailslot.error = {0}: sending from {1} to {2}\n'.format(ex, self.ha, destmailslot)
            console.terse(emsg)
            result = 0
            raise

        finally:
            win32file.CloseHandle(f)

        if console._verbosity >=  console.Wordage.profuse:
            cmsg = ("Server at {0} sent to {1}, {2} bytes\n"
                    "{3}\n".format(self.ha, destmailslot, result, data[:result].decode('UTF-8')))
            console.profuse(cmsg)

        if self.wlog:
            self.wlog.writeTx(da, data)

        return result

class Outgoer(object):
    """
    Nonblocking TCP Socket Client Class.
    """
    Timeout = 1.0  # timeout in seconds
    Reconnectable = False  # auto reconnect flag

    def __init__(self,
                 name=u'',
                 uid=0,
                 ha=None,
                 host=u'127.0.0.1',
                 port=56000,
                 bufsize=8096,
                 wlog=None,
                 store=None,
                 timeout=None,
                 reconnectable=None, ):
        """
        Initialization method for instance.
        name = user friendly name for connection
        uid = unique identifier for connection
        ha = host address duple (host, port) of remote server
        host = host address or tcp server to connect to
        port = socket port
        bufsize = buffer size
        wlog = WireLog object if any
        store = store reference
        timeout = auto reconnect timeout
        reconnectable = Boolean auto reconnect if timed out
        """
        self.name = name
        self.uid = uid
        self.reinitHostPort(ha=ha, hostname=host, port=port)
        self.ha = ha or (host, port)
        host, port = self.ha
        self.hostname = host  # host domain name
        host = socket.gethostbyname(host)  # ip host address
        self.ha = (host, port)
        self.bs = bufsize
        self.wlog = wlog

        self.cs = None  # connection socket
        self.ca = (None, None)  # host address of local connection
        self._accepted = False  # attribute to support accepted property
        self.cutoff = False  # True when detect connection closed on far side
        self.txes = deque()  # deque of data to send
        self.rxes = deque()  # deque of data received
        self.rxbs = bytearray()  # byte array of data recieved

        self.store = store or storing.Store(stamp=0.0)
        self.timeout = timeout if timeout is not None else self.Timeout
        self.timer = StoreTimer(self.store, duration=self.timeout)
        self.reconnectable = reconnectable if reconnectable is not None else self.Reconnectable


    @property
    def host(self):
        '''
        Property that returns host in .ha duple
        '''
        return self.ha[0]

    @host.setter
    def host(self, value):
        '''
        setter for host property
        '''
        self.ha = (value, self.port)

    @property
    def port(self):
        '''
        Property that returns port in .ha duple
        '''
        return self.ha[1]

    @port.setter
    def port(self, value):
        '''
        setter for port property
        '''
        self.ha = (self.host, value)

    @property
    def accepted(self):
        '''
        Property that returns accepted state of TCP socket
        '''
        return self._accepted

    @accepted.setter
    def accepted(self, value):
        '''
        setter for accepted property
        '''
        self._accepted = value

    @property
    def connected(self):
        '''
        Property that returns connected state of TCP socket
        Non-tls tcp is connected when accepted
        '''
        return self.accepted

    @connected.setter
    def connected(self, value):
        '''
        setter for connected property
        '''
        self.accepted = value

    def reinitHostPort(self, ha=None, hostname=u'127.0.0.1', port=56000):
        """
        Reinit self.ha and self.hostname from ha = (host, port) or hostname port
        self.ha is of form (host, port) where host is either dns name or ip
        self.hostname is hostname as dns name
        host eventually is host ip address output from gethostbyname()
        """
        self.ha = ha or (hostname, port)
        hostname, port = self.ha
        self.hostname = hostname  # host domain name
        host = socket.gethostbyname(hostname)  # ip host address
        self.ha = (host, port)

    def actualBufSizes(self):
        """
        Returns duple of the the actual socket send and receive buffer size
        (send, receive)
        """
        if not self.cs:
            return (0, 0)

        return (self.cs.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF),
                self.cs.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))

    def open(self):
        """
        Opens connection socket in non blocking mode.

        if socket not closed properly, binding socket gets error
          socket.error: (48, 'Address already in use')
        """
        self.accepted = False
        self.connected = False
        self.cutoff = False

        #create connection socket
        self.cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # make socket address reusable.
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in
        # TIME_WAIT state, without waiting for its natural timeout to expire.
        self.cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Linux TCP allocates twice the requested size
        if sys.platform.startswith('linux'):
            bs = 2 * self.bs  # get size is twice the set size
        else:
            bs = self.bs

        if self.cs.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) <  bs:
            self.cs.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bs)
        if self.cs.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < bs:
            self.cs.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bs)

        self.cs.setblocking(0) #non blocking socket

        return True

    def reopen(self):
        """
        Idempotently opens socket
        """
        self.close()
        return self.open()

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
            self.accepted = False
            self.connected = False

    close = shutclose  # alias

    def accept(self):
        """
        Attempt nonblocking acceptance connect to .ha
        Returns True if successful
        Returns False if not so try again later
        """
        try:
            result = self.cs.connect_ex(self.ha)  # async connect
        except socket.error as ex:
            console.terse("socket.error = {0}\n".format(ex))
            raise

        if result not in [0, errno.EISCONN]:  # not yet connected
            return False  # try again later

        # now self.cs has new virtual port see self.cs.getsockname()
        self.ca = self.cs.getsockname()  # resolved local connection address
        # self.cs.getpeername() is self.ha
        self.ha = self.cs.getpeername()  # resolved remote connection address

        self.accepted = True
        self.cutoff = False
        return True

    def connect(self):
        """
        Attempt nonblocking connect to .ha
        Returns True if successful
        Returns False if not so try again later
        For non-TLS tcp connect is done when accepted
        """
        return self.accept()

    def serviceConnect(self):
        """
        Service connection attempt
        If not already connected make a nonblocking attempt
        Returns .connected
        """
        if not self.connected:
            self.connect()

            if not self.connected and self.reconnectable:
                if self.timeout > 0.0 and self.timer.expired:  # timed out
                    self.reopen()
                    self.timer.restart()

        return self.connected

    def receive(self):
        """
        Perform non blocking receive from connected socket .cs

        If no data then returns None
        If connection closed then returns ''
        Otherwise returns data
        """
        try:
            data = self.cs.recv(self.bs)
        except socket.error as ex:
            if ex.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return None
            else:
                emsg = ("socket.error = {0}: Outgoer at {1} while receiving "
                        "from {2}\n".format(ex, self.ca, self.ha))
                console.profuse(emsg)
                raise  # re-raise

        if data:  # connection open
            if console._verbosity >= console.Wordage.profuse:  # faster to check
                cmsg = ("\nOutGoer at {0}, received from {1}:\n------------\n"
                           "{2}\n".format(self.ca, self.ha, data.decode("UTF-8")))
                console.profuse(cmsg)

            if self.wlog:  # log over the wire rx
                self.wlog.writeRx(self.ha, data)
        else:  # data empty so connection closed on other end
            self.cutoff = True

        return data

    def serviceReceives(self):
        """
        Service receives until no more
        """
        while self.connected and not self.cutoff:
            data = self.receive()
            if not data:
                break
            self.rxes.append(data)

    def serviceReceiveOnce(self):
        '''
        Retrieve from server only one reception
        '''
        if self.connected and not self.cutoff:
            data = self.receive()
            if data:
                self.rxes.append(data)

    def clearRxbs(self):
        """
        Clear .rxbs
        """
        self.rxbs = bytearray()

    def tailRxbs(self, index):
        """
        Returns duple of (bytes(self.rxbs[index:]), len(self.rxbs))
        slices the tail from index to end and converts to bytes
        also the length of .rxbs to be used to update index
        """
        return (bytes(self.rxbs[index:]), len(self.rxbs))

    def serviceRxes(self):
        """
        Pop off all rxes and append to .rxbs
        """
        while self.rxes:
            self.rxbs.extend(self.rxes.popleft())

    def serviceAllRx(self):
        """
        Service all rx services, service recieves and service rxes
        """
        self.serviceReceives()
        self.serviceRxes()

    def catRxes(self):
        """
        Pop off all rxes and concatenate into single byte string and return
        This is instead of servicesRxes which appends the .rxes to .rxbs
        """
        rx = b''.join(list(self.rxes))
        self.rxes.clear()
        return rx

    def send(self, data):
        """
        Perform non blocking send on connected socket .cs.
        Return number of bytes sent

        data is string in python2 and bytes in python3
        """
        try:
            result = self.cs.send(data) #result is number of bytes sent
        except socket.error as ex:
            result = 0
            if ex.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                emsg = ("socket.error = {0}: Outgoer at {1} while sending "
                        "to {2} \n".format(ex, self.ca, self.ha))
                console.profuse(emsg)
                raise

        if result:
            if console._verbosity >= console.Wordage.profuse:
                cmsg = ("\nOutgoer at {0}, sent {1} bytes to {2}:\n------------\n"
                        "{3}\n".format(self.ca, result, self.ha, data[:result].decode('UTF-8')))
                console.profuse(cmsg)

            if self.wlog:
                self.wlog.writeTx(self.ha, data[:result])

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
        while self.txes and self.connected and not self.cutoff:
            data = self.txes.popleft()
            count = self.send(data)
            if count < len(data):  # put back unsent portion
                self.txes.appendleft(data[count:])
                break  # try again later

ClientSocketTcpNb = Client = Outgoer  # aliases


class Incomer(object):
    """
    Manager class for incoming nonblocking TCP connections.
    """
    def __init__(self,
                 name=u'',
                 uid=0,
                 ha=None,
                 bs=None,
                 ca=None,
                 cs=None,
                 wlog=None):

        """
        Initialization method for instance.
        name = user friendly name for connection
        uid = unique identifier for connection
        ha = host address duple (host, port) near side of connection
        ca = virtual host address duple (host, port) far side of connection
        cs = connection socket object
        wlog = WireLog object if any
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
        self.rxes = deque() # deque of data received
        self.rxbs = bytearray()  # bytearray of data received
        if self.cs:
            self.cs.setblocking(0)  # linux does not preserve blocking from accept

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
            if ex.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return None
            else:
                emsg = ("socket.error = {0}: Incomer at {1} while receiving"
                        " from {2}\n".format(ex, self.ha, self.ca))
                console.profuse(emsg)
                raise  # re-raise

        if data:  # connection open
            if console._verbosity >= console.Wordage.profuse:  # faster to check
                cmsg = ("Incomer at {0} received from {1}\n"
                       "{2}\n".format(self.ha, self.ca, data.decode("UTF-8")))
                console.profuse(cmsg)

            if self.wlog:  # log over the wire rx
                self.wlog.writeRx(self.ca, data)

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
            self.rxes.append(data)

    def serviceReceiveOnce(self):
        '''
        Retrieve from server only one reception
        '''
        if not self.cutoff:
            data = self.receive()
            if data:
                self.rxes.append(data)

    def clearRxbs(self):
        """
        Clear .rxbs
        """
        self.rxbs = bytearray()

    def tailRxbs(self, index):
        """
        Returns duple of (bytes(self.rxbs[index:]), len(self.rxbs))
        slices the tail from index to end and converts to bytes
        also the length of .rxbs to be used to update index
        """
        return (bytes(self.rxbs[index:]), len(self.rxbs))

    def serviceRxes(self):
        """
        Pop off all rxes and append to .rxbs
        """
        while self.rxes:
            self.rxbs.extend(self.rxes.popleft())

    def serviceAllRx(self):
        """
        Service all rx services, service recieves and service rxes
        """
        self.serviceReceives()
        self.serviceRxes()

    def catRxes(self):
        """
        Pop off all rxes and concatenate into single byte string and return
        This is instead of servicesRxes which appends the .rxes to .rxbs
        """
        rx = b''.join(list(self.rxes))
        self.rxes.clear()
        return rx

    def send(self, data):
        """
        Perform non blocking send on connected socket .cs.
        Return number of bytes sent

        data is string in python2 and bytes in python3
        """
        try:
            result = self.cs.send(data) #result is number of bytes sent
        except socket.error as ex:
            result = 0
            if ex.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                emsg = ("socket.error = {0}: Incomer at {1} while "
                        "sending to {2}\n".format(ex, self.ha, self.ca))
                console.profuse(emsg)
                raise

        if result:
            if console._verbosity >=  console.Wordage.profuse:
                cmsg = ("Incomer at {0} sent to {1}, {2} bytes\n"
                        "{3}\n".format(self.ha, self.ha , result,
                                       data[:result].decode('UTF-8')))
                console.profuse(cmsg)

            if self.wlog:
                self.wlog.writeTx(self.ca, data[:result])

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


class Acceptor(object):
    """
    Nonblocking TCP Socket Acceptor Class.
    Listen socket for incoming TCP connections
    """
    def __init__(self,
                 ha=None,
                 host=u'',
                 port=56000,
                 eha=None,
                 bufsize=8096,
                 wlog=None):
        """
        Initialization method for instance.

        ha = host address duple (host, port) for listen socket
        host = host address for listen socket, '' means any interface on host
        port = socket port for listen socket
        eha = external destination address for incoming connections
        bufsize = buffer size
        wlog = WireLog object if any
        """
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
    def __init__(self, **kwa):
        """
        Initialization method for instance.
        """
        super(Server, self).__init__(**kwa)
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
                              wlog=self.wlog)
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

    def shutcloseIx(self, ca):
        """
        Shutdown and close incomer given by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        self.ixes[ca].shutclose()

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

    def serviceRxesIx(self, ca):
        """
        Service rxes for incomer by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        self.ixes[ca].serviceRxes()

    def serviceRxIx(self, ca):
        """
        Service rx for incomer by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        self.ixes[ca].serviceRx()

    def catRxesIx(self, ca):
        """
        Return concatenated rxes for incomer given by connection address ca
        """
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        return (self.ixes[ca].catRxes())

    def transmitIx(self, data, ca):
        '''
        Queue data onto .txes for incomer given by connection address ca
        '''
        if ca not in self.ixes:
            emsg = "Invalid connection address '{0}'".format(ca)
            raise ValueError(emsg)
        self.ixes[ca].tx(data)

    def serviceReceivesAllIx(self):
        """
        Service receives for all incomers in .ixes
        """
        for ix in self.ixes.values():
            ix.serviceReceives()

    def serviceRxesAllIx(self):
        """
        Service rxes for all incomers in .ixes
        """
        for ix in self.ixes.values():
            ix.serviceRxes()

    def serviceAllRxAllIx(self):
        """
        Service rxes for all incomers in .ixes
        """
        for ix in self.ixes.values():
            ix.serviceAllRx()

    def serviceTxesAllIx(self):
        """
        Service transmits for all incomers in .ixes
        """
        for ix in self.ixes.values():
            ix.serviceTxes()

ServerSocketTcpNb = Server  # alias

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


PeerSocketTcpNb = Peer  # alias


try:
    import ssl
except ImportError:
    pass
else:

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


    class OutgoerTls(Outgoer):
        """
        Outgoer with Nonblocking TLS/SSL support
        Nonblocking TCP Socket Client Class.
        """
        def __init__(self,
                     context=None,
                     version=None,
                     certify=None,
                     hostify=None,
                     certedhost="",
                     keypath=None,
                     certpath=None,
                     cafilepath=None,
                     **kwa):
            """
            Initialization method for instance.

            IF no context THEN create one

            IF no version THEN create using library default

            IF certify is not None then use certify else use default

            IF hostify is not none the use hostify else use default

            context = context object for tls/ssl If None use default
            version = ssl version If None use default
            certify = cert requirement If None use default
                      ssl.CERT_NONE = 0
                      ssl.CERT_OPTIONAL = 1
                      ssl.CERT_REQUIRED = 2
            keypath = pathname of local client side PKI private key file path
                      If given apply to context
            certpath = pathname of local client side PKI public cert file path
                      If given apply to context
            cafilepath = Cert Authority file path to use to verify server cert
                      If given apply to context
            hostify = verify server hostName If None use default
            certedhost = server's certificate common name (hostname) to check against
            """
            super(OutgoerTls, self).__init__(**kwa)

            self._connected = False  # attributed supporting connected property

            if context is None:  # create context
                if not version:  # use default context
                    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
                    hostify = hostify if hostify is not None else context.check_hostname
                    context.check_hostname = hostify
                    certify = certify if certify is not None else context.verify_mode
                    context.verify_mode = certify

                else:  # create context with specified protocol version
                    context = ssl.SSLContext(version)
                    # disable bad protocols versions
                    context.options |= ssl.OP_NO_SSLv2
                    context.options |= ssl.OP_NO_SSLv3
                    # disable compression to prevent CRIME attacks (OpenSSL 1.0+)
                    context.options |= getattr(ssl._ssl, "OP_NO_COMPRESSION", 0)
                    context.verify_mode = certify = ssl.CERT_REQUIRED if certify is None else certify
                    context.check_hostname = hostify = True if hostify else False

            self.context = context
            self.certedhost = certedhost or self.hostname

            if cafilepath:
                context.load_verify_locations(cafile=cafilepath,
                                              capath=None,
                                              cadata=None)
            elif context.verify_mode != ssl.CERT_NONE:
                context.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)

            if keypath or certpath:
                context.load_cert_chain(certfile=certpath, keyfile=keypath)

            if hostify and certify == ssl.CERT_NONE:
                raise ValueError("Check Hostname needs a SSL context with "
                                 "either CERT_OPTIONAL or CERT_REQUIRED")

        @property
        def connected(self):
            '''
            Property that returns connected state of TCP socket
            TLS tcp is connected when accepted and handshake completed
            '''
            return self._connected

        @connected.setter
        def connected(self, value):
            '''
            setter for connected property
            '''
            self._connected = value

        def shutclose(self):
            """
            Shutdown and close connected socket .cs
            """
            if self.cs:
                self.shutdown()
                self.cs.close()  #close socket
                self.cs = None
                self.accepted = False
                self.connected = False

        close = shutclose  # alias

        def wrap(self):
            """
            Wrap socket .cs in ssl context
            """
            self.cs = self.context.wrap_socket(self.cs,
                                               server_side=False,
                                               do_handshake_on_connect=False,
                                               server_hostname=self.certedhost)

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

        def connect(self):
            """
            Attempt nonblocking connect to .ha
            Returns True if successful
            Returns False if not so try again later
            Connected when both accepted connection and TLS handshake complete
            """
            if not self.accepted:
                self.accept()

                if self.accepted:  # only do this once immediately after accepted
                    if not self.certedhost:
                        self.certedhost = self.ha[0]
                    self.wrap()

            if self.accepted and not self.connected:
                self.handshake()

            return self.connected


        #def serviceConnect(self):
            #"""
            #Service connection and handshake attempt
            #If not already accepted and handshaked  Then
                 #make nonblocking attempt
            #Returns .handshaked
            #"""
            #if not self.connected:
                #self.connect()

            #return self.connected

        def receive(self):
            """
            Perform non blocking receive from connected socket .cs

            If no data then returns None
            If connection closed then returns ''
            Otherwise returns data
            """
            try:
                data = self.cs.recv(self.bs)
            except ssl.SSLError as ex:
                if ex.errno in (ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE):
                    return None
                else:
                    emsg = ("SSLError = {0}: OutgoerTLS at {1} receiving"
                            " from {2}\n".format(ex, self.ca, self.ha))
                    console.profuse(emsg)
                    raise  # re-raise

            if data:  # connection open
                if console._verbosity >= console.Wordage.profuse:  # faster to check
                    cmsg = ("\nOutgoer at {0}, received from {1}:\n------------\n"
                               "{2}\n".format(self.ca, self.ha, data.decode("UTF-8")))
                    console.profuse(cmsg)

                if self.wlog:  # log over the wire rx
                    self.wlog.writeRx(self.ha, data)
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
            except ssl.SSLError as ex:
                result = 0
                if ex.errno not in (ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE):
                    emsg = ("socket.error = {0}: OutgoerTLS at {1} while sending "
                            "to {2} \n".format(ex, self.ca, self.ha))
                    console.profuse(emsg)
                    raise

            if result:
                if console._verbosity >=  console.Wordage.profuse:
                    cmsg = ("\nOutgoer at {0}, sent {1} bytes to {2}:\n------------\n"
                            "{3}\n".format(self.ca, result, self.ha, data[:result].decode('UTF-8')))
                    console.profuse(cmsg)

                if self.wlog:
                    self.wlog.writeTx(self.ha, data[:result])

            return result


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
            except ssl.SSLError as ex:
                if ex.errno in (ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE):
                    return None
                else:
                    emsg = ("SSLError = {0}: IncomerTLS at {1} while receiving"
                            " from {2}\n".format(ex, self.ha, self.ca))
                    console.profuse(emsg)
                    raise  # re-raise

            if data:  # connection open
                if console._verbosity >= console.Wordage.profuse:  # faster to check
                    cmsg = ("Incomer at {0} received from {1}\n"
                           "{2}\n".format(self.ha, self.ca, data.decode("UTF-8")))
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
            except ssl.SSLError as ex:
                result = 0
                if ex.errno not in (ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE):
                    emsg = ("SSLError = {0}: IncomerTLS at {1} while "
                            "sending to {2}\n".format(ex, self.ha, self.ca))
                    console.profuse(emsg)
                    raise

            if result:
                if console._verbosity >=  console.Wordage.profuse:
                    cmsg = ("Incomer at {0} sent to {1}, {2} bytes\n"
                            "{3}\n".format(self.ha, self.ha , result,
                                           data[:result].decode('UTF-8')))
                    console.profuse(cmsg)

                if self.wlog:
                    self.wlog.writeTx(self.ca, data[:result])

            return result


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
