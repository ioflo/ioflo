"""
uxd async io (nonblocking) module

"""
from __future__ import absolute_import, division, print_function

import sys
import os
import socket
import errno
from binascii import hexlify

# Import ioflo libs
from ...aid.sixing import *
from ...aid.consoling import getConsole

console = getConsole()

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
        self.opened = True
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
            self.opened = False

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
            # ex.args[0] is always ex.errno for better compat
            if ex.args[0]  in (errno.EAGAIN, errno.EWOULDBLOCK):
                return (b'', None) #receive has nothing empty string for data
            else:
                emsg = "socket.error = {0}: receiving at {1}\n".format(ex, self.ha)
                console.profuse(emsg)
                raise #re raise exception ex1

        if console._verbosity >= console.Wordage.profuse:  # faster to check
            try:
                load = data.decode("UTF-8")
            except UnicodeDecodeError as ex:
                load = "0x{0}".format(hexlify(data).decode("ASCII"))
            cmsg = ("Server at {0}, received from {1}:\n------------\n"
                    "{2}\n\n".format(self.ha, sa, load))
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
            try:
                load = data[:result].decode("UTF-8")
            except UnicodeDecodeError as ex:
                load = "0x{0}".format(hexlify(data[:result]).decode("ASCII"))
            cmsg = ("Server at {0}, sent {1} bytes to {2}:\n------------\n"
                    "{3}\n\n".format(self.ha, result, da, load))
            console.profuse(cmsg)

        if self.wlog:
            self.wlog.writeTx(da, data)

        return result


PeerUxd = SocketUxdNb  # alias
