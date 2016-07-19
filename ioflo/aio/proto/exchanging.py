"""
Exchange Base Class Package

"""
from __future__ import absolute_import, division, print_function

import struct
from binascii import hexlify
from collections import deque
import enum

from ...aid.sixing import *
from ...aid.odicting import odict
from ...aid.byting import bytify, unbytify, packify, packifyInto, unpackify
from ...aid.eventing import eventify, tagify
from ...aid.timing import StoreTimer, tuuid
from ...aid import getConsole
from .protoing import MixIn

console = getConsole()


class Exchange(MixIn):
    """
    Exchange (pseudo transaction) base class for exchanges
    """
    Timeout =  2.0  # default timeout
    RedoTimeout = 0.5  # default redo timeout

    def __init__(self,
                 stack,
                 uid=None,
                 name=None,
                 device=None,
                 timeout=None,
                 redoTimout=None,
                 tx=None,
                 rx=None):
        """
        Setup Exchange instance

        Inherited Parameters:

        Parameters:
            stack is interface stack instance
            uid is Exchange unique id
            name is user friendly name of exchange
            device is associated device handling exchange
            timeout is exchange expiration timeout
                timeout of 0.0 means no expiration go on forever
            redoTimeout is redo appropriate packet/message in exchange
            rx is latest received  msg/pkt/data
            tx is latest/next transmitted msg/pkt/data

        Class Attributes:
            .Timeout is overall exchange timeout
            .RedoTimeout is redo timeout

        Inherited Attributes

        Attributes:
            .stack is interface stack instance
            .uid is Exchange unique id
            .name is user friendly name of exchange
            .device is associated device handling exchange
            .timeout is exchange expiration timeout
                timeout of 0.0 means no expiration go on forever
            .timer is StoreTimer instance for .timeout
            .redoTimeout is redo appropriate packet/message in exchange
            .redoTimer is StoreTimer instance for .redoTimeout
            .rx is latest received  msg/pkt/data
            .tx is latest/next transmitted msg/pkt/data
            .done is True If done  False otherwise
            .failed is True If failed False otherwise
            .acked is True if ack has been sent

        Inherited Properties

        Properties

        """
        self.stack = stack
        self.uid = uid if uid is not None else tuuid()
        self.name = name or self.__class__.__name__
        self.device = device
        self.timeout = timeout if timeout is not None else self.Timeout
        self.timer = StoreTimer(stack.stamper, duration=self.timeout)
        self.redoTimeout = redoTimeout if redoTimout is not None else self.RedoTimeout
        self.redoTimer = StoreTimer(stack.stamper, duration=self.redoTimeout)
        self.rx = rx  # latest received
        self.tx = tx  # initial to transmit
        self.done = False
        self.failed = False
        self.acked = False

    def prepStart(self):
        """
        Set flags for start
        """
        self.done = False
        self.failed = False
        self.acked = False

    def start(self):
        """
        Startup first run when context is ready
        override in subclass
        """
        self.prepStart()

    def run(self):
        """
        Run one iteration
        """
        self.done = True

    def process(self):
        """
        Process time based handling of exchange like timeout or retries
        """
        if self.timeout > 0.0 and self.timer.expired:
            console.verbose("{0}. Timed out with {1} at {2}\n".format(
                    self.stack.name, self.device.name, round(self.stack.stamper.stamp, 3)))
            self.fail()
            return

        if self.redoTimeout > 0.0 and self.redoTimer.expired:
            self.redoTimer.restart()
            console.verbose("{0}: Redoing {1} with {2} at {3}\n".format(
                                            self.stack.name,
                                            self.name,
                                            self.device.name,
                                            round(self.stack.stamper.stamp, 3)))
            if self.tx is not None:
                self.send(self.tx)

    def prepSend(self, tx=None):
        """
        Setups flags and .tx for send.
        """
        if tx is not None:
            self.tx = tx  # always last transmitted msg/pkt/data
        if self.tx is None:
            raise ValueError("{0}: {1} Cannot send. No .tx."
                                "\n".format(self.stack.name,
                                            self.name))

    def send(self, tx=None):
        """
        Setup and transmit packet

        Extend in subclass to queue appropriately

        Either:
           self.prepSend(tx)
           self.stack.transmit(self.tx, self.device.ha)
        Or
           self.prepSend(tx)
           self.stack.message(self.tx, self.device)
        """
        self.prepSend(tx=tx)
        self.transmit(pkt=tx)

    def transmit(self, pkt=None):
        """
        Queue pkt on stack packet queue
        """
        if pkt is not None:
            self.tx = pkt  # always last transmitted msg/pkt/data
        if self.tx is None:
            raise ValueError("{0}: {1} Cannot transmit. No .tx."
                                "\n".format(self.stack.name,
                                            self.name))
        self.stack.transmit(self.tx)

    def message(self, msg=None):
        """
        Queue msg on stack message queue
        """
        if msg is not None:
            self.tx = msg  # always last transmitted msg/pkt/data
        if self.tx is None:
            raise ValueError("{0}: {1} Cannot message. No .tx."
                                "\n".format(self.stack.name,
                                            self.name))
        self.stack.message(self.tx)

    def prepReceive(self, rx):
        """
        Setups .rx for receive. And flags if any
        extend in subclass
        """
        self.rx = rx

    def receive(self, rx):
        """
        Process received msg/pkt/data.
        Subclasses should extend with call to .prepReceive
        and additional handling
        """
        self.prepReceive(rx)


    def prepFinish(self):
        """
        Mark flags
        """
        self.done = True

    def finish(self):
        """
        Exchange complete
        Default is as success unless .failed
        Mark flags
        """
        self.prepFinish()
        console.verbose("{0}: Finished {1} with {2} as {3}"
                        " at {4}\n".format(self.stack.name,
                                            self.name,
                                            self.device.name,
                                            'FAILURE' if self.failed else 'SUCCESS',
                                            round(self.stack.stamper.stamp, 3)))

    def fail(self):
        """
        Exchange complete as failure
        """
        self.failed = True
        self.finish()


class Exchanger(Exchange):
    """
    Exchanger (pseudo transaction) base class for initiated exchanges
    """
    def __init__(self, stack, **kwa):
        """
        Setup Exchanger instance

        Inherited Parameters:
            stack is interface stack instance
            uid is Exchange unique id
            name is user friendly name of exchange
            device is associated device handling exchange
            timeout is exchange expiration timeout
                timeout of 0.0 means no expiration go on forever
            redoTimeout is redo appropriate packet/message in exchange
            rx is latest received  msg/pkt/data
            tx is latest/next transmitted msg/pkt/data

        Parameters:

        Inherited Class Attributes:
            .Timeout is overall exchange timeout
            .RedoTimeout is redo timeout

        Inherited Attributes
            .stack is interface stack instance
            .uid is Exchange unique id
            .name is user friendly name of exchange
            .device is associated device handling exchange
            .timeout is exchange expiration timeout
                timeout of 0.0 means no expiration go on forever
            .timer is StoreTimer instance for .timeout
            .redoTimeout is redo appropriate packet/message in exchange
            .redoTimer is StoreTimer instance for .redoTimeout
            .rx is latest received  msg/pkt/data
            .tx is latest/next transmitted msg/pkt/data
            .done is True If done  False otherwise
            .failed is True If failed False otherwise
            .acked is True if ack has been sent

        Attributes:

        Inherited Properties

        Properties

        """
        super(Exchanger, self).__init__(stack=stack, **kwa)

    def start(self, tx=None):
        """
        Initiate exchange
        tx is latest/next transmitted msg/pkt/data

        """
        self.prepStart()  # reset flags

        self.timer.restart()
        self.redoTimer.restart()
        console.verbose("{0}: Initiating {1} with {2} at {3}.\n".format(self.stack.name,
                                            self.name,
                                            self.device.name,
                                            round(self.stack.stamper.stamp, 3)))
        self.send(tx)

class Exchangent(Exchange):
    """
    Exchangent (pseudo transaction) base class for correspondent exchanges
    """
    Timeout = 0.5  # default timeout
    RedoTimeout = 0.1

    def __init__(self, stack, **kwa):
        """
        Setup Exchangent instance

        Inherited Parameters:
            stack is interface stack instance
            uid is Exchange unique id
            name is user friendly name of exchange
            device is associated device handling exchange
            timeout is exchange expiration timeout
                timeout of 0.0 means no expiration go on forever
            redoTimeout is redo appropriate packet/message in exchange
            rx is latest received  msg/pkt/data
            tx is latest/next transmitted msg/pkt/data

        Parameters:

        Inherited Class Attributes:
            .Timeout is overall exchange timeout
            .RedoTimeout is redo timeout

        Inherited Attributes
            .stack is interface stack instance
            .uid is Exchange unique id
            .name is user friendly name of exchange
            .device is associated device handling exchange
            .timeout is exchange expiration timeout
                timeout of 0.0 means no expiration go on forever
            .timer is StoreTimer instance for .timeout
            .redoTimeout is redo appropriate packet/message in exchange
            .redoTimer is StoreTimer instance for .redoTimeout
            .rx is latest received  msg/pkt/data
            .tx is latest/next transmitted msg/pkt/data
            .done is True If done  False otherwise
            .failed is True If failed False otherwise
            .acked is True if ack has been sent

        Attributes:

        Inherited Properties

        Properties


        """
        super(Exchangent, self).__init__(stack=stack, **kwa)

    def start(self, rx=None):
        """
        Correspond to exchange
        """
        self.prepStart()  # reset flags

        self.timer.restart()
        self.redoTimer.restart()
        console.verbose("{0}: Corresponding {1} with {2} at {3}.\n".format(self.stack.name,
                                            self.name,
                                            self.device.name,
                                            round(self.stack.stamper.stamp, 3)))
        self.respond(rx)

    def respond(self, rx=None):
        """
        Respond to the associated request
        """
        if rx is not None:
            self.rx = rx

        if self.rx is None:
            raise ValueError("{0}: Cannot respond {1} no .rx"
                             "received.\n".format(self.stack.name,
                                                  self.name))
        self.finish()
