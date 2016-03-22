"""
Device Base Package

"""
from __future__ import absolute_import, division, print_function

import struct
from binascii import hexlify
from collections import deque, namedtuple
import enum

from ioflo.aid.sixing import *
from ioflo.aid.odicting import odict
from ioflo.aid.byting import bytify, unbytify, packify, unpackify
from ioflo.aid.eventing import eventify, tagify
from ioflo.aid import getConsole

console = getConsole()


class Device(object):
    """
    Device Class
    """
    def __init__(self,
                 stack,
                 uid=None,
                 name=None,
                 ha=None,
                 kind=0,
                 exchanger=None,
                 exchangent=None,
                 ):
        """
        Initialization method for instance

        Parameters:
            stack is Stack managing this device required
            name is user friendly name of device
            uid  is unique device id
            ha is device host address
            kind is type of device
            exchanger is Exchanger instance of current exchange with this device
            exchangent is Exchangent instance of correspondent exchange with this device

        Attributes:
            .stack is Stack managing this device required
            .name is user friendly name of device
            .uid  is unique device id per channel or site
            .ha is device host address
            .kind is type of device
            .exchanger is Exchanger instance of initiated exchange with this device
            .exchangent is Exchangent instance of correspondent exchange with this device

        """
        self.stack = stack
        self.uid = uid if uid is not None else stack.nextUid()
        self.name = name if name is not None else "Device{0}".format(self.uid)
        self.ha = ha
        self.kind = kind
        self.exchanger = exchanger
        self.exchangent = exchangent

    def show(self):
        """
        Display device data
        """
        result = ("Device: name={0} uid={1} ha={2} kind={3}\n".format(
                    self.name,
                    self.uid,
                    self.ha,
                    self.kind))
        return result

    def process(self):
        '''
        Call .process on .exchanger .exchangent to allow timer based processing
        '''
        if self.exchanger:
            self.exchanger.process()

        if self.exchangent:
            self.exchangent.process()

    def receive(self, msg):
        """
        Process received msg.
        """
        if self.exchanger:
            self.exchanger.receive(msg)

        elif self.exchangent:
            self.exchangent.receive(msg)

class LocalDevice(Device):
    """
    Local Device Class
    """
    def __init__(self,
                 stack,
                 uid=None,
                 **kwa):
        """
        Initialization method for instance

        Assumes local device in stack is created before any remotes are added
        """
        uid = uid if uid is not None else stack.nextUid()
        super(LocalDevice, self).__init__(stack=stack, uid=uid, **kwa)


class RemoteDevice(Device):
    """
    Remote Device Class
    """
    def __init__(self,
                 stack,
                 uid=None,
                 **kwa):
        """
        Initialization method for instance
        """
        if uid is None:
            uid = stack.nextUid()
            while uid in stack.remotes or uid in (stack.local.uid,):
                uid = stack.nextUid()

        super(RemoteDevice, self).__init__(stack=stack, uid=uid, **kwa)



