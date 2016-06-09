"""
Device Base Package

"""
from __future__ import absolute_import, division, print_function

import struct
from binascii import hexlify
from collections import deque, namedtuple
import enum
import socket

from ...aid.sixing import *
from ...aid.odicting import odict
from ...aid.byting import bytify, unbytify, packify, unpackify
from ...aid.eventing import eventify, tagify
from ...aid import getConsole
from .protoing import MixIn

console = getConsole()

class Device(MixIn):
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

    def receive(self, rx):
        """
        Process received rx msg/pkt/data.
        """
        pass

class LocalDevice(Device):
    """
    Local Device Class
    """
    def __init__(self,
                 stack,
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
        super(LocalDevice, self).__init__(stack=stack, **kwa)


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


class SingleRemoteDevice(Device):
    """
    Remote Device Class when only one remote in stack .remote
    Affects how uid is assigned
    """
    def __init__(self,
                 stack,
                 uid=None,
                 uids=None,
                 **kwa):
        """
        Initialization method for instance

        Inherited Parameters:
            stack is Stack managing this device required
            name is user friendly name of device
            uid  is unique device id
            ha is device host address
            kind is type of device

        Parameters:
            uids is sequence or set of used uids to not use for remote if uid not provided

        Inherited Attributes:
            .stack is Stack managing this device required
            .name is user friendly name of device
            .uid  is unique device id per channel or site
            .ha is device host address
            .kind is type of device

        Attributes:
            .uids is sequence or set of used uids to not use for remote if uid not provided

        """
        if uid is None:
            uids = set(uids) if uids is not None else set()
            if hasattr(stack, 'local'):
                uids.add(stack.local.uid)
            uid = stack.nextUid()
            while uid in uids:
                uid = stack.nextUid()

        super(SingleRemoteDevice, self).__init__(stack=stack, uid=uid, **kwa)


class IpDevice(Device):
    """
    IP device
    """

    def __init__(self,
                 stack,
                 ha=None,
                 **kwa):
        """
        Initialization method for instance

        Inherited Parameters:
            stack is Stack managing this device required
            name is user friendly name of device
            uid  is unique device id
            ha is device  udp host address, a duple (host,port)
            kind is type of device

        Parameters:


        Inherited Attributes:
            .stack is Stack managing this device required
            .name is user friendly name of device
            .uid  is unique device id per channel or site
            .ha is device udp host address, a duple (host,port)
            .kind is type of device

        Attributes:

        """
        if ha:
            host, port = ha
            host = socket.gethostbyname(host)
            if host in ['0.0.0.0', '']:
                host = '127.0.0.1'
            ha = (host, port)
        else:
            ha = ('127.0.0.1', stack.Port)

        super().__init__(stack=stack, ha=ha, **kwa)

    @property
    def host(self):
        """
        Property that returns host of local interface ha duple (host, port)
        """
        return self.ha[0]

    @host.setter
    def host(self, value):
        """
        Setter for host property
        """
        host, port = self.local.ha
        self.local.ha = (value, port)

    @property
    def port(self):
        """
        Property that returns host of local interface ha duple (host, port)
        """
        return self.ha[1]

    @port.setter
    def port(self, value):
        """
        Setter for host property
        """
        host, port = self.local.ha
        self.local.ha = (host, value)


class IpLocalDevice(IpDevice, LocalDevice):
    """
    Ip LocalDevice
    """
    def __init__(self,
                 stack,
                 **kwa):
        """
        Initialization method for instance

        Inherited Parameters:
            stack is Stack managing this device required
            name is user friendly name of device
            uid  is unique device id
            ha is device udp host address, a duple (host,port)
            kind is type of device

        Parameters:


        Inherited Attributes:
            .stack is Stack managing this device required
            .name is user friendly name of device
            .uid  is unique device id per channel or site
            .ha is device udp host address, a duple (host,port)
            .kind is type of device

        Attributes:

        """
        super().__init__(stack=stack, **kwa)


class IpRemoteDevice(IpDevice, RemoteDevice):
    """
    Ip remote device
    """

    def __init__(self,
                 stack,
                 **kwa):
        """
        Initialization method for instance

        Inherited Parameters:
            stack is Stack managing this device required
            name is user friendly name of device
            uid  is unique device id
            ha is device udp host address, a duple (host,port)
            kind is type of device

        Parameters:


        Inherited Attributes:
            .stack is Stack managing this device required
            .name is user friendly name of device
            .uid  is unique device id per channel or site
            .ha is device udp host address, a duple (host,port)
            .kind is type of device

        Attributes:

        """
        super().__init__(stack=stack, **kwa)


class IpSingleRemoteDevice(IpDevice, SingleRemoteDevice):
    """
    Ip Single Remote Device Class when only one remote in stack .remote
    Affects how uid is assigned
    """

    def __init__(self,
                 stack,
                 **kwa):
        """
        Initialization method for instance

        Inherited Parameters:
            stack is Stack managing this device required
            name is user friendly name of device
            uid  is unique device id
            ha is device udp host address, a duple (host,port)
            kind is type of device

        Parameters:


        Inherited Attributes:
            .stack is Stack managing this device required
            .name is user friendly name of device
            .uid  is unique device id per channel or site
            .ha is device udp host address, a duple (host,port)
            .kind is type of device

        Attributes:

        """
        super().__init__(stack=stack, **kwa)
