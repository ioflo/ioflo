"""
nonblocking.py

"""
#print("module {0}".format(__name__))

from __future__ import division


import sys
import os
import socket
import errno

try:
    import win32file
except ImportError:
    pass

# Import ioflo libs
from .globaling import *
from .odicting import odict
from . import excepting

from .consoling import getConsole
console = getConsole()


class SerialNB(object):
    """ Class to manage non blocking io on serial port.

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
        """ Opens fd on serial port in non blocking mode.

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

class ConsoleNB(object):
    """Class to manage non blocking io on console.

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
        """Opens fd on terminal console in non blocking mode.

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

class SocketUdpNb(object):
    """Class to manage non blocking io on UDP socket.

       Opens non blocking socket
       Use instance method close to close socket

       Needs socket module
    """

    def __init__(self, ha=None, host = '', port = 55000, bufsize = 1024,
                 path = '', log = False):
        """Initialization method for instance.

           ha = host address duple (host, port)
           host = '' equivalant to any interface on host
           port = socket port
           bs = buffer size
        """
        self.ha = ha or (host,port) #ha = host address
        self.bs = bufsize
        self.ss = None #server's socket needs to be opened

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

    def open(self):
        """Opens socket in non blocking mode.

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

        if self.log:
            if not self.openLogs():
                return False

        return True

    def reopen(self):
        """     """
        self.close()
        return self.open()

    def close(self):
        """Closes  socket.

        """
        if self.ss:
            self.ss.close() #close socket
            self.ss = None

        self.closeLogs()

    def receive(self):
        """Perform non blocking read on  socket.

           returns tuple of form (data, sa)
           if no data then returns ('',None)
           but always returns a tuple with two elements
        """
        try:
            #sa = source address tuple (sourcehost, sourceport)
            data, sa = self.ss.recvfrom(self.bs)

            message = "Server at {0} received {1} from {2}\n".format(
                str(self.ha),data, str(sa))
            console.profuse(message)

            if self.log and self.rxLog:
                self.rxLog.write("%s\n%s\n" % (str(sa), repr(data)))

            return (data,sa)
        except socket.error as ex: # 2.6 socket.error is subclass of IOError
            # Some OSes define errno differently so check for both
            if ex.errno == errno.EAGAIN or ex.errno == errno.EWOULDBLOCK:
                return ('',None) #receive has nothing empty string for data
            else:
                emsg = "socket.error = {0}: receiving at {1}\n".format(ex, self.ha)
                console.profuse(emsg)
                raise #re raise exception ex1

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

        console.profuse("Server at {0} sent {1} bytes\n".format(str(self.ha), result))

        if self.log and self.txLog:
            self.txLog.write("%s %s bytes\n%s\n" %
                             (str(da), str(result), repr(data)))

        return result

class SocketUxdNb(object):
    """Class to manage non blocking io on UXD (unix domain) socket.

       Opens non blocking socket
       Use instance method close to close socket

       Needs socket module
    """

    def __init__(self, ha=None, bufsize = 1024, path = '', log = False, umask=None):
        """Initialization method for instance.

           ha = host address duple (host, port)
           host = '' equivalant to any interface on host
           port = socket port
           bs = buffer size
        """
        self.ha = ha # uxd host address string name
        self.bs = bufsize
        self.ss = None #server's socket needs to be opened

        self.path = path #path to directory where log files go must end in /
        self.txLog = None #transmit log
        self.rxLog = None #receive log
        self.log = log
        self.umask = umask

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

    def open(self):
        """Opens socket in non blocking mode.

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

        if self.log:
            if not self.openLogs():
                return False

        return True

    def reopen(self):
        """     """
        self.close()
        return self.open()

    def close(self):
        """Closes  socket.

        """
        if self.ss:
            self.ss.close() #close socket
            self.ss = None

        try:
            os.unlink(self.ha)
        except OSError:
            if os.path.exists(self.ha):
                raise

        self.closeLogs()

    def receive(self):
        """Perform non blocking read on  socket.

           returns tuple of form (data, sa)
           if no data then returns ('',None)
           but always returns a tuple with two elements
        """
        try:
            #sa = source address tuple (sourcehost, sourceport)
            data, sa = self.ss.recvfrom(self.bs)

            message = "Server at {0} received {1} from {2}\n".format(
                str(self.ha),data, str(sa))
            console.profuse(message)

            if self.log and self.rxLog:
                self.rxLog.write("%s\n%s\n" % (str(sa), repr(data)))

            return (data, sa)
        except socket.error as ex: # 2.6 socket.error is subclass of IOError
            if ex.errno == errno.EAGAIN: #Resource temporarily unavailable on os x
                return ('', None) #receive has nothing empty string for data
            else:
                emsg = "socket.error = {0}: receiving at {1}\n".format(ex, self.ha)
                console.profuse(emsg)
                raise #re raise exception ex1

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

        console.profuse("Server at {0} sent {1} bytes\n".format(str(self.ha), result))

        if self.log and self.txLog:
            self.txLog.write("%s %s bytes\n%s\n" %
                             (str(da), str(result), repr(data)))

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
            return ('', None)

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
        self.peers = odict()  # keys are ha (duples) values are connected sockets

        self.path = path #path to directory where log files go must end in /
        self.txLog = None #transmit log
        self.rxLog = None #receive log
        self.log = log
        self.client = client

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

    def open(self):
        """Opens socket in non blocking mode.

           if socket not closed properly, binding socket gets error
              socket.error: (48, 'Address already in use')
        """
        #create socket ss = server socket
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # make socket address reusable. doesn't seem to have an effect.
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in
        # TIME_WAIT state, without waiting for its natural timeout to expire.
        self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) <  self.bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bs)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < self.bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bs)
        self.ss.setblocking(0) #non blocking socket

        # TCP connection Server
        try:  # bind to host address port to receive connections
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
        Idempotently opens socket
        """
        self.close()
        return self.open()

    def close(self):
        """
        Closes socket.
        """
        if self.ss:
            self.ss.shutdown(socket.SHUT_RDWR)  # shutdown socket
            self.ss.close()  #close socket
            self.ss = None

        self.closeLogs()

    def connect(ca):
        """
        Create a connection to ca
        """
        if ca not in self.peers or not self.peers[ca]:
            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # make socket address reusable. doesn't seem to have an effect.
            # the SO_REUSEADDR flag tells the kernel to reuse a local socket in
            # TIME_WAIT state, without waiting for its natural timeout to expire.
            cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if cs.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) <  self.bs:
                cs.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bs)
            if cs.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < self.bs:
                cs.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bs)
            cs.setblocking(0) #non blocking socket

            try:
                cs.connect(ca)
            except socket.error as ex:
                console.terse("socket.error = {0}\n".format(ex))
                return False

            ca = cs.getsockname() #get resolved ca after connection
            self.peers[ca] = cs

        return True

    def reconnect(ca):
        """
        Idempotently reconnects socket
        """
        if ca not in self.peers:
            return self.connect(ca)

        cs = self.peers[ca]
        if not cs:
            cs.shutdown(socket.SHUT_RDWR)  # shutdown socket
            cs.close()  #close socket
            self.peers[ca] = None

        return self.connect(ca)

    def accept():
        """
        Accept any pending connections
        """
        # accept new connected socket created from server socket
        cs, ca = self.ss.accept()  # duple of connected (socket, host address)
        while cs: # keep accepting until no more to accept
            self.peers[ca] = cs
            cs, ca = self.ss.accept()

    def receiveAny(self):
        """
        Select and receive from any connected sockets that have data
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

    def receive(self, ca):
        """
        Perform non blocking read on connected socket with by ca (connected address).

        returns tuple of form (data, sa)
        if no data then returns ('',None)
        but always returns a tuple with two elements
        """
        cs = self.peers.get(ca)
        if not cs:
            raise ValueError("Host '{0}' not connected.\n".format(str(ca)))

        try:
            data = cs.recv(self.bs)

            message = "Server at {0} received {1} from {2}\n".format(
                str(self.ha), data, str(ca))
            console.profuse(message)

            if self.log and self.rxLog:
                self.rxLog.write("%s\n%s\n" % (str(ca), repr(data)))
            return (data, ca)

        except socket.error as ex: # 2.6 socket.error is subclass of IOError
            # Some OSes define errno differently so check for both
            if ex.errno == errno.EAGAIN or ex.errno == errno.EWOULDBLOCK:
                return ('', None) #receive has nothing empty string for data
            else:
                emsg = ("socket.error = {0}: server at {1} receiving "
                                    "on {2}\n".format(ex, self.ha, ca))
                console.profuse(emsg)
                raise #re raise exception ex1

    def send(self, data, ca):
        """
        Perform non blocking send on  socket to ca.

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

class SocketTcpClientNb(object):
    """Class to manage non blocking IO on TCP socket.

       Opens non blocking socket as client only
       Use instance method close to close socket

       Needs socket module
    """

    def __init__(self, ha=None, host='', port=56000, bufsize=1024,
                 path='', log=False):
        """Initialization method for instance.

           ha = host address duple (host, port) or server
           host = '' equivalant to any interface on host
           port = socket port
           bufsize = buffer size
           path = path to log directory
           log = boolean flag, creates logs if True
        """
        self.ha = ha or (host,port)  # ha = host address of server
        self.bs = bufsize
        self.ss = None #server's socket needs to be opened

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

    def open(self):
        """Opens socket in non blocking mode.

           if socket not closed properly, binding socket gets error
              socket.error: (48, 'Address already in use')
        """
        #create socket ss = server socket
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # make socket address reusable. doesn't seem to have an effect.
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in
        # TIME_WAIT state, without waiting for its natural timeout to expire.
        self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) <  self.bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bs)
        if self.ss.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < self.bs:
            self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bs)
        self.ss.setblocking(0) #non blocking socket

        try: # TCP Client only
            self.ss.connect(self.ha)
        except socket.error as ex:
            console.terse("socket.error = {0}\n".format(ex))
            return False

        self.ha = self.ss.getsockname() #get resolved ha after connection

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

    def close(self):
        """
        Closes socket.
        """
        if self.ss:
            self.ss.shutdown()  # shutdown socket
            self.ss.close()  #close socket
            self.ss = None

        self.closeLogs()

    def accept():
        """
        Accept any pending connections
        """
        pass

    def receive(self):
        """
        Perform non blocking read on  socket.

        returns tuple of form (data, sa)
        if no data then returns ('',None)
        but always returns a tuple with two elements
        """
        try:
            # sa = source address tuple (sourcehost, sourceport)
            data, sa = self.ss.recv(self.bs)

            message = "Server at {0} received {1} from {2}\n".format(
                str(self.ha),data, str(sa))
            console.profuse(message)

            if self.log and self.rxLog:
                self.rxLog.write("%s\n%s\n" % (str(sa), repr(data)))

            return (data,sa)
        except socket.error as ex: # 2.6 socket.error is subclass of IOError
            # Some OSes define errno differently so check for both
            if ex.errno == errno.EAGAIN or ex.errno == errno.EWOULDBLOCK:
                return ('',None) #receive has nothing empty string for data
            else:
                emsg = "socket.error = {0}: receiving at {1}\n".format(ex, self.ha)
                console.profuse(emsg)
                raise #re raise exception ex1

    def send(self, data):
        """
        Perform non blocking send on  socket.

        data is string in python2 and bytes in python3
        da is destination address tuple (destHost, destPort)
        """
        try:
            result = self.ss.send(data) #result is number of bytes sent
        except socket.error as ex:
            emsg = "socket.error = {0}: sending from {1} to {2}\n".format(ex, self.ha, da)
            console.profuse(emsg)
            result = 0
            raise

        console.profuse("Server at {0} sent {1} bytes\n".format(str(self.ha), result))

        if self.log and self.txLog:
            self.txLog.write("%s %s bytes\n%s\n" %
                             (str(da), str(result), repr(data)))

        return result

