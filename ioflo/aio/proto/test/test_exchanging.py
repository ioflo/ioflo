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

from ioflo.aio.proto import exchanging, devicing, stacking

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

    def testExchange(self):
        """
        Test Exchange class
        """
        console.terse("{0}\n".format(self.testExchange.__doc__))

        stack = stacking.Stack()
        exchange = exchanging.Exchange(stack=stack)
        self.assertIs(exchange.stack, stack)
        self.assertEqual(len(exchange.uid), 24)
        self.assertEqual(exchange.name, 'Exchange')
        self.assertIs(exchange.device, None)


        exchanger = exchanging.Exchanger(stack=stack)
        self.assertIs(exchanger.stack, stack)
        self.assertEqual(len(exchanger.uid), 24)
        self.assertEqual(exchanger.name, 'Exchanger')
        self.assertIs(exchanger.device, None)

        exchangent = exchanging.Exchangent(stack=stack)
        self.assertIs(exchangent.stack, stack)
        self.assertEqual(len(exchanger.uid), 24)
        self.assertEqual(exchangent.name, 'Exchangent')
        self.assertIs(exchangent.device, None)


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
             'testExchange',
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



