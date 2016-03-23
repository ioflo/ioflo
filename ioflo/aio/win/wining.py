"""
windows mailslog async io (nonblocking)

"""
from __future__ import absolute_import, division, print_function

import sys
import os

try:
    import win32file
except ImportError:
    pass

# Import ioflo libs
from ...aid.sixing import *
from ...aid.consoling import getConsole

console = getConsole()


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
        self.opened = False

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

        self.opened = True
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
            self.opened = False

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


PeerWms =WinMailslotNb
