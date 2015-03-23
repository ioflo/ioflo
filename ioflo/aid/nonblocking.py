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
                 stringify=False):
        """
        Initialization method for instance.
        path = directory for log files
        prefix = prefix to include in log name if provided
        midfix = another more prefix for log name if provided
        rx = Boolean create rx log file if True
        tx = Boolean create tx log file if True
        stringify = Boolean use StringIO instead of File object
        """
        self.path = path  # path to directory where log files go must end in /
        self.prefix = prefix
        self.midfix = midfix
        self.rx = True if rx else False
        self.tx = True if tx else False
        self.rxLog = None  # receive log file
        self.txLog = None  # transmit log file
        self.stringify = True if stringify else False

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

        if self.rx:
            if not self.stringify:
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
            if not self.stringify:
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
        Returns rx string buffer value if .stringify else None
        """
        if self.stringify and self.rxLog and not self.rxLog.closed:
            return (self.rxLog.getvalue())
        return None

    def getTx(self):
        """
        Returns tx string buffer value if .stringify else None
        """
        if self.stringify and self.txLog and not self.txLog.closed:
            return (self.txLog.getvalue())
        return None

    def writeRx(self, sa, data):
        """
        Write bytes data received from source address sa,
        """
        if self.rx and self.rxLog:
            self.rxLog.write(ns2b("{0}\n".format(sa)))
            self.rxLog.write(data)
            self.rxLog.write(b'\n')

    def writeTx(self, da, data):
        """
        Write bytes data transmitted to destination address da,
        """
        if self.tx and self.txLog:
            self.txLog.write(ns2b("{0}\n".format(da)))
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
        self.ss = None #server's socket needs to be opened
        self.wlog = wlog

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
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return (b'', None) #receive has nothing empty string for data
            else:
                emsg = "socket.error = {0}: receiving at {1}\n".format(ex, self.ha)
                console.profuse(emsg)
                raise #re raise exception ex1

        if console._verbosity >= console.Wordage.profuse:  # faster to check
            cmsg = ("Server at {0} received from {1}\n"
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
            cmsg = ("Server at {0} sent to {1}, {2} bytes\n"
                    "{3}\n".format(self.ha, da, result, data[:result].encode('UTF-8')))
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
        self.ss = None  # server's socket needs to be opened
        self.wlog = wlog

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
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return (b'', None) #receive has nothing empty string for data
            else:
                emsg = "socket.error = {0}: receiving at {1}\n".format(ex, self.ha)
                console.profuse(emsg)
                raise #re raise exception ex1

        if console._verbosity >= console.Wordage.profuse:  # faster to check
            cmsg = ("Server at {0} received from {1}\n"
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
                    "{3}\n".format(self.ha, da, result, data[:result].encode('UTF-8')))
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

    def __init__(self, ha=None, bufsize=1024, path='', log=False):
        """
        Init method for instance

        bufsize = default mailslot buffer size
        path = path to directory where logfiles go.  Must end in /.
        ha = basename for mailslot path.
        """
        self.ha = ha
        self.bs = bufsize
        self.ms = None   # Mailslot needs to be opened

        self.path = path
        self.txLog = None     # Transmit log
        self.rxLog = None     # receive log
        self.log = log

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

        if self.log:
            if not self.openLogs():
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

        self.closeLogs()

    def receive(self):
        """
        Perform a non-blocking read on the mailslot

        Returns tuple of form (data, sa)
        if no data, returns ('', None)
          but always returns a tuple with 2 elements

        Note win32file.ReadFile returns a tuple: (errcode, data)

        """
        try:
            data = win32file.ReadFile(self.ms, self.bs)

            # Mailslots don't send their source address
            # We can pick this up in a higher level of the stack if we
            # need
            sa = None

            message = "Server at {0} received {1}\n".format(
                self.ha, data[1])

            console.profuse(message)

            if self.log and self.rxLog:
                self.rxLog.write("%s\n%s\n" % (sa, repr(data[1])))

            return (data[1], sa)

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

        try:
            result = win32file.WriteFile(f, data)
            console.profuse("Server at {0} sent {1} bytes\n".format(self.ha,
                                                                    result))
        except win32file.error as ex:
            emsg = 'mailslot.error = {0}: sending from {1} to {2}\n'.format(ex, self.ha, destmailslot)
            console.terse(emsg)
            result = 0
            raise

        finally:
            win32file.CloseHandle(f)

        if self.log and self.txLog:
            self.txLog.write("%s %s bytes\n%s\n" %
                             (str(destmailslot), str(result), repr(data)))

        # WriteFile returns a tuple, we only care about the number of bytes
        return result[1]

    def openLogs(self, path = ''):
        """Open log files

        """
        date = time.strftime('%Y%m%d_%H%M%S',time.gmtime(time.time()))
        name = "%s%s_%s_%s_tx.txt" % (self.path, self.ha[0], str(self.ha[1]), date)
        try:
            self.txLog = open(name, 'w+')
        except IOError:
            self.txLog = None
            self.log = False
            return False
        name = "%s%s_%s_%s_rx.txt" % (self.path, self.ha[0], str(self.ha[1]), date)
        try:
            self.rxLog = open(name, 'w+')
        except IOError:
            self.rxLog = None
            self.log = False
            return False

        return True

    def closeLogs(self):
        """Close log files

        """
        if self.txLog and not self.txLog.closed:
            self.txLog.close()
        if self.rxLog and not self.rxLog.closed:
            self.rxLog.close()


class ServerSocketTcpNb(object):
    """
    Nonblocking TCP Socket Server Class.
    """
    def __init__(self, ha=None, host='', port=56000, eha=None, bufsize=8096,
                 path='', log=False, txLog=None, rxLog=None):
        """
        Initialization method for instance.

        ha = host address duple (host, port) for listen socket
        host = host address for listen socket, '' means any interface on host
        port = socket port for listen socket
        eha = external destination address for incoming connections
        bufsize = buffer size
        path = path to log directory
        log = boolean flag, creates logs if True
        txLog = log file object or None
        rxLog = log file object or None
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
        self.ss = None  # listen socket for accepts

        self.path = path #path to directory where log files go must end in /
        self.txLog = txLog  # transmit log file object
        self.rxLog = rxLog  # receive log file object
        self.log = log
        self.ownTxLog = False  # txLog created not passed in
        self.ownRxLog = False  # rxLog created not passed in

    def openLogs(self, path = ''):
        """
        Open log files
        """
        date = time.strftime('%Y%m%d_%H%M%S',time.gmtime(time.time()))

        if not self.txLog:
            name = "{0}{1}_{2}_{3}_tx.txt".format(self.path, self.ha[0], self.ha[1], date)
            try:
                self.txLog = open(name, 'w+')
            except IOError:
                self.txLog = None
                self.log = False
                return False
            self.ownTxLog = True

        if not self.rxLog:
            name = "{0}{1}_{2}_{3}_rx.txt".format(self.path, self.ha[0], self.ha[1], date)
            try:
                self.rxLog = open(name, 'w+')
            except IOError:
                self.rxLog = None
                self.log = False
                return False
            self.ownRxLog = True

        return True

    def closeLogs(self):
        """
        Close log files
        """
        if self.txLog and not self.txLog.closed and self.ownTxLog:
            self.txLog.close()
        if self.rxLog and not self.rxLog.closed and self.ownTxLog:
            self.rxLog.close()

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

        if self.log:
            if not self.openLogs():
                return False

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

        self.closeLogs()

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
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return (None, None)  # nothing yet
            emsg = ("socket.error = {0}: server at {1} while "
                    "accepting \n".format(ex, self.ha))
            console.profuse(emsg)
            raise  # re-raise
        return (cs, ca)

    @staticmethod
    def shutdown(cs, how=socket.SHUT_RDWR):
        """
        Shutdown connected socket cs
        """
        if cs:
            try:
                cs.shutdown(how)  # shutdown socket
            except socket.error as ex:
                #console.terse("socket.error = {0}\n".format(ex))
                pass

    @staticmethod
    def shutdownSend(cs):
        """
        Shutdown send on connected socket cs
        """
        if cs:
            try:
                cs.shutdown(socket.SHUT_WR)  # shutdown socket
            except socket.error as ex:
                #console.terse("socket.error = {0}\n".format(ex))
                pass

    @staticmethod
    def shutdownReceive(cs):
        """
        Shutdown receive on connected socket cs
        """
        if cs:
            try:
                cs.shutdown(socket.SHUT_RD)  # shutdown socket
            except socket.error as ex:
                #console.terse("socket.error = {0}\n".format(ex))
                pass

    @staticmethod
    def shutclose(cs):
        """
        Shutdown and close connected socket cs
        """
        if cs:
            try:
                cs.shutdown(socket.SHUT_RDWR)  # shutdown socket
            except socket.error as ex:
                #console.terse("socket.error = {0}\n".format(ex))
                pass
            cs.close()  #close socket

    def receive(self, cs):
        """
        Perform non blocking receive from connected socket cs

        If no data then returns None
        If connection closed then returns ''
        Otherwise returns data
        """
        try:
            data = cs.recv(self.bs)
        except socket.error as ex:
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return None
            else:
                emsg = ("socket.error = {0}: server at {1} while receiving"
                        "\n".format(ex, self.ha))
                console.profuse(emsg)
                raise  # re-raise

        message = ("Server at {0} received {1}\n".format(self.ha, data))
        console.profuse(message)
        if self.log and self.rxLog:
            self.rxLog.write("{0}\n{1}\n".format(self.ha, data))
        return data

    def receiveFrom(self, cs):
        """
        If no data then returns (None, sa)
        If connection closed on far side then returns ('', sa)
        Otherwise returns (data, ca)

        Where sa is source socket's ha given by .getpeername()
        """
        return (self.receive(cs), cs.getpeername())

    def send(self, data, cs):
        """
        Perform non blocking send on connected socket cs.
        Return number of bytes sent

        data is string in python2 and bytes in python3
        """
        try:
            result = cs.send(data) #result is number of bytes sent
        except socket.error as ex:
            result = 0
            if ex.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                emsg = ("socket.error = {0}: server at {1} while"
                        "sending\n".format(ex, self.ha,))
                console.profuse(emsg)
                raise

        console.profuse("Server at {0} sent {1} "
                        "bytes\n".format(self.ha, result))

        if self.log and self.txLog:
            self.txLog.write("{0}\n{1}\n".format(self.ha, data))

        return result

    def serviceAx(self):
        """
        Service any accept requests
        Returns list of accepted connection socket duples
        [(cs,ca)]
        """
        accepteds = []
        while True:
            cs, ca = self.accept()
            if not cs:
                break
            accepteds.append((cs, ca))
        return accepteds


class ClientSocketTcpNb(object):
    """
    Nonblocking TCP Socket Client Class.
    """
    def __init__(self, ha=None, host='', port=56000, bufsize=8096,
                 path='', log=False, txLog=None, rxLog=None):
        """
        Initialization method for instance.

        ha = host address duple (host, port) of remote server
        host = host address or tcp server to connect to
        port = socket port
        bufsize = buffer size
        path = path to log directory must end in /
        log = boolean flag, creates logs if True
        txLog = transmit log file object or None
        rxLog = receive log file object or None
        """
        self.ha = ha or (host,port)
        self.ca = (None, None)  # host address of local connection
        self.bs = bufsize
        self.cs = None  # connection socket
        self.connected = False  # connected successfully
        self.path = path
        self.txLog = txLog  # transmit log
        self.rxLog = rxLog  # receive log
        self.log = log
        self.ownTxLog = False  # txLog created not passed in
        self.ownRxLog = False  # rxLog created not passed in

    def openLogs(self, path = ''):
        """
        Open log files
        """
        date = time.strftime('%Y%m%d_%H%M%S',time.gmtime(time.time()))

        if not self.txLog:
            name = "{0}{1}_{2}_{3}_tx.txt".format(self.path, self.ha[0], self.ha[1], date)
            try:
                self.txLog = open(name, 'w+')
            except IOError:
                self.txLog = None
                self.log = False
                return False
            self.ownTxLog = True

        if not self.rxLog:
            name = "{0}{1}_{2}_{3}_rx.txt".format(self.path, self.ha[0], self.ha[1], date)
            try:
                self.rxLog = open(name, 'w+')
            except IOError:
                self.rxLog = None
                self.log = False
                return False
            self.ownRxLog = True

        return True

    def closeLogs(self):
        """
        Close log files
        """
        if self.txLog and not self.txLog.closed and self.ownTxLog:
            self.txLog.close()
        if self.rxLog and not self.rxLog.closed and self.ownTxLog:
            self.rxLog.close()

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
        self.connected = False

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

        if self.log:
            if not self.openLogs():
                return False

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
            self.connected = False

    def close(self):
        """
        Closes local connection socket
        """
        self.shutclose()
        self.closeLogs()

    def connect(self):
        """
        Attempt nonblocking connect to .ha
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

        self.connected = True
        # now self.cs has new virtual port see self.cs.getsockname()
        self.ca = self.cs.getsockname()  # resolved local connection address
        # self.cs.getpeername() is self.ha
        self.ha = self.cs.getpeername()  # resolved remote connection address

        return True

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
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return None
            else:
                emsg = ("socket.error = {0}: server at {1} receiving "
                        "from {2}\n".format(ex, self.ca, self.ha))
                console.profuse(emsg)
                raise  # re-raise
        message = ("Client at {0} received from {1}, "
                   "{2}\n".format(self.ca, self.ha, data))
        console.profuse(message)
        if self.log and self.rxLog:
            self.rxLog.write("{0}\n{1}\n".format(self.ha, data))
        return data

    def receiveFrom(self):
        """
        If no data then returns (None, sa)
        If connection closed on far side then returns ('', sa)
        Otherwise returns (data, ca)

        Where sa is source socket's ha given by .getpeername()
        """
        return (self.receive(), self.ha)

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
            if ex.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                emsg = ("socket.error = {0}: server at {1} sending "
                        "to {2} \n".format(ex, self.ca, self.ha))
                console.profuse(emsg)
                raise

        console.profuse("Client at {0} sent to {1}, {2} "
                        "bytes\n".format(self.ca, self.ha, result))

        if self.log and self.txLog:
            self.txLog.write("{0}\n{1}\n".format(self.ha, data))

        return result

class Incomer(object):
    """
    Manager class for incoming nonblocking TCP connections.
    """
    def __init__(self,
                 name='',
                 uid=0,
                 ha=None,
                 ca=None,
                 cs=None,
                 log=False,
                 txLog=None,
                 rxLog=None):

        """
        Initialization method for instance.
        name = user friendly name for connection
        uid = unique identifier for connection
        ha = host address duple (host, port) near side of connection
        ca = virtual host address duple (host, port) far side of connection
        cs = connection socket object
        log = Boolean If True then log rx tx to log files
        txLog = transmit log file
        rxLog = receive log file
        """
        self.name = name
        self.uid = uid
        self.ha = ha
        self.ca = ca
        self.cs = cs
        self.closed  # True when detect connection closed on far side
        self.txes = deque()  # deque of data to send
        self.rxes = deque() # deque of data received
        self.log = log
        self.txLog = txLog
        self.rxLog = rxLog

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
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return None
            else:
                emsg = ("socket.error = {0}: Incomer at {1} while receiving from {2}\n"
                        "f\n".format(ex, self.ha, self.ca))
                console.profuse(emsg)
                raise  # re-raise

        if data == '':  # far side shutdown or closed
            self.closed = True

        message = ("Incomer at {0} received from {1}, "
                   "{2}\n".format(self.ha, self.ca, data))
        console.profuse(message)
        if self.log and self.rxLog:
            self.rxLog.write("{0}\n{1}\n".format(self.ca, data))
        return data

    def receiveFrom(self):
        """
        If no data then returns (None, sa)
        If connection closed on far side then returns ('', sa)
        Otherwise returns (data, ca)

        Where sa is source socket's ha given by self.ca = self.cs.getpeername()
        """
        return (self.receive(), self.ca)

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
            if ex.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                emsg = ("socket.error = {0}: server at {1} "
                        "sending\n".format(ex, self.ha,))
                console.profuse(emsg)
                raise

        console.profuse("Incomer at {0} sent to {1}, {2} "
                        "bytes\n".format(self.ha, self.ca, result))

        if self.log and self.txLog:
            self.txLog.write("{0}\n{2}\n".format(self.ca, data))

        return result


class Outgoer(object):
    """
    Manager class for outgoing nonblocking TCP connections.
    """
    def __init__(self,
                 name='',
                 uid=0,
                 ha=None,
                 ca=None,
                 cs=None,
                 bufsize=8096,
                 log=False,
                 txLog=None,
                 rxLog=None):
        """
        Initialization method for instance.
        name = user friendly name for connection
        uid = unique identifier for connection
        ha = host address duple (host, port) far side of connection
        ca = virtual host address duple (host, port) near side of connection
        cs = connection socket object
        bufsize = size of send and receive socket buffers
        log = Boolean If True then log rx tx to log files
        txLog = transmit log file
        rxLog = receive log file
        """
        self.name = name
        self.uid = uid
        self.ha = ha
        self.ca = ca
        self.cs = cs
        self.bs = bufsize
        self.closed  # True when detect connection closed on far side
        self.connected  # True once connection completed
        self.txes = deque()  # deque of data to send
        self.rxes = deque() # deque of data received
        self.log = log
        self.txLog = txLog
        self.rxLog = rxLog

    def open(self):
        """
        Opens connection socket in non blocking mode.

        if socket not closed properly, binding socket gets error
          socket.error: (48, 'Address already in use')
        """
        self.connected = False

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
            self.connected = False

    close = shutclose  # alias

    def connect(self):
        """
        Attempt nonblocking connect to .ha
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

        self.connected = True
        # now self.cs has new virtual port see self.cs.getsockname()
        self.ca = self.cs.getsockname()  # resolved local connection address
        # self.cs.getpeername() is self.ha
        self.ha = self.cs.getpeername()  # resolved remote connection address

        return True

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
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return None
            else:
                emsg = ("socket.error = {0}: server at {1} receiving "
                        "from {2}\n".format(ex, self.ca, self.ha))
                console.profuse(emsg)
                raise  # re-raise
        message = ("Client at {0} received from {1}, "
                   "{2}\n".format(self.ca, self.ha, data))
        console.profuse(message)
        if self.log and self.rxLog:
            self.rxLog.write("{0}\n{1}\n".format(self.ha, data))
        return data

    def receiveFrom(self):
        """
        If no data then returns (None, sa)
        If connection closed on far side then returns ('', sa)
        Otherwise returns (data, ca)

        Where sa is source socket's ha given by .getpeername()
        """
        return (self.receive(), self.ha)

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
            if ex.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                emsg = ("socket.error = {0}: server at {1} sending "
                        "to {2} \n".format(ex, self.ca, self.ha))
                console.profuse(emsg)
                raise

        console.profuse("Client at {0} sent to {1}, {2} "
                        "bytes\n".format(self.ca, self.ha, result))

        if self.log and self.txLog:
            self.txLog.write("{0}\n{1}\n".format(self.ha, data))

        return result

class PeerSocketTcpNb(object):
    """
    Nonblocking Peer TCP Socket Class.
    Supports both incoming and outgoing connections.
    """
    def __init__(self, ha=None, host='', port=56000, eha=None, bufsize=8096,
                 path='', log=False, txLog=None, rxLog=None):
        """
        Initialization method for instance.

        ha = host address duple (host, port) for listen socket
        host = host address for listen socket, '' means any interface on host
        port = socket port for listen socket
        eha = external destination address for incoming connections
        bufsize = buffer size
        path = path to log directory
        log = boolean flag, creates logs if True
        txLog = log file object or None
        rxLog = log file object or None
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
        self.ss = None  # listen socket for accepts
        self.ixers = odict()  # incoming connections indexed by ca far side
        self.oxers = odict()  # outgoing connections indexed by ha far side

        self.path = path #path to directory where log files go must end in /
        self.txLog = txLog  # transmit log file object
        self.rxLog = rxLog  # receive log file object
        self.log = log
        self.ownTxLog = False  # txLog created not passed in
        self.ownRxLog = False  # rxLog created not passed in

    def openLogs(self, path = ''):
        """
        Open log files
        """
        date = time.strftime('%Y%m%d_%H%M%S',time.gmtime(time.time()))

        if not self.txLog:
            name = "{0}{1}_{2}_{3}_tx.txt".format(self.path, self.ha[0], self.ha[1], date)
            try:
                self.txLog = open(name, 'w+')
            except IOError:
                self.txLog = None
                self.log = False
                return False
            self.ownTxLog = True

        if not self.rxLog:
            name = "{0}{1}_{2}_{3}_rx.txt".format(self.path, self.ha[0], self.ha[1], date)
            try:
                self.rxLog = open(name, 'w+')
            except IOError:
                self.rxLog = None
                self.log = False
                return False
            self.ownRxLog = True

        return True

    def closeLogs(self):
        """
        Close log files
        """
        if self.txLog and not self.txLog.closed and self.ownTxLog:
            self.txLog.close()
        if self.rxLog and not self.rxLog.closed and self.ownTxLog:
            self.rxLog.close()

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

        if self.log:
            if not self.openLogs():
                return False

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

        self.closeLogs()

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
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return (None, None)  # nothing yet
            emsg = ("socket.error = {0}: server at {1} while "
                    "accepting \n".format(ex, self.ha))
            console.profuse(emsg)
            raise  # re-raise
        return (cs, ca)

    def serviceAx(self):
        """
        Service any accept requests and add to .ixers
        Returns list of accepted connection socket duples
        [(cs,ca)]
        """
        accepteds = []
        while True:
            cs, ca = self.accept()
            if not cs:
                break
            accepteds.append((cs, ca))
            if ca != cs.getpeername() or self.ha != cs.getsockename():
                raise ValueError("Accepted socket host addresses malformed for "
                                 "peer ha {0} != {1}, ca {2} != {3}\n".format(
                                 self.ha, cs.getsockname(), ca, cs.getpeername()))
            incomer = Incomer(ha=cs.getsockname(),
                              ca=cs.getpeername(),
                              cs=cs,
                             log=self.log,
                             txLog=self.txLog,
                             rxLog=self.rxLog)
            self.ixers[ca] = incomer
        return accepteds

    def _handleOneReceived(self):
        '''
        Handle one received message from server
        assumes that there is a server
        '''
        try:
            rx, ra = self.server.receive()  # if no data the duple is ('',None)
        except socket.error as ex:
            if ex.errno == errno.ECONNRESET:
                return False
        if not rx:  # no received data
            return False
        self.rxes.append((rx, ra))     # duple = ( packet, source address)
        return True

    def serviceReceives(self):
        '''
        Retrieve from server all recieved and put on the rxes deque
        '''
        if self.server:
            while self._handleOneReceived():
                pass

    def serviceReceives(self, ca):
        """
        Perform non blocking receive from connected socket cs

        If no data then returns None
        If connection closed then returns ''
        Otherwise returns data
        """
        try:
            data = cs.recv(self.bs)
        except socket.error as ex:
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return None
            else:
                emsg = ("socket.error = {0}: server at {1} receiving "
                        "f\n".format(ex, self.ha))
                console.profuse(emsg)
                raise  # re-raise

        message = ("Server at {0} received {1}\n".format(self.ha, data))
        console.profuse(message)
        if self.log and self.rxLog:
            self.rxLog.write("%s\n%s\n" % (str(cs.getpeername()), repr(data)))
        return data

    def _handleOneTx(self, laters, blocks):
        '''
        Handle one message on .txes deque
        Assumes there is a message
        laters is deque of messages to try again later
        blocks is list of destinations that already blocked on this service
        '''
        tx, ta = self.txes.popleft()  # duple = (packet, destination address)

        if ta in blocks: # already blocked on this iteration
            laters.append((tx, ta)) # keep sequential
            return

        try:
            self.server.send(tx, ta)
        except socket.error as ex:
            if (ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK,
                             errno.ENETUNREACH, errno.ETIME,
                             errno.EHOSTUNREACH, errno.EHOSTDOWN,
                             errno.ECONNRESET]):
                # problem sending such as busy with last message. save it for later
                laters.append((tx, ta))
                blocks.append(ta)
            else:
                raise

        def serviceTxes(self):
            '''
            Service the .txes deque to send  messages through server
            '''
            if self.server:
                laters = deque()
                blocks = []
                while self.txes:
                    self._handleOneTx(laters, blocks)
                while laters:
                    self.txes.append(laters.popleft())


    def serviceSends(self, data, cs):
        """
        Perform non blocking send on connected socket cs.
        Return number of bytes sent

        data is string in python2 and bytes in python3
        """
        try:
            result = cs.send(data) #result is number of bytes sent
        except socket.error as ex:
            result = 0
            if ex.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                emsg = ("socket.error = {0}: server at {1} "
                        "sending\n".format(ex, self.ha,))
                console.profuse(emsg)
                raise

        console.profuse("Server at {0} sent {1} "
                        "bytes\n".format(self.ha, result))

        if self.log and self.txLog:
            self.txLog.write("%s %s bytes\n%s\n" %
                             (str(cs.getpeername()), str(result), repr(data)))

        return result



class OldSocketTcpPeerNb(object):
    """
    Nonblocking TCP Server Socket Class.
    """
    def __init__(self, ha=None, host='', port=56000, bufsize=8096,
                 path='', log=False):
        """
        Initialization method for instance.

        ha = host address duple (host, port) for listen socket
        host = '' equivalant to any interface on host
        port = socket port
        bufsize = buffer size
        path = path to log directory
        log = boolean flag, creates logs if True
        """
        self.ha = ha or (host,port)  # ha = host address
        self.bs = bufsize
        self.ss = None  # own socket needs to be opened
        self.cxes = odict()  # client connections
        # keys are duples (host, virtual port), values are sockets

        self.path = path #path to directory where log files go must end in /
        self.txLog = None #transmit log
        self.rxLog = None #receive log
        self.log = log

    def openLogs(self, path = ''):
        """Open log files

        """
        date = time.strftime('%Y%m%d_%H%M%S',time.gmtime(time.time()))
        name = "%s%s_%s_%s_tx.txt" % (self.path, self.ha[0], str(self.ha[1]), date)
        try:
            self.txLog = open(name, 'w+')
        except IOError:
            self.txLog = None
            self.log = False
            return False
        name = "%s%s_%s_%s_rx.txt" % (self.path, self.ha[0], str(self.ha[1]), date)
        try:
            self.rxLog = open(name, 'w+')
        except IOError:
            self.rxLog = None
            self.log = False
            return False

        return True

    def closeLogs(self):
        """Close log files

        """
        if self.txLog and not self.txLog.closed:
            self.txLog.close()
        if self.rxLog and not self.rxLog.closed:
            self.rxLog.close()

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
        """Opens listen socket in non blocking mode.

           if socket not closed properly, binding socket gets error
              socket.error: (48, 'Address already in use')
        """
        #create socket ss = server socket
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # make socket address reusable.
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in
        # TIME_WAIT state, without waiting for its natural timeout to expire.
        self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Linux TCP allocates twice the requested size so get size is twice the set size
        if sys.platform.startswith('linux'):
            bs = 2 * self.bs
        else:
            bs = self.bs
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) < bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bs)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bs)
        self.ss.setblocking(0) #non blocking socket

        # TCP Server socket eventually used to accept connections
        try:  # bind to listen socket (host, port) to receive connections
            self.ss.bind(self.ha)
            self.ss.listen(5)
        except socket.error as ex:
            console.terse("socket.error = {0}\n".format(ex))
            return False

        self.ha = self.ss.getsockname()  # get resolved ha after bind

        if self.log:
            if not self.openLogs():
                return False

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

        self.closeLogs()

    def closeAll(self):
        """
        Closes listen socket and all connections
        """
        self.close()
        self.shutcloseAll()

    def accept(self):
        """
        Accept new connection
        Add to clients dict
        Returns duple (cs, ca) of connected socket and connected host address
        Otherwise if no new connection returns (None, None)
        """
        # accept new virtual connected socket created from server socket
        try:
            cs, ca = self.ss.accept()  # virtual connection (socket, host address)
        except socket.error as ex:
            if ex.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                emsg = ("socket.error = {0}: server at {1} while "
                        "accepting \n".format(ex, self.ha))
                console.profuse(emsg)
                raise  # re-raise
            return (None, None)  # nothing yet
        return (cs, ca)

    def acceptCx(self):
        """
        Accepts new connection and adds to .cxes
        """
        cs, ca = self.accept()
        if cs:
            self.cxes[ca] = cs

    @staticmethod
    def shutdown(cs, how=socket.SHUT_RDWR):
        """
        Shutdown and close connected socket cs
        """
        if cs:
            try:
                cs.shutdown(how)  # shutdown socket
            except socket.error as ex:
                #console.terse("socket.error = {0}\n".format(ex))
                pass

    @staticmethod
    def shutdownSend(cs, how=socket.SHUT_WR):
        """
        Shutdown and close connected socket cs
        """
        if cs:
            try:
                cs.shutdown(how)  # shutdown socket
            except socket.error as ex:
                #console.terse("socket.error = {0}\n".format(ex))
                pass

    @staticmethod
    def shutdownReceive(cs, how=socket.SHUT_RD):
        """
        Shutdown and close connected socket cs
        """
        if cs:
            try:
                cs.shutdown(how)  # shutdown socket
            except socket.error as ex:
                #console.terse("socket.error = {0}\n".format(ex))
                pass

    def shutdownCx(self, ca, how=socket.SHUT_RDWR):
        """
        Shutdown connection indexed by ca (host, port)
        """
        if ca in self.cxes:
            cs = self.cxes[ca]
            self.shutdown(cs, how=how)

    def shutdownSendCx(self, ca):
        """
        Shutdown sends on connection indexed by ca (host, port)
        """
        self.shutdownCx(cs, how=socket.SHUT_WR)

    def shutdownReceiveCx(self, ca):
        """
        Shutdown receives on connection indexed by ca (host, port)
        """
        self.shutdownCx(cs, how=socket.SHUT_RD)

    @staticmethod
    def shutclose(cs):
        """
        Shutdown and close connected socket cs
        """
        if cs:
            try:
                cs.shutdown(socket.SHUT_RDWR)  # shutdown socket
            except socket.error as ex:
                #console.terse("socket.error = {0}\n".format(ex))
                pass
            cs.close()  #close socket

    def shutcloseCx(self, ca):
        """
        Shutdown, close, and remove from .cxes, connection indexed by ca (host, port)
        """
        if ca in self.cxes:
            cs = self.cxes[ca]
            self.shutclose(cs)
            del self.cxes[ca]

    def shutcloseAll(self):
        """
        Shutdown and close all connections in .cxes
        """
        for ca in self.cxes:
            self.shutcloseCx(ca)

    def receive(self, cs):
        """
        Perform non blocking receive from connected socket cs

        If no data then returns None
        If connection closed then returns ''
        Otherwise returns data
        """
        try:
            data = cs.recv(self.bs)
            message = ("Server at {0} received from {1}, {2}\n".format(
                        str(cs.getsockname()), str(cs.getpeername(), data)))
            console.profuse(message)
            if self.log and self.rxLog:
                self.rxLog.write("%s\n%s\n" % (str(cs.getpeername()), repr(data)))
            return data

        except socket.error as ex:
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return None
            else:
                emsg = ("socket.error = {0}: server at {1} receiving "
                        "from {3} to {2}\n".format(ex,
                                                   self.ha,
                                                   cs.getpeername(),
                                                   cs.getsockname()))
                console.profuse(emsg)
                raise  # re-raise

    def receiveFrom(self, cs):
        """
        If no data then returns (None, sa)
        If connection closed on far side then
            returns ('', sa)
        Otherwise returns (data, ca)

        Where sa is source socket ha
        """
        return (self.receive(cs), cs.getpeername())

    def receiveCx(self, ca):
        """
        Perform non blocking read on connected socket indexed
        by ca (host, port).

        If no data then returns None
        If connection closed on far side then returns ''
        Otherwise returns data
        """
        cs = self.cxes.get(ca)
        if not cs:
            raise ValueError("Host '{0}' not connected.\n".format(str(ca)))
        return(self.receive(cs))

    def receiveFromCx(self, ca):
        """
        Perform non blocking read on connected socket indexed
        by ca (host, port).

        If no data then returns (None, sa)
        If connection closed on far side then
            returns ('', sa)
        Otherwise returns tuple of form (data, sa)

        Where sa is source socket ha
        """
        cs = self.cxes.get(ca)
        if not cs:
            raise ValueError("Host '{0}' not connected.\n".format(str(ca)))
        return (self.receiveFrom(cs))

    def receiveAll(self):
        """
        Attempt nonblocking receive all all clients.
        Returns list of duples of receptions
        """
        receptions = []
        for ca in self.cxes:
            data, sa = self.receiveCx(ca)
            if data:
                receptions.append((data, sa))
        return receptions

    def receiveAny(self):
        """
        Receive from any connected sockets that have data using select
        """
        receptions = []
        return receptions


    def send(self, data, cs):
        """
        Perform non blocking send on connected socket cs.
        Return number of bytes sent

        data is string in python2 and bytes in python3
        """
        try:
            result = cs.send(data) #result is number of bytes sent
        except socket.error as ex:
            emsg = ("socket.error = {0}: server at {1} sending to {2} "
                    "from {3}\n".format(ex,
                                        self.ha,
                                        cs.getpeername(),
                                        cs.getsockname() ))
            console.profuse(emsg)
            #result = 0
            raise

        console.profuse("Server at {0} sent to {1}, {2} "
                        "bytes\n".format(str(self.ha),
                                         str(cs.getpeername()),
                                        result))

        if self.log and self.txLog:
            self.txLog.write("%s %s bytes\n%s\n" %
                             (str(cs.getpeername()), str(result), repr(data)))

        return result

    def sendCx(self, data, ca):
        """
        Perform non blocking send on virtual connected socket indexed by ca.

        data is string in python2 and bytes in python3
        """
        cs = self.cxes.get(ca)
        if not cs:
            raise ValueError("Host '{0}' not connected.\n".format(str(ca)))

        return (self.send(data, cs))

    def serviceAx(self):
        """
        Service any accept requests
        """
        done = False
        while not done:
            cs, ca = self.accept()
            if not cs:
                done = True

    def service(self):
        """
        Service any accept requests and any connection attempts
        """
        pass

    def serviceAny(self):
        """
        Service any accept requests, connection attempts, or receives using select
        """
        pass




class SocketTcpNb(object):
    """Class to manage non blocking io on TCP socket.

       Opens non blocking socket
       Use instance method close to close socket

       Needs socket module
    """

    def __init__(self, ha=None, host='', port=56000, bufsize=1024,
                 path='', log=False):
        """Initialization method for instance.

           ha = host address duple (host, port)
           host = '' equivalant to any interface on host
           port = socket port
           bufsize = buffer size
           path = path to log directory
           log = boolean flag, creates logs if True
        """
        self.ha = ha or (host,port) #ha = host address
        self.bs = bufsize
        self.ss = None  # own socket needs to be opened
        self.yets = odict()  # keys are ha (duples), values sockets in connection process
        self.peers = odict()  # keys are ha (duples), values are connected sockets

        self.path = path #path to directory where log files go must end in /
        self.txLog = None #transmit log
        self.rxLog = None #receive log
        self.log = log

    def openLogs(self, path = ''):
        """Open log files

        """
        date = time.strftime('%Y%m%d_%H%M%S',time.gmtime(time.time()))
        name = "%s%s_%s_%s_tx.txt" % (self.path, self.ha[0], str(self.ha[1]), date)
        try:
            self.txLog = open(name, 'w+')
        except IOError:
            self.txLog = None
            self.log = False
            return False
        name = "%s%s_%s_%s_rx.txt" % (self.path, self.ha[0], str(self.ha[1]), date)
        try:
            self.rxLog = open(name, 'w+')
        except IOError:
            self.rxLog = None
            self.log = False
            return False

        return True

    def closeLogs(self):
        """Close log files

        """
        if self.txLog and not self.txLog.closed:
            self.txLog.close()
        if self.rxLog and not self.rxLog.closed:
            self.rxLog.close()

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
        """Opens listen socket in non blocking mode.

           if socket not closed properly, binding socket gets error
              socket.error: (48, 'Address already in use')
        """
        #create socket ss = server socket
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # make socket address reusable. doesn't seem to have an effect.
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in
        # TIME_WAIT state, without waiting for its natural timeout to expire.
        self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Linux TCP allocates twice the requested size so get size is twice the set size
        if sys.platform.startswith('linux'):
            bs = 2 * self.bs
        else:
            bs = self.bs
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) < bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bs)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bs)
        self.ss.setblocking(0) #non blocking socket

        # TCP connection Server
        try:  # bind to listen socket host address port to receive connections
            self.ss.bind(self.ha)
            self.ss.listen(5)
        except socket.error as ex:
            console.terse("socket.error = {0}\n".format(ex))
            return False

        self.ha = self.ss.getsockname() #get resolved ha after bind

        if self.log:
            if not self.openLogs():
                return False

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

        self.closeLogs()

    def closeAll(self):
        """
        Closes listen socket and all connections
        """
        self.close()
        for ca in self.peers:
            self.unconnectPeer(ca)
        for ca in self.yets:
            self.unconnectYet(ca)

    def accept(self):
        """
        Accept any pending connections
        """
        # accept new virtual connected socket created from server socket
        try:
            cs, ca = self.ss.accept()  # virtual connection (socket, host address)
        except socket.error as ex:
            if ex.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                emsg = ("socket.error = {0}: server at {1} while "
                        "accepting \n".format(ex, self.ha))
                console.profuse(emsg)
                raise #re raise exception
            return False
        if ca not in self.peers:  # may have simultaneous connection
            self.peers[ca] = cs
        else:
            self.closeshut(cs)

        return True

    def connect(self, ca):
        """
        Create a connection to ca
        """
        if ca in self.peers:  # use
            raise ValueError("Attempt to connect to peer socket {0}. "
                             "Use reconnect instead.".format(ca))

        if ca in self.yets:
            cs = self.yets[ca]
        else:  # ca not in self.yets or ca not in self.peers:
            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # make socket address reusable. doesn't seem to have an effect.
            # the SO_REUSEADDR flag tells the kernel to reuse a local socket in
            # TIME_WAIT state, without waiting for its natural timeout to expire.
            cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Linux TCP allocates twice the requested size so get size is twice the set size
            if sys.platform.startswith('linux'):
                bs = 2 * self.bs
            else:
                bs = self.bs
            if cs.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) < bs:
                cs.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bs)
            if cs.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < bs:
                cs.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bs)
            cs.setblocking(0) #non blocking socket
            self.yets[ca] = cs

        try:
            result = cs.connect_ex(ca)  # async connect
        except socket.error as ex:
            console.terse("socket.error = {0}\n".format(ex))
            raise

        # now has new virtual port and ca != cs.getsockname()

        if result not in [0, errno.EISCONN]:  # not yet connected
            return False

        if ca in self.yets:
            del self.yets[ca]
        if ca not in self.peers:  # may have a simultaneous connection
            self.peers[ca] = cs  # successfully connected
        else:
            self.closeshut(cs)
        return True

    def reconnectPeer(self, ca):
        """
        Idempotently reconnects peer socket or makes new connection
        """
        self.unconnectPeer(ca)
        return self.connect(ca)

    @staticmethod
    def closeshut(cs):
        """
        Shutdown and close connected socket cs
        """
        if cs:
            try:
                cs.shutdown(socket.SHUT_RDWR)  # shutdown socket
            except socket.error as ex:
                #console.terse("socket.error = {0}\n".format(ex))
                pass
            cs.close()  #close socket

    def unconnectPeer(self, ca):
        """
        Shutdown and close connected socket peer given by ca
        """
        if ca in self.peers:
            cs = self.peers[ca]
            self.closeshut(cs)
            del self.peers[ca]

    def unconnectYet(self, ca):
        """
        Shutdown and close connected socket yet given by ca
        """
        if ca in self.yets:
            cs = self.yets[ca]
            self.closeshut(cs)
            del self.yets[ca]


    def service(self):
        """
        Service any accept requests and any connection attempts
        """
        while self.accept():
            pass

        for ca in self.yets:
            self.connect(ca)

    def serviceAny(self):
        """
        Service any accept requests, connection attempts, or receives using select
        """
        pass

    def receiveAny(self):
        """
        Receive from any connected sockets that have data using select
        """
        receptions = []
        return receptions

    def receiveAll(self):
        """
        Attempt nonblocking receive all all peers.
        Returns list of duples of receptions
        """
        receptions = []
        for ca in self.peers:
            data, ca = self.receive(ca)
            if data:
                receptions.append((data, ca))
        return receptions

    def receive(self, ca, bs=None):
        """
        Perform non blocking read on connected socket with by ca (connected address).

        returns tuple of form (data, sa)
        if no data then returns ('',None)
        but always returns a tuple with two elements
        """
        cs = self.peers.get(ca)
        if not cs:
            raise ValueError("Host '{0}' not connected.\n".format(str(ca)))

        if not bs:
            bs = self.bs

        try:
            data = cs.recv(bs)

            message = "Server at {0} received {1} from {2}\n".format(
                str(self.ha), data, str(ca))
            console.profuse(message)

            if self.log and self.rxLog:
                self.rxLog.write("%s\n%s\n" % (str(ca), repr(data)))
            return (data, ca)

        except socket.error as ex: # 2.6 socket.error is subclass of IOError
            # Some OSes define errno differently so check for both
            if ex.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                return ('', None) #receive has nothing empty string for data
            else:
                emsg = ("socket.error = {0}: server at {1} receiving "
                                    "on {2}\n".format(ex, self.ha, ca))
                console.profuse(emsg)
                raise #re raise exception ex1

    def send(self, data, ca):
        """
        Perform non blocking send on virtual connected socket indexed by ca.

        data is string in python2 and bytes in python3
        da is destination address tuple (destHost, destPort)
        """
        cs = self.peers.get(ca)
        if not cs:
            raise ValueError("Host '{0}' not connected.\n".format(str(ca)))

        try:
            result = cs.send(data) #result is number of bytes sent
        except socket.error as ex:
            emsg = "socket.error = {0}: sending from {1} to {2}\n".format(ex, self.ha, ca)
            console.profuse(emsg)
            result = 0
            raise

        console.profuse("Server at {0} sent {1} bytes\n".format(str(self.ha), result))

        if self.log and self.txLog:
            self.txLog.write("%s %s bytes\n%s\n" %
                             (str(ca), str(result), repr(data)))

        return result
