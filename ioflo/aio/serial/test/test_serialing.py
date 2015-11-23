# -*- coding: utf-8 -*-
"""
Unittests for serialing module
"""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os
import time
import tempfile
import shutil
import socket
import errno

from ioflo.aid.sixing import *
from ioflo.aid.consoling import getConsole
from ioflo.aio.serial import serialing

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

    def tearDown(self):
        """

        """

    def testConsoleNb(self):
        """
        Test Class ConsoleNB
        """
        console.terse("{0}\n".format(self.testConsoleNb.__doc__))

        myconsole = serialing.ConsoleNb()
        result = myconsole.open()
        #self.assertIs(result, False)
        #self.assertIs(result, True)

        #cout = "Enter 'hello' and hit return: "
        #myconsole.put(cout)
        #cin = ''
        #while not cin:
            #cin = myconsole.getLine()
        #myconsole.put("You typed: " + cin)
        #self.assertEqual('hello\n', cin)

        myconsole.close()



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
    names = ['testConsoleNb',
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

    #runOne('testClientAutoReconnect')


