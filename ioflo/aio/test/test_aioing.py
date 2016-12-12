# -*- coding: utf-8 -*-
"""
Unittests for aioing module

"""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os
import tempfile
import shutil

from ioflo.aid.sixing import *
from ioflo.aid.consoling import getConsole
from ioflo.aio import aioing

console = getConsole()


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
        pass


    def tearDown(self):
        """

        """
        pass

    def testNormalizeHost(self):
        """
        Test normalizeHost function
        """
        console.terse("{0}\n".format(self.testNormalizeHost.__doc__))

        host = aioing.normalizeHost("")
        self.assertEqual(host, "0.0.0.0")
        host = aioing.normalizeHost("::")
        self.assertEqual(host, "::")


        host = aioing.normalizeHost("216.58.193.78")
        self.assertEqual(host, "216.58.193.78")
        host = aioing.normalizeHost("2607:f8b0:400a:809::200e")
        self.assertEqual(host, '2607:f8b0:400a:809::200e')


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
             'testNormalizeHost',
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

    #console.reinit(verbosity=console.Wordage.concise)

    #runAll() #run all unittests

    runSome()#only run some

    #runOne('testClientAutoReconnect')


