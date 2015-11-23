# -*- coding: utf-8 -*-
"""
Unit Test Template
"""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os

from ioflo.test import testing
from ioflo.aid.consoling import getConsole
console = getConsole()

from ioflo.aid import classing
from ioflo.base import registering

def setUpModule():
    console.reinit(verbosity=console.Wordage.concise)

def tearDownModule():
    pass


class BasicTestCase(unittest.TestCase):
    """
    Example TestCase
    """

    def setUp(self):
        """
        Call super if override so House Framer and Frame are setup correctly
        """
        super(BasicTestCase, self).setUp()

    def tearDown(self):
        """
        Call super if override so House Framer and Frame are torn down correctly
        """
        super(BasicTestCase, self).tearDown()

    def TestNonStringIterable(self):
        """
        Test the utility function nonStringIterable
        """
        console.terse("{0}\n".format(self.TestNonStringIterable.__doc__))
        a = bytearray(b'abc')
        w = dict(a=1, b=2, c=3)
        x = 'abc'
        y = b'abc'
        z = [1, 2, 3]

        self.assertTrue(isinstance(a, classing.NonStringIterable))
        self.assertTrue(isinstance(w, classing.NonStringIterable))
        self.assertFalse(isinstance(x, classing.NonStringIterable))
        self.assertFalse(isinstance(y, classing.NonStringIterable))
        self.assertTrue(isinstance(z, classing.NonStringIterable))


    def TestNonStringSequence(self):
        """
        Test the utility function nonStringSequence
        """
        console.terse("{0}\n".format(self.TestNonStringSequence.__doc__))
        a = bytearray(b'abc')
        w = dict(a=1, b=2, c=3)
        x = 'abc'
        y = b'abc'
        z = [1, 2, 3]

        self.assertTrue(isinstance(a, classing.NonStringIterable))
        self.assertFalse(isinstance(w, classing.NonStringSequence))
        self.assertFalse(isinstance(x, classing.NonStringSequence))
        self.assertFalse(isinstance(y, classing.NonStringSequence))
        self.assertTrue(isinstance(z, classing.NonStringSequence))

    def TestMetaclassify(self):
        """
        Test the utility decorator metaclassify
        """
        console.terse("{0}\n".format(self.TestMetaclassify.__doc__))

        @classing.metaclassify(registering.RegisterType)
        class A(object):
            #__metaclass__ = registering.RegisterType
            def __init__(self, name="", store=None):
                self.name = name
                self.store = store


        self.assertEqual(A.Registry, {'A': (A, None, None, None)})


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
    names = ['TestNonStringIterable',
             'TestNonStringSequence',
             'TestMetaclassify',
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

    #runOne('testBasic')


