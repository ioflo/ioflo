# -*- coding: utf-8 -*-
"""
Unit Test Template
"""
from __future__ import absolute_import, division, print_function

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os

from ioflo.aid.sixing import *
from ioflo.test import testing
from ioflo.base.consoling import getConsole
console = getConsole()

from ioflo.aid import aiding


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

    def testBinizeUnbinize(self):
        """
        Test the binize unbinize functions
        """
        console.terse("{0}\n".format(self.testBinizeUnbinize.__doc__))

        n = 5
        u = aiding.binize(n, 8)
        self.assertEqual(u, '00000101')
        n = aiding.unbinize(u)
        self.assertEqual(n, 5)

    def testIntifyBytify(self):
        """
        Test the intify bytify functions
        """
        console.terse("{0}\n".format(self.testIntifyBytify.__doc__))

        b = bytearray([1, 2, 3])
        n = aiding.unbytify(b)
        self.assertEqual(n, 0x010203)
        n = aiding.unbytify([1, 2, 3])
        self.assertEqual(n, 0x010203)
        n = aiding.unbytify(b'\x01\x02\x03')
        self.assertEqual(n, 0x010203)

        b = aiding.bytify(n)
        self.assertEqual(b, bytearray([1, 2, 3]))
        b = aiding.bytify(n, 4)
        self.assertEqual(b, bytearray([0, 1, 2, 3]))
        b = aiding.bytify(n, 2)
        self.assertEqual(b, bytearray([1, 2, 3]))

    def testPackify(self):
        """
        Test the packbits
        """
        console.terse("{0}\n".format(self.testPackify.__doc__))

        fmt = u'3211'
        fields = [6, 2, True, False]
        size = 1
        packed = aiding.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([212]))
        self.assertEqual(aiding.binize(aiding.unbytify(packed), size*8), '11010100')

        fmt = u''
        fields = []
        size = 0
        packed = aiding.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([]))

        fmt = u'31'
        fields = [5, True]
        size = 1
        packed = aiding.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([0xb0]))
        self.assertEqual(aiding.binize(aiding.unbytify(packed), size*8), '10110000')

        fmt = u'8673'
        fields = [0xA5, 0x38, 0x08, 0x01]
        size = 3
        packed = aiding.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([0xa5, 0xe0, 0x41]))
        self.assertEqual(aiding.binize(aiding.unbytify(packed), size*8), '101001011110000001000001')
        # 0xa5e040

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
             'testBinizeUnbinize',
             'testIntifyBytify',
             'testPackify',
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


