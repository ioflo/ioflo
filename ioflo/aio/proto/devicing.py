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
                 kind=None,
                 ):
        """
        Initialization method for instance

        Parameters:
            stack is Stack managing this device required
            name is user friendly name of device
            uid  is unique device id
            ha is device host address
            kind is type of device

        Attributes:
            .stack is Stack managing this device required
            .name is user friendly name of device
            .uid  is unique device id per channel or site
            .ha is device host address
            .kind is type of device

        """
        self.stack = stack
        self.uid = uid if uid is not None else stack.nextUid()
        self.name = name if name is not None else "Device{0}".format(self.uid)
        self.ha = ha if ha is not None else ''
        self.kind = kind

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
        """
        Timer based processing
        """
        pass

    def receive(self, msg):
        """
        Process received msg.
        """
        pass

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
        
        Inherited Parameters:
            stack is Stack managing this device required
            name is user friendly name of device
            uid  is unique device id
            ha is device host address
            kind is type of device

        Inherited Attributes:
            .stack is Stack managing this device required
            .name is user friendly name of device
            .uid  is unique device id per channel or site
            .ha is device host address
            .kind is type of device
            
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
        
        Inherited Parameters:
            stack is Stack managing this device required
            name is user friendly name of device
            uid  is unique device id
            ha is device host address
            kind is type of device

        Inherited Attributes:
            .stack is Stack managing this device required
            .name is user friendly name of device
            .uid  is unique device id per channel or site
            .ha is device host address
            .kind is type of device
            
        """
        if uid is None:
            uid = stack.nextUid()
            while uid in stack.remotes or uid in (stack.local.uid,):
                uid = stack.nextUid()

        super(RemoteDevice, self).__init__(stack=stack, uid=uid, **kwa)



