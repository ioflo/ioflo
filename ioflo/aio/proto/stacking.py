"""
Stack Interface Package

"""
from __future__ import absolute_import, division, print_function

import struct
from binascii import hexlify
from collections import deque
import enum
import time
import random
import errno
import socket

from ...aid.sixing import *
from ...aid.odicting import odict
from ...aid.byting import bytify, unbytify, packify, unpackify
from ...aid.eventing import eventify, tagify
from ...aid.timing import tuuid, Stamper, StoreTimer
from ...aid import getConsole
from ..udp import udping
from .protoing import MixIn
from . import devicing, packeting


console = getConsole()


class Stack(MixIn):
    """
    Base stack object.
    Should be subclassed for specific transport type
    """
    Uid = 0  # base for next unique id for local and remotes

    def __init__(self,
                 stamper=None,
                 version=None,
                 puid=None,
                 local=None,
                 uid=None,
                 name=None,
                 ha=None,
                 kind=None,
                 server=None,
                 rxbs=None,
                 rxPkts=None,
                 rxMsgs=None,
                 txbs=None,
                 txPkts=None,
                 txMsgs=None,
                 remotes=None,
                 nameRemotes=None,
                 haRemotes=None,
                 stats=None,
                 **kwa
                ):
        """
        Setup Stack instance

        Inherited Parameters:


        Parameters:
            stamper is relative time stamper for this stack
            version is version tuple or string for this stack
            puid is previous uid for devices managed by this stack
            local is local device created by subclass takes precedence
            uid is uid of local device shared with stack if local not given
            name is name of local device shared with stack if local not given
            ha is host address of local device shared with stack if local not given
            kind is kind of local device shared with stack if local not given
            server is interface server if any
            rxbs is bytearray buffer to hold rx data stream if any
            rxPkts is deque to hold received packet if any
            rxMsgs is deque to hold received msgs if any
            txbs is bytearray buffer to hold rx data stream if any
            txPkts is deque to hold packet to be transmitted if any
            txMsgs is deque to hold messages to be transmitted if any
            remotes is odict to hold remotes keyed by uid if any
            nameRemotes is odict to hold remotes keyed by name if any
            haRemotes is odict to remotes keyed by ha if any
            stats is odict of stack statistics if any

        Inherited Attributes:

        Attributes:
            .stamper is relative time stamper for this stack
            .version is version tuple or string for this stack
            .puid is previous uid for devices managed by this stack
            .local is local device for this stack
            .server is interface server if any
            .rxbs is bytearray buffer to hold input data stream
            .rxPkts is deque of duples to hold received packets
            .rxMsgs is deque of duples to hold received msgs and remotes
            .txbs is bytearray buffer to hold rx data stream if any
            .txPkts is deque of duples to hold packets to be transmitted
            .txMsgs is deque of duples to hold messages to be transmitted
            .remotes is odict of remotes indexed by uid
            .uidRemotes is alias for .remotes
            .nameRemotes = odict  of remotes indexed by name
            .haRemotes = odict of remotes indexed by ha
            .stats is odict of stack statistics
            .statTimer is relative timer for statistics
            .aha is server accepting (listening) host address for .server

        Inherited Properties:

        Properties:
            .uid is local device unique id as stack uid
            .name is local device name as stack name
            .ha  is local device ha as stack ha
            .kind is local device kind as stack kind

        """
        super(Stack, self).__init__(**kwa)

        self.stamper = stamper or Stamper(stamp=0.0)
        self.version = version

        if getattr(self, 'aha', None) is None:  # allows subclass override
            self.aha = ha if ha is not None else ''

        if getattr(self, 'puid', None) is None:  # allows subclass override
            self.puid = puid if puid is not None else self.Uid

        self.local = local if local is not None else devicing.LocalDevice(stack=self,
                                                                          name=name,
                                                                          uid=uid,
                                                                          ha=ha,
                                                                          kind=kind)
        self.local.stack = self  # in case passed up from subclass

        self.remotes = self.uidRemotes = remotes if remotes is not None else odict()
        self.nameRemotes = nameRemotes if nameRemotes is not None else odict()
        self.haRemotes =  haRemotes if haRemotes is not None else odict()

        self.server = server if server is not None else self.createServer(ha=self.aha)

        if self.server:
            if not self.server.reopen():  # open interface
                raise ValueError("Stack '{0}': Failed opening server at"
                            " '{1}'\n".format(self.name, self.server.ha))

            self.aha = self.server.ha  # update local host address after open

            console.verbose("Stack '{0}': Opened server at '{1}'\n".format(self.name,
                                                                           self.aha))
        self.rxbs = rxbs if rxbs is not None else bytearray()
        self.rxPkts = rxPkts if rxPkts is not None else deque()
        self.rxMsgs = rxMsgs if rxMsgs is not None else deque()
        self.txbs = txbs if txbs is not None else bytearray()
        self.txPkts = txPkts if txPkts is not None else deque()
        self.txMsgs = txMsgs if txMsgs is not None else deque()

        self.stats = stats if stats is not None else odict() # udp statistics
        self.statTimer = StoreTimer(self.stamper)


    @property
    def uid(self):
        """
        Property that returns uid of local interface
        """
        return self.local.uid

    @uid.setter
    def uid(self, value):
        """
        Setter for uid property
        """
        self.local.uid = value

    @property
    def name(self):
        """
        Property that returns name of local interface
        """
        return self.local.name

    @name.setter
    def name(self, value):
        """
        Setter for name property
        """
        self.local.name = value

    @property
    def ha(self):
        """
        Property that returns local host address
        """
        return self.local.ha

    @ha.setter
    def ha(self, value):
        """
        Setter for ha property
        """
        self.local.ha = value

    @property
    def kind(self):
        """
        Property that returns local device kind
        """
        return self.local.kind

    @kind.setter
    def kind(self, value):
        """
        Setter for kind property
        """
        self.local.kind = value

    def nextUid(self):
        """
        Generates next unique id number for local or remotes.
        """
        self.puid += 1
        return self.puid

    def createServer(self, ha):
        """
        Create and return server on ha

        ha is the host address of the server
        """
        return None

    def close(self):
        """
        Close server if any
        """
        if self.server:
            self.server.close()
    
    def reopen(self):
        """
        Reopen server if any
        """
        if self.server:
            return self.server.reopen()    

    def addRemote(self, remote):
        """
        Uniquely add a remote to indexes
        """
        if remote.uid in self.uidRemotes or remote.uid in (self.local.uid, ):
            emsg = "Cannot add remote at uid '{0}', alreadys exists.".format(remote.uid)
            raise ValueError(emsg)
        if remote.name in self.nameRemotes or remote.name in (self.local.name, ):
            emsg = "Cannot add remote at name '{0}', alreadys exists.".format(remote.name)
            raise ValueError(emsg)
        if remote.ha in self.haRemotes or remote.ha in (self.local.ha, ):
            emsg = "Cannot add remote at ha '{0}', alreadys exists.".format(remote.ha)
            raise ValueError(emsg)
        remote.stack = self
        self.uidRemotes[remote.uid] = remote
        self.nameRemotes[remote.name] = remote
        self.haRemotes[remote.ha] = remote
        return remote

    def moveRemote(self, remote, new):
        """
        Uniquely move remote at remote.uid to new uid but keep same index
        """
        old = remote.uid
        if new != old:
            if new in self.uidRemotes or new in (self.local.uid, ):
                emsg = "Cannot move, remote to '{0}', already exists.".format(new)
                raise ValueError(emsg)

            if old not in self.uidRemotes:
                emsg = "Cannot move remote at '{0}', does not exist.".format(old)
                raise ValueError(emsg)

            if remote is not self.uidRemotes[old]:
                emsg = "Cannot move remote at '{0}', not identical.".format(old)
                raise ValueError(emsg)

            remote.uid = new
            index = self.uidRemotes.keys().index(old)
            del self.uidRemotes[old]
            self.uidRemotes.insert(index, new, remote)

    def renameRemote(self, remote, new):
        """
        Uniquely rename remote with old remote.name to new name but keep same index
        """
        old = remote.name
        if new != old:
            if new in self.nameRemotes or new in (self.local.name, ):
                emsg = "Cannot rename remote to '{0}', already exists.".format(new)
                raise ValueError(emsg)
            if old not in self.nameRemotes:
                emsg = "Cannot rename remote '{0}', does not exist.".format(old)
                raise ValueError(emsg)
            if remote is not self.nameRemotes[old]:
                emsg = "Cannot rename remote '{0}', not identical.".format(old)
                raise ValueError(emsg)
            remote.name = new
            index = self.nameRemotes.keys().index(old)
            del self.nameRemotes[old]
            self.nameRemotes.insert(index, new, remote)

    def rehaRemote(self, remote, new):
        """
        Uniquely rename remote with old remote.name to new name but keep same index
        """
        old = remote.ha
        if new != old:
            if new in self.haRemotes or new in (self.local.ha, ):
                emsg = "Cannot reha remote to '{0}', already exists.".format(new)
                raise ValueError(emsg)
            if old not in self.haRemotes:
                emsg = "Cannot reha remote '{0}', does not exist.".format(old)
                raise ValueError(emsg)
            if remote is not self.haRemotes[old]:
                emsg = "Cannot reha remote '{0}', not identical.".format(old)
                raise ValueError(emsg)
            remote.ha = new
            index = self.haRemotes.keys().index(old)
            del self.haRemotes[old]
            self.haRemotes.insert(index, new, remote)

    def removeRemote(self, remote):
        """
        Remove remote from all remote indexes
        """
        if remote.uid not in self.uidRemotes:
            emsg = "Cannot remove remote '{0}', does not exist.".format(remote.uid)
            raise ValueError(emsg)
        if remote is not self.uidRemotes[remote.uid]:
            emsg = "Cannot remove remote '{0}', not identical.".format(uid)
            raise ValueError(emsg)

        del self.uidRemotes[remote.uid]
        del self.nameRemotes[remote.name]
        del self.haRemotes[remote.ha]

    def removeAllRemotes(self):
        """
        Remove all the remotes
        """
        remotes = self.remotes.values()  # copy so can delete in place
        for remote in remotes:
            self.removeRemote(remote)

    def incStat(self, key, delta=1):
        """
        Increment stat key counter by delta
        """
        if key in self.stats:
            self.stats[key] += delta
        else:
            self.stats[key] = delta

    def updateStat(self, key, value):
        """
        Set stat key to value
        """
        self.stats[key] = value

    def clearStat(self, key):
        """
        Set the specified state counter to zero
        """
        if key in self.stats:
            self.stats[key] = 0

    def clearAllStats(self):
        """
        Set all the stat counters to zero and reset the timer
        """
        for key, value in self.stats.items():
            self.stats[key] = 0
        self.statTimer.restart()

    def clearTxbs(self):
        """
        Clear .txbs
        """
        del self.txbs[:]  # self.txbs.clear() not supported before python 3.3

    def _serviceOneTxPkt(self):
        """
        Service one (packet, ha) duple on .txPkts deque
        Packet is assumed to be packed already in .packed
        Assumes there is a duple on the deque
        Override in subclass
        """
        ha = ''
        pkt = None
        if not self.txbs:  # everything sent last time
            pkt, ha = self.txPkts.popleft()  # duple = (packet, destination address)
            self.txbs.extend(pkt.packed)

        try:
            count = self.server.send(self.txbs, ha)
        except Exception as ex:
            errno = ex.args[0]  # args[0] is always errno for better compat
            if (errno in (errno.EAGAIN,
                          errno.EWOULDBLOCK,
                          errno.ENETUNREACH,
                          errno.ETIME,
                          errno.EHOSTUNREACH,
                          errno.EHOSTDOWN,
                          errno.ECONNRESET)):
                if pkt is not None:
                    self.txPkts.appendleft((pkt, ha))  # requeue packet
                    self.clearTxbs()
                return False  # blocked try again later
            else:
                raise

        console.profuse("{0}: sent to {1}\n    0x{2}\n".format(self.name,
                                                             ha or '',
                                                             hexlify(self.txbs[:count]).decode('ascii')))

        if count < len(self.txbs):
            del self.txbs[:count]
            return False  # partially blocked try again later

        self.clearTxbs()
        return True  # not blocked

    def serviceTxPkts(self):
        """
        Service the .txPkts deque to send packets through server
        Override in subclass
        """
        while self.server.opened and self.txPkts:
            if not self._serviceOneTxPkt():
                break  # blocked try again later

    def serviceTxPktsOnce(self):
        '''
        Service .txPkts deque once (one pkt)
        '''
        if self.server.opened and self.txPkts:
            self._serviceOneTxPkt()

    def transmit(self, pkt, ha=None):
        """
        Pack and Append (pkt, ha) duple to .txPkts deque
        If destination remote.ha not given
        Then use zeroth remote.ha If any otherwise Raise exception
        Override in subclass
        """
        if ha is None:
            if not self.remotes:
                emsg = "No remote to send to.\n"
                console.terse(emsg)
                self.incStat("pkt_destination_invalid")
                return
            ha = self.remotes.values()[0].ha
        pkt.pack()
        self.txPkts.append((pkt, ha))

    def packetize(self, msg, remote):
        """
        Returns packed packet created from msg destined for remote
        Override in subclass
        """
        return None

    def _serviceOneTxMsg(self):
        """
        Handle one (message, remote) duple from .txMsgs deque
        Assumes there is a duple on the deque
        Appends (packed, ha) duple to txPkts deque
        """
        msg, remote = self.txMsgs.popleft()  # duple (msg, destination uid
        console.verbose("{0} sending to {1}\n{2}\n".format(self.name,
                                                           remote.name,
                                                           msg))
        packet = self.packetize(msg, remote)
        if packet is not None:
            self.txPkts.append((packet, remote.ha))

    def serviceTxMsgs(self):
        """
        Service .txMsgs deque of outgoing  messages
        """
        while self.txMsgs:
            self._serviceOneTxMsg()

    def serviceTxMsgOnce(self):
        """
        Service .txMsgs deque once (one msg)
        """
        if self.txMsgs:
            self._serviceOneTxMsg()

    def message(self, msg, remote=None):
        """
        Append (msg, remote) duple to .txMsgs deque
        If destination remote not given
        Then use zeroth remote If any otherwise Raise exception
        Override in subclass
        """
        if remote is None:
            if not self.remotes:
                emsg = "No remote to send to.\n"
                console.terse(emsg)
                self.incStat("msg_destination_invalid")
                return
            remote = self.remotes.values()[0]
        self.txMsgs.append((msg, remote))

    def serviceAllTx(self):
        '''
        Service:
           txMsgs queue
           txes queue to server send
        '''
        self.serviceTxMsgs()
        self.serviceTxPkts()

    def serviceAllTxOnce(self):
        """
        Service the transmit side of the stack once (one transmission)
        """
        self.serviceTxMsgOnce()
        self.serviceTxPktsOnce()

    def serviceTimers(self):
        """
        Allow timer based processing
        Call .process on all remotes to allow timer based processing
        of their exchanges
        """
        for remote in self.remotes.values():
            remote.process()

    def clearRxbs(self):
        """
        Clear .rxbs
        """
        del self.rxbs[:]  # self.rxbs.clear() not supported before python 3.3

    def parserize(self, raw, ha):
        """
        Returns packet parsed from raw data sourced from ha
        Override in subclass
        """
        return None

    def _serviceOneReceived(self):
        """
        Service one received duple (raw, ha) raw packet data or chunk from server
        assumes that there is a server
        Override in subclass
        """
        ha = None # when no ha returned from receive
        while True:  # keep receiving until empty
            try:
                raw = self.server.receive()
            except Exception as ex:
                errno = ex.args[0]  # args[0] always errno for compat
                if errno == errno.ECONNRESET:
                    return False  # no received data
                else:
                    raise

            if not raw:
                return False  # no received data
            self.rxbs.extend(raw)

        packet = self.parserize(raw, ha)

        if packet is not None:
            del self.rxbs[:packet.size]
            self.rxPkts.append((packet, ha))     # duple = ( packed, source address)
        return True  # received data

    def serviceReceives(self):
        """
        Retrieve from server all recieved and put on the rxes deque
        """
        while self.server.opened:
            if not self._serviceOneReceived():
                break

    def serviceReceivesOnce(self):
        """
        Service recieves once (one reception)
        """
        if self.server.opened:
            self._serviceOneReceived()

    def messagize(self, pkt, ha):
        """
        Returns duple of (message, remote) converted from packet pkt and ha
        Override in subclass
        """
        return (None, None)

    def _serviceOneRxPkt(self):
        """
        Service one duple from .rxPkts deque
        Assumes that there is a message on the .rxes deque
        """
        pkt, ha = self.rxPkts.popleft()  # (packet, source address)
        console.verbose("{0} received packet from {1}\n{2}\n".format(self.name,
                                                                     ha,
                                                                     pkt.show()))
        message, remote = self.messagize(pkt, ha)
        if message is not None:
            self.rxMsgs.append((message, remote))

    def serviceRxPkts(self):
        """
        Process all duples  in .rxPkts deque
        """
        while self.rxPkts:
            self._serviceOneRxPkt()

    def serviceRxPktsOnce(self):
        """
        Service .rxPkts deque once (one pkt)
        """
        if self.rxPkts:
            self._serviceOneRxPkt()

    def _serviceOneRxMsg(self):
        """
        Service one duple from .rxMsgs deque
        """
        msg, remote = self.rxMsgs.popleft()
        console.concise("{0}: Servicing RxMsg from {1} at {2:.3f}:"
                        "\n     {3}\n".format(self.name,
                                              remote.name,
                                              self.stamper.stamp,
                                              msg))
        if remote:
            remote.receive(msg)

    def serviceRxMsgs(self):
        """
        Service .rxMsgs deque of duples
        """
        while self.rxMsgs:
            self._serviceOneRxMsg()


    def serviceRxMsgsOnce(self):
        """
        Service .rxMsgs deque once (one msg)
        """
        if self.rxMsgs:
            self._serviceOneRxMsg()

    def serviceAllRx(self):
        """
        Service recieve side of stack
        """
        self.serviceReceives()
        self.serviceRxPkts()
        self.serviceRxMsgs()
        self.serviceTimers()

    def serviceAllRxOnce(self):
        """
        Service recieve side of stack once (one reception)
        """
        self.serviceReceivesOnce()
        self.serviceRxPktsOnce()
        self.serviceRxMsgsOnce()
        self.serviceTimers()

    def serviceAll(self):
        """
        Service all Rx and Tx
        """
        self.serviceAllRx()
        self.serviceAllTx()

    def serviceServer(self):
        """
        Service the server's receive and transmit queues
        """
        self.serviceReceives()
        self.serviceTxPkts()


class KeepStack(Stack):
    """
    Base stack object with persistance via Keep attribute.
    Should be subclassed for specific transport type
    """
    Count = 0
    Uid =  0

    def __init__(self,
                 puid=None,
                 clean=False,
                 cleanlocal=False,
                 cleanremote=False,
                 keep=None,
                 dirpath='',
                 basedirpath='',
                 local=None, #passed up from subclass
                 name='',
                 uid=None,
                 ha=None,
                 **kwa
                 ):
        '''
        Setup Stack instance
        '''
        if getattr(self, 'puid', None) is None:
            self.puid = puid if puid is not None else self.Uid

        self.keep = keep or keeping.LotKeep(dirpath=dirpath,
                                            basedirpath=basedirpath,
                                            stackname=name)

        if clean or cleanlocal: # clear persisted data so use provided or default data
            self.clearLocalKeep()

        local = self.restoreLocal() or local or lotting.Lot(stack=self,
                                                                 name=name,
                                                                 uid=uid,
                                                                 ha=ha,
                                                                 )
        local.stack = self

        super(KeepStack, self).__init__(puid=puid,
                                        local=local,
                                        **kwa)

        if clean or cleanremote:
            self.clearRemoteKeeps()
        self.restoreRemotes() # load remotes from saved data

        for remote in self.remotes.values():
            remote.nextSid()

        self.dumpLocal() # save local data
        self.dumpRemotes() # save remote data

    def addRemote(self, remote, dump=False):
        '''
        Add a remote  to .remotes
        '''
        super(KeepStack, self).addRemote(remote=remote)
        if dump:
            self.dumpRemote(remote)
        return remote

    def moveRemote(self, remote, new, clear=False, dump=False):
        '''
        Move remote with key remote.uid old to key new uid and replace the odict key index
        so order is the same.
        If clear then clear the keep file for remote at old
        If dump then dump the keep file for the remote at new
        '''
        #old = remote.uid
        super(KeepStack, self).moveRemote(remote, new=new)
        if clear:
            self.keep.clearRemoteData(remote.name)
        if dump:
            self.dumpRemote(remote=remote)

    def renameRemote(self, remote, new, clear=True, dump=False):
        '''
        Rename remote with old remote.name to new name but keep same index
        '''
        old = remote.name
        super(KeepStack, self).renameRemote(remote=remote, new=new)
        if clear:
            self.keep.clearRemoteData(old)
        if dump:
            self.dumpRemote(remote=remote)

    def removeRemote(self, remote, clear=True):
        '''
        Remove remote
        If clear then also remove from disk
        '''
        super(KeepStack, self).removeRemote(remote=remote)
        if clear:
            self.clearRemote(remote)

    def removeAllRemotes(self, clear=True):
        '''
        Remove all the remotes
        If clear then also remove from disk
        '''
        remotes = self.remotes.values() #make copy since changing .remotes in-place
        for remote in remotes:
            self.removeRemote(remote, clear=clear)

    def clearAllDir(self):
        '''
        Clear out and remove the keep dir and contents
        '''
        console.verbose("Stack {0}: Clearing keep dir '{1}'\n".format(
                                  self.name, self.keep.dirpath))
        self.keep.clearAllDir()

    def dumpLocal(self):
        '''
        Dump keeps of local
        '''
        self.keep.dumpLocal(self.local)

    def restoreLocal(self):
        '''
        Load self.local from keep file if any and return local
        Otherwise return None
        '''
        local = None
        data = self.keep.loadLocalData()
        if data:
            if self.keep.verifyLocalData(data):
                local = lotting.Lot(stack=self,
                                         uid=data['uid'],
                                         name=data['name'],
                                         ha=data['ha'],
                                         sid = data['sid'])
                self.local = local
            else:
                self.keep.clearLocalData()
        return local

    def clearLocalKeep(self):
        '''
        Clear local keep
        '''
        self.keep.clearLocalData()

    def dumpRemote(self, remote):
        '''
        Dump keeps of remote
        '''
        self.keep.dumpRemote(remote)

    def dumpRemotes(self, clear=True):
        '''
        Dump all remotes data to keep files
        If clear then clear all files first
        '''
        if clear:
            self.clearRemotes()
        for remote in self.remotes.values():
            self.dumpRemote(remote)

    def restoreRemote(self, name):
        '''
        Load, add, and return remote with name if any
        Otherwise return None
        '''
        remote = None
        data = self.keep.loadRemoteData(name)
        if data:
            if self.keep.verifyRemoteData(data):
                remote = lotting.Lot(stack=self,
                                  uid=data['uid'],
                                  name=data['name'],
                                  ha=data['ha'],
                                  sid=data['sid'])
                self.addRemote(remote)
            else:
                self.keep.clearRemoteData(name)
        return remote

    def restoreRemotes(self):
        '''
        Load and add remote for each remote file
        '''
        keeps = self.keep.loadAllRemoteData()
        if keeps:
            for name, data in keeps.items():
                if self.keep.verifyRemoteData(data):
                    remote = lotting.Lot(stack=self,
                                      uid=data['uid'],
                                      name=data['name'],
                                      ha=data['ha'],
                                      sid=data['sid'])
                    self.addRemote(remote)
                else:
                    self.keep.clearRemoteData(name)

    def clearRemote(self, remote):
        '''
        Clear remote keep of remote
        '''
        self.keep.clearRemoteData(remote.name)

    def clearRemotes(self):
        '''
        Clear remote keeps of .remotes
        '''
        for remote in self.remotes.values():
            self.clearRemote(remote)

    def clearRemoteKeeps(self):
        '''
        Clear all remote keeps
        '''
        self.keep.clearAllRemoteData()

    def clearAllKeeps(self):
        self.clearLocalKeep()
        self.clearRemoteKeeps()


class StreamStack(Stack):
    """
    Stream based stack object.
    Should be subclassed for specific transport type
    """

    def __init__(self,
                 **kwa):
        """
        Setup Stack instance

        Inherited Parameters:
            stamper is relative time stamper for this stack
            version is version tuple or string for this stack
            puid is previous uid for devices managed by this stack
            local is local device if any for this stack
            uid is uid of local device shared with stack if local not given
            name is name of local device shared with stack if local not given
            ha is host address of local device shared with stack if local not given
            kind is kind of local device shared with stack if local not given
            server is interface server if any
            rxbs is bytearray buffer to hold input data stream if any
            rxPkts is deque to hold received packet if any
            rxMsgs is deque to hold received msgs if any
            txPkts is deque to hold packet to be transmitted if any
            remotes is odict to hold remotes keyed by uid if any
            nameRemotes is odict to hold remotes keyed by name if any
            haRemotes is odict to remotes keyed by ha if any
            txMsgs is deque to hold messages to be transmitted if any
            stats is odict of stack statistics if any

        Parameters:

        Inherited Attributes:
            .stamper is relative time stamper for this stack
            .version is version tuple or string for this stack
            .puid is previous uid for devices managed by this stack
            .local is local device for this stack
            .server is interface server if any
            .rxbs is bytearray buffer to hold input data stream
            .rxPkts is deque of duples to hold received packets
            .rxMsgs is deque of duples to hold received msgs and remotes
            .txPkts is deque of duples to hold packets to be transmitted
            .txMsgs is deque of duples to hold messages to be transmitted
            .remotes is odict of remotes indexed by uid
            .uidRemotes is alias for .remotes
            .nameRemotes = odict  of remotes indexed by name
            .haRemotes = odict of remotes indexed by ha
            .stats is odict of stack statistics
            .statTimer is relative timer for statistics

        Attributes:

        Inherited Properties:
            .uid is local device unique id as stack uid
            .name is local device name as stack name
            .ha  is local device ha as stack ha
            .kind is local device kind as stack kind

        Properties:


        """
        super(StreamStack, self).__init__(**kwa)


class GramStack(Stack):
    """
    Datagram based stack object.
    Should be subclassed for specific transport type
    """

    def __init__(self,
                 **kwa):
        """
        Setup Stack instance

        Inherited Parameters:
            stamper is relative time stamper for this stack
            version is version tuple or string for this stack
            puid is previous uid for devices managed by this stack
            local is local device if any for this stack
            uid is uid of local device shared with stack if local not given
            name is name of local device shared with stack if local not given
            ha is host address of local device shared with stack if local not given
            kind is kind of local device shared with stack if local not given
            server is interface server if any
            rxbs is bytearray buffer to hold input data stream if any
            rxPkts is deque to hold received packet if any
            rxMsgs is deque to hold received msgs if any
            txPkts is deque to hold packet to be transmitted if any
            txMsgs is deque to hold messages to be transmitted if any
            remotes is odict to hold remotes keyed by uid if any
            nameRemotes is odict to hold remotes keyed by name if any
            haRemotes is odict to remotes keyed by ha if any
            stats is odict of stack statistics if any

        Parameters:

        Inherited Attributes:
            .stamper is relative time stamper for this stack
            .version is version tuple or string for this stack
            .puid is previous uid for devices managed by this stack
            .local is local device for this stack
            .server is interface server if any
            .rxbs is bytearray buffer to hold input data stream
            .rxPkts is deque of duples to hold received packets
            .rxMsgs is deque of duples to hold received msgs and remotes
            .txPkts is deque of duples to hold packets to be transmitted
            .txMsgs is deque of duples to hold messages to be transmitted
            .remotes is odict of remotes indexed by uid
            .uidRemotes is alias for .remotes
            .nameRemotes = odict  of remotes indexed by name
            .haRemotes = odict of remotes indexed by ha
            .stats is odict of stack statistics
            .statTimer is relative timer for statistics
            .aha is host address of accepting (listening) by server

        Attributes:

        Inherited Properties:
            .uid is local device unique id as stack uid
            .name is local device name as stack name
            .ha  is local device ha as stack ha
            .kind is local device kind as stack kind

        Properties:


        """
        super(GramStack, self).__init__(**kwa)


    def createServer(self, ha):
        """
        Create server from local data
        """
        return None

    def _serviceOneTxPkt(self, laters, blockeds):
        """
        Service one (packet, ha) duple on .txPkts deque
        Packet is assumed to be packed already in .packed
        Assumes there is a duple on the deque
        laters is deque of packed packets to try again later
        blockeds is list of ha destinations that have already blocked on this pass
        Override in subclass
        """
        pkt, ha = self.txPkts.popleft()  # duple = (packet, destination address)

        if ha in blockeds: # already blocked on this iteration
            laters.append((pkt, ha)) # keep sequential
            return False  # blocked

        try:
            count = self.server.send(pkt.packed, ha)  # datagram always sends all
        except socket.error as ex:
            errno = ex.args[0]  # args[0] is always errno for better compat
            if (errno in (errno.EAGAIN,
                          errno.EWOULDBLOCK,
                          errno.ENETUNREACH,
                          errno.ETIME,
                          errno.EHOSTUNREACH,
                          errno.EHOSTDOWN,
                          errno.ECONNRESET)):
                # problem sending such as busy with last message. save it for later
                laters.append((pkt, ha))
                blockeds.append(ha)
            else:
                raise

        console.profuse("{0}: sent to {1}\n    0x{2}\n".format(self.name,
                                                          ha,
                                                          hexlify(pkt.packed).decode('ascii')))
        return True  # not blocked

    def serviceTxPkts(self):
        """
        Service the .txPcks deque to send packets through server
        Override in subclass
        """
        if self.server.opened:
            laters = deque()
            blockeds = []
            while self.txPkts:
                again = self._serviceOneTxPkt(laters, blockeds)
                if not again:
                    break
            while laters:
                self.txPkts.append(laters.popleft())

    def serviceTxPktsOnce(self):
        '''
        Service .txPkts deque once (one pkt)
        '''
        if self.server.opened:
            laters = deque()
            blockeds = [] # will always be empty since only once
            if self.txPkts:
                self._serviceOneTxPkt(laters, blockeds)
            while laters:
                self.txPkts.append(laters.popleft())

    def _serviceOneReceived(self):
        '''
        Service one received duple (raw, ha) raw packet data or chunk from server
        assumes that there is a server
        Override in subclass
        '''
        try:
            raw, ha = self.server.receive()  # if no data the duple is (b'', None)
        except socket.error as ex:
            errno = ex.args[0]  # args[0] always errno for compat
            if errno == errno.ECONNRESET:
                return False  # no received data
            else:
                raise

        if not raw:  # no received data
            return False
        packet = self.parserize(raw, ha)
        if packet is not None:
            self.rxPkts.append((packet, ha))     # duple = ( packed, source address)
        return True  # received data


class UdpStack(GramStack):
    """
    UDP communications Stack Class
    """
    Port = 12357

    def __init__(self,
                 puid=None,
                 local=None,
                 uid=None,
                 name=None,
                 ha=None,
                 kind=None,
                 host=None,
                 port=None,
                 bufcnt=2,
                 **kwa):
        """
        Setup Stack instance

        Inherited Parameters:
            stamper is relative time stamper for this stack
            version is version tuple or string for this stack
            puid is previous uid for devices managed by this stack
            local is local device if any for this stack
            uid is uid of local device shared with stack if local not given
            name is name of local device shared with stack if local not given
            ha is host address of local udp device (host,port) shared with stack if local not given
            kind is kind of local device shared with stack if local not given
            server is interface server if any
            rxbs is bytearray buffer to hold input data stream if any
            rxPkts is deque to hold received packet if any
            rxMsgs is deque to hold received msgs if any
            txPkts is deque to hold packet to be transmitted if any
            txMsgs is deque to hold messages to be transmitted if any
            remotes is odict to hold remotes keyed by uid if any
            nameRemotes is odict to hold remotes keyed by name if any
            haRemotes is odict to remotes keyed by ha if any
            stats is odict of stack statistics if any

        Parameters:
            host is local udp host if ha not provided
            port is local udp port if ha not provided
            bufcnt is number of udp buffers equivalent for udp buffer to allocate

        Inherited Attributes:
            .stamper is relative time stamper for this stack
            .version is version tuple or string for this stack
            .puid is previous uid for devices managed by this stack
            .local is local device for this stack
            .server is interface server if any
            .rxbs is bytearray buffer to hold input data stream
            .rxPkts is deque of duples to hold received packets
            .rxMsgs is deque of duples to hold received msgs and remotes
            .txPkts is deque of duples to hold packets to be transmitted
            .txMsgs is deque of duples to hold messages to be transmitted
            .remotes is odict of remotes indexed by uid
            .uidRemotes is alias for .remotes
            .nameRemotes = odict  of remotes indexed by name
            .haRemotes = odict of remotes indexed by ha
            .stats is odict of stack statistics
            .statTimer is relative timer for statistics
            .aha is host address of accepting (listening) by server

        Attributes:
            .bufcnt is number of udp buffers equivalent ffor udp buffer to allocate

        Inherited Properties:
            .uid is local device unique id as stack uid
            .name is local device name as stack name
            .ha  is local device ha as stack ha
            .kind is local device kind as stack kind

        Properties:


        """
        if ha is None:
            if (host is not None or port is not None):
                host = host if host is not None else ''
                port = port if port is not None else self.Port
                ha = (host, port)
            else:
                ha = ('', self.Port)  # host all interfaces, bind with 0 port creates ephemeral port

        self.bufcnt = bufcnt  # used in createServer

        if getattr(self, 'puid', None) is None:  # need .puid to make local
            self.puid = puid if puid is not None else self.Uid

        local = local if local is not None else devicing.UdpLocalDevice(stack=self,
                                                                        uid=uid,
                                                                        name=name,
                                                                        ha=ha,
                                                                        kind=kind)
        super().__init__(local=local, ha=ha, **kwa)

    def createServer(self, ha):
        """
        Create local listening server for stack
        """
        server = udping.SocketUdpNb(ha=ha,
                             bufsize=udping.UDP_MAX_PACKET_SIZE * self.bufcnt)
        return server

    def packetize(self, msg, remote):
        """
        Returns packed packet created from msg destined for remote
        Override in subclass
        """
        return packeting.Packet(packed=msg.encode('ascii'))

    def parserize(self, raw, ha):
        """
        Returns packet parsed from raw data sourced from ha
        Override in subclass
        """
        return packeting.Packet(packed=raw)

    def messagize(self, pkt, ha):
        """
        Returns duple of (message, remote) converted from packet pkt and ha
        Override in subclass
        """
        msg = pkt.packed.decode("ascii")
        try:
            remote = self.haRemotes[ha]
        except KeyError as ex:
            console.concise(("{0}: Dropping packet received from unknown remote "
                             "ha '{1}'.\n{2}\n".format(self.name, ha, pkt.packed)))
        return (msg, remote)

    def _serviceOneRxMsg(self):
        """
        Service one duple from .rxMsgs deque
        """
        msg, remote = self.rxMsgs.popleft()
        console.concise("{0}: Servicing RxMsg from {1} at {2:.3f}:"
                        "\n     {3}\n".format(self.name,
                                              remote.name,
                                              self.stamper.stamp,
                                              msg))
        self.incStat("msg_received")
        if remote:
            remote.receive(msg)
