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



