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

# Import ioflo libs
from ioflo.aid.sixing import *
from ioflo.aid.byting import hexify, bytify, unbytify, packify, unpackify
from ioflo.aid.timing import Timer
from ioflo.aid import getConsole

console = getConsole()

from ioflo.aio.proto import stacking, devicing

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
        self.assertEqual(stack.server, None)
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


    def testStacks(self):
        """
        Test two stacks sending packets
        """
        console.terse("{0}\n".format(self.testStacks.__doc__))

        alpha = stacking.UdpStack(name='alpha',
                               port=8000)
        self.assertEqual(alpha.name, "alpha")
        self.assertEqual(alpha.ha, ('127.0.0.1', 8000))
        self.assertEqual(alpha.aha, ('0.0.0.0', 8000))
        self.assertIs(alpha.server.opened, True)
        self.assertEqual(len(alpha.remotes), 0)

        remote = devicing.UdpRemoteDevice(stack=alpha,
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
        self.assertIs(beta.server.opened, True)
        self.assertEqual(len(beta.remotes), 0)

        remote = devicing.UdpRemoteDevice(stack=beta,
                                       name='AlphaRemote',
                                       ha=('localhost', 8000))
        self.assertEqual(remote.uid, 2)
        self.assertEqual(remote.name, 'AlphaRemote')
        self.assertEqual(remote.ha, ('127.0.0.1', 8000))
        beta.addRemote(remote)

        msg2beta = "Hello beta it's me alpha."
        alpha.transmit(msg2beta)

        msg2alpha = "Hi alpha from beta."
        beta.transmit(msg2alpha)

        timer = Timer(duration=0.5)
        while not timer.expired:
            alpha.serviceAll()
            beta.serviceAll()

        self.assertEqual(len(alpha.rxMsgs), 0)
        self.assertEqual(len(beta.rxMsgs), 0)
        self.assertEqual(alpha.stats['msg_received'], 1)
        self.assertEqual(beta.stats['msg_received'], 1)

        alpha.server.close()
        beta.server.close()

    def testUdpStack(self):
        """
        Test UdpStack class
        """
        console.terse("{0}\n".format(self.testUdpStack.__doc__))

        stack = stacking.UdpStack()
        self.assertIsInstance(stack.local, devicing.UdpLocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, ('127.0.0.1', stacking.UdpStack.Port))
        self.assertEqual(stack.local.kind, None)
        self.assertEqual(stack.aha, ('0.0.0.0', stacking.UdpStack.Port))
        stack.close()

        ha = ('127.0.0.1', 8000)
        stack = stacking.UdpStack(ha=ha)
        self.assertIsInstance(stack.local, devicing.UdpLocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, ha)
        self.assertEqual(stack.local.kind, None)
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
             'testStacks',
             'testUdpStack',
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



