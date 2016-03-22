"""
Exchange Base Class Package

"""
from __future__ import absolute_import, division, print_function

import struct
from binascii import hexlify
from collections import deque
import enum

from ioflo.aid.sixing import *
from ioflo.aid.odicting import odict
from ioflo.aid.byting import bytify, unbytify, packify, packifyInto, unpackify
from ioflo.aid.eventing import eventify, tagify
from ioflo.aid.timing import StoreTimer
from ioflo.aid import getConsole

console = getConsole()


class Exchange(object):
    """
    Exchange (pseudo transaction) base class for exchanges
    """
    Timeout =  2.0  # default timeout
    RedoTimeout = 0.5  # default redo timeout

    def __init__(self,
                 stack,
                 euid=None,
                 device=None,
                 name=None,
                 timeout=None,
                 redoTimout=None,
                 rxMsg=None,
                 txMsg=None):
        """
        Setup Exchange instance
        timeout of 0.0 means no timeout go forever

        Attributes:
            .stack is interface stack instance
            .euid is Exchange uid
            .done is True If done  False otherwise
            .failed is True If failed False otherwise

        """
        self.stack = stack
        self.euid = euid
        self.done = False
        self.failed = False
        self.device = device
        self.name = name or self.__class__.__name__
        self.timeout = timeout if timeout is not None else self.Timeout
        self.timer = StoreTimer(stack.stamper, duration=self.timeout)
        self.redoTimeout = redoTimeout if redoTimout is not None else self.RedoTimeout
        self.redoTimer = StoreTimer(stack.stamper, duration=self.redoTimeout)
        self.rxMsg = rxMsg  # latest message received
        self.txMsg = txMsg  # initial message to transmit
        self.acked = False

    def start(self):
        """
        Startup first run when context is ready
        """
        self.done = False
        self.failed = False

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
            console.concise("Exchange {0}. Timed out with {1} at {2}\n".format(
                    self.stack.name, self.device.name, round(self.stack.stamper.stamp, 3)))
            self.fail()
            return

        if self.redoTimer.expired:
            self.redoTimer.restart()
            console.concise("{0}: Redoing {1} with {2} at {3}\n".format(
                                            self.stack.name,
                                            self.name,
                                            self.device.name,
                                            round(self.stack.stamper.stamp, 3)))
            self.transmit(self.txMsg)

    def receive(self, msg):
        """
        Process received msg.
        Subclasses should call super to call this
        """
        self.rxMsg = msg

    def transmit(self, msg):
        """
        Queue msg on stack transmit queue
        """
        self.stack.transmit(msg)
        self.txMsg = msg  # always last transmitted msg

    def finish(self, event=None):
        """
        Exchange complete as success
        Mark flags and  push completion event
        """
        if event is None:
            event =  eventify(tag=tagify(['exchange', self.name, 'finished' ]))
        self.stack.rxEvents.append(event)
        self.remove()
        self.done = True
        console.concise("{0}: Finished {1} with {2} as {3} at {4}\n".format(
                                            self.stack.name,
                                            self.name,
                                            self.device.name,
                                            'FAILURE' if self.failed else 'SUCCESS',
                                            round(self.stack.stamper.stamp, 3)))

    def fail(self, event=None):
        """
        Exchange complete as failure
        """
        self.failed = True
        if event is None:
            event =  eventify(tag=tagify(['exchange', self.name, 'failed' ]))
        self.finish(event=event)


class Exchanger(Exchange):
    """
    Exchanger (pseudo transaction) base class for initiated exchanges
    """
    def __init__(self,
                 stack,
                 **kwa):
        """
        Setup Exchanger instance
        """
        super(Exchanger, self).__init__(stack=stack, **kwa)

    def add(self):
        """
        set self as .device exchanger
        """
        if self.device.exchanger is not None:
            raise ValueError("Failed add, device exchanger is not None")

        self.device.exchanger = self

    def remove(self):
        """
        Remove self as device exchanger
        """
        if self.device.exchanger is self:
            self.device.exchanger = None

    def process(self):
        """
        Process time based handling of exchange like timeout or retries
        """
        if self.timeout > 0.0 and self.timer.expired:
            console.concise("Exchanger {0}. Timed out with {1} at {2}\n".format(
                    self.stack.name, self.device.name, round(self.stack.stamper.stamp, 3)))
            self.fail()
            return

        if self.redoTimer.expired:
            self.redoTimer.restart()
            console.concise("{0}: Redoing {1} with {2} at {3}\n".format(
                                    self.stack.name,
                                    self.name,
                                    self.device.name,
                                    round(self.stack.stamper.stamp, 3)))
            self.transmit(self.txMsg)

    def start(self, txMsg=None):
        """
        Initiate exchange
        """
        if txMsg is not None:
            self.txMsg = txMsg

        if not self.txMsg:
            raise waving.ExchangeError("{0}: Cannot start {1} no initial message"
                                        " to send.".format(self.stack.name,
                                                           self.name))

        self.timer.restart()
        self.redoTimer.restart()
        self.add()
        console.concise("{0}: Initiating {1} with {2} at {3}.\n".format(self.stack.name,
                                            self.name,
                                            self.device.name,
                                            round(self.stack.stamper.stamp, 3)))

        self.transmit(self.txMsg)

    def finish(self, event=None):
        """
        Exchange complete as success
        Super to clean up
        """
        super(Exchanger, self).finish(event=event)


class Exchangent(Exchange):
    """
    Exchangent (pseudo transaction) base class for correspondent exchanges
    """
    Timeout = 0.5  # default timeout
    RedoTimeout = 0.1

    def __init__(self,
                 stack,
                 **kwa):
        """
        Setup Exchangent instance

        """
        super(Exchangent, self).__init__(stack=stack, **kwa)

    def add(self):
        """
        set self as .device exchangent
        """
        if self.device.exchangent is not None:
            raise ValueError("Failed add, device exchangent in use.")

        self.device.exchanger = self

    def remove(self):
        """
        Remove self as device exchangent
        """
        if self.device.exchangent is self:
            self.device.exchangent = None


    def process(self):
        """
        Process time based handling of exchange like timeout or retries
        """
        if self.timeout > 0.0 and self.timer.expired:
            console.concise("Exchange {0}. Timed out with {1} at {2}\n".format(
                    self.stack.name, self.device.name, round(self.stack.stamper.stamp, 3)))
            self.fail()
            return

    def start(self, rxMsg=None):
        """
        Correspond to exchange
        """
        if rxMsg is not None:
            self.rxMsg = rxMsg

        if not self.rxMsg:
            raise waving.ExchangeError("{0}: Cannot start {1} no initial message"
                                        " to correspond to.".format(self.stack.name,
                                                                    self.name))
        self.timer.restart()
        self.redoTimer.restart()
        self.add()
        console.concise("{0}: Corresponding {1} with {2} at {3}.\n".format(self.stack.name,
                                            self.name,
                                            self.device.name,
                                            round(self.stack.stamper.stamp, 3)))
        self.respond()

    def respond(self):
        """
        Respond to the associated request
        """
        self.finish()
