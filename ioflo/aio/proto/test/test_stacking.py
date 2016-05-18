# -*- coding: utf-8 -*-
"""
Unittests
"""
from __future__ import absolute_import, division, print_function

import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os

from binascii import hexlify
import time

# Import ioflo libs
from ioflo.aid.sixing import *
from ioflo.aid.byting import hexify, bytify, unbytify, packify, unpackify
from ioflo.aid.timing import Timer, StoreTimer, Stamper
from ioflo.aid import getConsole

console = getConsole()

from ioflo.aio.proto import stacking, devicing, packeting

def setUpModule():
    console.reinit(verbosity=console.Wordage.concise)

def tearDownModule():
    console.reinit(verbosity=console.Wordage.concise)

class BasicTestCase(unittest.TestCase):
    """
    Test Case
    """

    def setUp(self):
        """

        """
        console.reinit(verbosity=console.Wordage.profuse)

    def tearDown(self):
        """

        """
        console.reinit(verbosity=console.Wordage.concise)

    def testStack(self):
        """
        Test Stack class
        """
        console.terse("{0}\n".format(self.testStack.__doc__))

        stack = stacking.Stack()
        self.assertIs(stack.local.stack, stack)
        self.assertEqual(stack.name, "Device1")
        self.assertEqual(stack.local.name, stack.name)
        self.assertEqual(stack.uid, 1)
        self.assertEqual(stack.local.uid, stack.uid)
        self.assertEqual(stack.ha, '')
        self.assertEqual(stack.aha, '')
        self.assertEqual(stack.local.ha, stack.ha)
        self.assertEqual(stack.kind, None)
        self.assertEqual(stack.local.kind, stack.kind)
        self.assertEqual(stack.handler, None)


    def testRemoteStack(self):
        """
        Test RemoteStack class
        """
        console.terse("{0}\n".format(self.testRemoteStack.__doc__))

        stack = stacking.RemoteStack()
        self.assertIs(stack.local.stack, stack)
        self.assertEqual(stack.name, "Device1")
        self.assertEqual(stack.local.name, stack.name)
        self.assertEqual(stack.uid, 1)
        self.assertEqual(stack.local.uid, stack.uid)
        self.assertEqual(stack.ha, '')
        self.assertEqual(stack.aha, '')
        self.assertEqual(stack.local.ha, stack.ha)
        self.assertEqual(stack.kind, None)
        self.assertEqual(stack.local.kind, stack.kind)
        self.assertEqual(stack.handler, None)

        self.assertEqual(len(stack.remotes), 0)
        self.assertIs(stack.remotes, stack.uidRemotes)
        self.assertEqual(len(stack.nameRemotes), 0)
        self.assertEqual(len(stack.haRemotes), 0)
        self.assertEqual(len(stack.stats), 0)

        remote = devicing.RemoteDevice(stack=stack, ha='hello')
        self.assertEqual(remote.uid, 2)
        self.assertEqual(remote.name, 'Device2')
        self.assertEqual(remote.ha, 'hello')
        stack.addRemote(remote)
        self.assertEqual(len(stack.remotes), 1)
        self.assertEqual(len(stack.nameRemotes), 1)
        self.assertEqual(len(stack.haRemotes), 1)
        self.assertIs(remote, stack.remotes[remote.uid])
        self.assertIs(remote, stack.nameRemotes[remote.name])
        self.assertIs(remote, stack.haRemotes[remote.ha])

        self.assertRaises(ValueError, stack.addRemote, remote)

        newUid = 3
        stack.moveRemote(remote, newUid)
        self.assertEqual(remote.uid, newUid)
        self.assertIs(remote, stack.remotes[newUid])

        newName = 'DeviceBlah'
        stack.renameRemote(remote, newName)
        self.assertEqual(remote.name, newName)
        self.assertIs(remote, stack.nameRemotes[newName])

        newHa = 'HelloWorld'
        stack.rehaRemote(remote, newHa)
        self.assertEqual(remote.ha, newHa)
        self.assertIs(remote, stack.haRemotes[newHa])

        stack.removeRemote(remote)
        self.assertEqual(len(stack.remotes), 0)
        self.assertEqual(len(stack.nameRemotes), 0)
        self.assertEqual(len(stack.haRemotes), 0)

    def testUdpStack(self):
        """
        Test UdpStack class
        """
        console.terse("{0}\n".format(self.testUdpStack.__doc__))

        stack = stacking.UdpStack()
        self.assertIsInstance(stack.local, devicing.IpLocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, ('127.0.0.1', stacking.UdpStack.Port))
        self.assertEqual(stack.local.kind, None)
        self.assertEqual(stack.aha, ('0.0.0.0', stacking.UdpStack.Port))
        stack.close()

        ha = ('127.0.0.1', 8000)
        stack = stacking.UdpStack(ha=ha)
        self.assertIsInstance(stack.local, devicing.IpLocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, ha)
        self.assertEqual(stack.local.kind, None)
        self.assertEqual(stack.aha, ha)
        stack.close()

    def testUdpStacks(self):
        """
        Test two stacks sending packets
        """
        console.terse("{0}\n".format(self.testUdpStacks.__doc__))

        stamper = Stamper()

        alpha = stacking.UdpStack(name='alpha',
                               port=8000)
        self.assertEqual(alpha.name, "alpha")
        self.assertEqual(alpha.ha, ('127.0.0.1', 8000))
        self.assertEqual(alpha.aha, ('0.0.0.0', 8000))
        self.assertIs(alpha.handler.opened, True)
        self.assertEqual(len(alpha.remotes), 0)

        remote = devicing.IpRemoteDevice(stack=alpha,
                                       name='BetaRemote',
                                       ha=('localhost', 8002))
        self.assertEqual(remote.uid, 2)
        self.assertEqual(remote.name, 'BetaRemote')
        self.assertEqual(remote.ha, ('127.0.0.1', 8002))
        alpha.addRemote(remote)


        beta = stacking.UdpStack(name='beta',
                              port=8002)
        self.assertEqual(beta.name, "beta")
        self.assertEqual(beta.ha, ('127.0.0.1', 8002))
        self.assertEqual(beta.aha, ('0.0.0.0', 8002))
        self.assertIs(beta.handler.opened, True)
        self.assertEqual(len(beta.remotes), 0)

        remote = devicing.IpRemoteDevice(stack=beta,
                                       name='AlphaRemote',
                                       ha=('localhost', 8000))
        self.assertEqual(remote.uid, 2)
        self.assertEqual(remote.name, 'AlphaRemote')
        self.assertEqual(remote.ha, ('127.0.0.1', 8000))
        beta.addRemote(remote)

        msg2beta = "Hello beta it's me alpha."
        alpha.message(msg2beta)

        msg2alpha = "Hi alpha from beta."
        beta.message(msg2alpha)

        #timer = Timer(duration=0.5)
        while (alpha.txMsgs or alpha.txPkts or alpha.rxPkts or alpha.rxMsgs
                or beta.txMsgs or  beta.txPkts or beta.rxPkts or beta.rxMsgs):
            alpha.serviceAllTx()
            beta.serviceAllTx()
            time.sleep(0.1)
            alpha.serviceAllRx()
            beta.serviceAllRx()
            stamper.advanceStamp(0.1)

        self.assertEqual(len(alpha.rxMsgs), 0)
        self.assertEqual(len(beta.rxMsgs), 0)
        self.assertEqual(alpha.stats['msg_received'], 1)
        self.assertEqual(beta.stats['msg_received'], 1)

        msg2beta = "Whats up beta?"
        packet = packeting.Packet(packed=msg2beta.encode('ascii'))
        alpha.transmit(packet)

        msg2alpha = "Just hanging alpha."
        packet = packeting.Packet(packed=msg2alpha.encode('ascii'))
        beta.transmit(packet)

        while (alpha.txMsgs or alpha.txPkts or alpha.rxPkts or alpha.rxMsgs
                or beta.txMsgs or  beta.txPkts or beta.rxPkts or beta.rxMsgs):
            alpha.serviceAllTx()
            beta.serviceAllTx()
            time.sleep(0.1)
            alpha.serviceAllRx()
            beta.serviceAllRx()
            stamper.advanceStamp(0.1)

        self.assertEqual(len(alpha.rxMsgs), 0)
        self.assertEqual(len(beta.rxMsgs), 0)
        self.assertEqual(alpha.stats['msg_received'], 2)
        self.assertEqual(beta.stats['msg_received'], 2)

        alpha.close()
        beta.close()

        alpha.reopen()
        beta.reopen()

        alpha.close()
        beta.close()

    def testTcpServerStack(self):
        """
        Test TcpServerStack class
        """
        console.terse("{0}\n".format(self.testTcpServerStack.__doc__))

        stack = stacking.TcpServerStack()
        self.assertIsInstance(stack.local, devicing.IpLocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, ('127.0.0.1', stacking.TcpServerStack.Port))
        self.assertEqual(stack.local.kind, None)
        self.assertEqual(stack.aha, ('0.0.0.0', stacking.UdpStack.Port))
        self.assertEqual(stack.eha, ('127.0.0.1', stacking.TcpServerStack.Port))
        stack.close()

        ha = ('127.0.0.1', 9000)
        stack = stacking.TcpServerStack(ha=ha)
        self.assertIsInstance(stack.local, devicing.IpLocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, ha)
        self.assertEqual(stack.local.kind, None)
        self.assertEqual(stack.aha, ha)
        self.assertEqual(stack.eha, ha)
        stack.close()

    def testTcpClientStack(self):
        """
        Test TcpClientStack class
        """
        console.terse("{0}\n".format(self.testTcpClientStack.__doc__))

        stack = stacking.TcpClientStack()
        self.assertIsInstance(stack.local, devicing.IpLocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, (None, None))  # not connected yet
        self.assertEqual(stack.local.kind, None)
        self.assertEqual(stack.aha, ('127.0.0.1', stacking.TcpServerStack.Port))
        self.assertEqual(stack.aha, stack.ha)
        self.assertEqual(stack.ha, stack.remote.ha)
        self.assertEqual(stack.aha, ('127.0.0.1', stacking.TcpServerStack.Port))
        self.assertEqual(stack.remote.ha, ('127.0.0.1', stacking.TcpServerStack.Port))
        stack.close()

        ha = ('127.0.0.1', 9000)
        stack = stacking.TcpClientStack(ha=ha)
        self.assertIsInstance(stack.local, devicing.IpLocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, (None, None))
        self.assertEqual(stack.local.kind, None)
        self.assertEqual(stack.ha, ha)
        self.assertEqual(stack.aha, stack.ha)
        self.assertEqual(stack.ha, stack.remote.ha)
        self.assertEqual(stack.remote.ha, ('127.0.0.1', 9000))
        self.assertEqual(stack.aha, ha)
        stack.close()



def runOne(test):
    '''
    Unittest Runner
    '''
    test = BasicTestCase(test)
    suite = unittest.TestSuite([test])
    unittest.TextTestRunner(verbosity=2).run(suite)

def runSome():
    """ Unittest runner """
    tests =  []
    names = [
             'testStack',
             'testRemoteStack',
             'testUdpStack',
             'testUdpStacks',
             'testTcpServerStack',
             'testTcpClientStack',
            ]
    tests.extend(map(BasicTestCase, names))
    suite = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)

def runAll():
    """ Unittest runner """
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BasicTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__' and __package__ is None:

    #runAll() #run all unittests

    runSome()#only run some

    #runOne('testPart')



