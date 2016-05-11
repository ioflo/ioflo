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
from ioflo.aid import getConsole

console = getConsole()

from ioflo.aio.proto import devicing, stacking

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

    def testDevice(self):
        """
        Test Device class
        """
        console.terse("{0}\n".format(self.testDevice.__doc__))

        stack = stacking.Stack()
        self.assertIsInstance(stack.local, devicing.LocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, "")
        self.assertEqual(stack.local.kind, None)

        device = devicing.Device(stack=stack)
        self.assertEqual(device.stack, stack)
        self.assertEqual(device.uid, 2)  # stacks .local has uid 1
        self.assertEqual(device.name, "Device{0}".format(device.uid))
        self.assertEqual(device.ha, '')
        self.assertEqual(device.kind, None)

        stack = stacking.RemoteStack()
        self.assertIsInstance(stack.local, devicing.LocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, "")
        self.assertEqual(stack.local.kind, None)

        device = devicing.RemoteDevice(stack=stack)
        self.assertIs(device.stack, stack)
        self.assertEqual(device.uid, 2)
        self.assertEqual(device.name, "Device{0}".format(device.uid))
        self.assertEqual(device.ha, '')
        self.assertEqual(device.kind, None)


    def testUdpDevice(self):
        """
        Test UdpDevice class
        """
        console.terse("{0}\n".format(self.testUdpDevice.__doc__))

        stack = stacking.UdpStack()
        self.assertIsInstance(stack.local, devicing.IpLocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, ('127.0.0.1', stacking.UdpStack.Port))
        self.assertEqual(stack.local.kind, None)
        self.assertEqual(stack.aha, ('0.0.0.0', stacking.UdpStack.Port))

        device = devicing.IpDevice(stack=stack)
        self.assertEqual(device.stack, stack)
        self.assertEqual(device.uid, 2)  # stacks .local has uid 1
        self.assertEqual(device.name, "Device{0}".format(device.uid))
        self.assertEqual(device.ha, ('127.0.0.1',stacking.UdpStack.Port))
        self.assertEqual(device.kind, None)

        device = devicing.IpRemoteDevice(stack=stack)
        self.assertIs(device.stack, stack)
        self.assertEqual(device.uid, 3)
        self.assertEqual(device.name, "Device{0}".format(device.uid))
        self.assertEqual(device.ha, ('127.0.0.1', stacking.UdpStack.Port))
        self.assertEqual(device.kind, None)

        stack.close()

        ha = ('127.0.0.1', 8000)
        stack = stacking.UdpStack(ha=ha)
        self.assertIsInstance(stack.local, devicing.IpLocalDevice)
        self.assertEqual(stack.local.uid, 1)
        self.assertEqual(stack.local.name, "Device{0}".format(stack.local.uid))
        self.assertEqual(stack.local.ha, ha)
        self.assertEqual(stack.local.kind, None)
        self.assertEqual(stack.aha, ha)

        device = devicing.IpDevice(stack=stack, ha=ha)
        self.assertEqual(device.stack, stack)
        self.assertEqual(device.uid, 2)  # stacks .local has uid 1
        self.assertEqual(device.name, "Device{0}".format(device.uid))
        self.assertEqual(device.ha, ha)
        self.assertEqual(device.kind, None)
        self.assertEqual(device.host, ha[0])
        self.assertEqual(device.port, ha[1])

        device = devicing.IpRemoteDevice(stack=stack, ha=ha)
        self.assertIs(device.stack, stack)
        self.assertEqual(device.uid, 3)
        self.assertEqual(device.name, "Device{0}".format(device.uid))
        self.assertEqual(device.ha, ha)
        self.assertEqual(device.kind, None)
        self.assertEqual(device.host, ha[0])
        self.assertEqual(device.port, ha[1])

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
             'testDevice',
             'testUdpDevice',
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



