# -*- coding: utf-8 -*-
"""
Unit Test Template
"""
from __future__ import absolute_import, division, print_function

import sys
import datetime
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os

from ioflo.aid.sixing import *
from ioflo.aid.odicting import odict
from ioflo.test import testing
from ioflo.aid.consoling import getConsole
console = getConsole()

from ioflo.aid import byting


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
        u = byting.binize(n, 8)
        self.assertEqual(u, '00000101')
        n = byting.unbinize(u)
        self.assertEqual(n, 5)

    def testBytifyUnbytify(self):
        """
        Test the bytify unbytify functions
        """
        console.terse("{0}\n".format(self.testBytifyUnbytify.__doc__))

        b = bytearray([1, 2, 3])
        n = byting.unbytify(b)
        self.assertEqual(n, 0x010203)
        n = byting.unbytify([1, 2, 3])
        self.assertEqual(n, 0x010203)
        n = byting.unbytify(b'\x01\x02\x03')
        self.assertEqual(n, 0x010203)

        b = byting.bytify(n)
        self.assertEqual(b, bytearray([1, 2, 3]))
        b = byting.bytify(n, 4)
        self.assertEqual(b, bytearray([0, 1, 2, 3]))
        b = byting.bytify(n, 2)
        self.assertEqual(b, bytearray([1, 2, 3]))

    def testPackifyUnpackify(self):
        """
        Test the packbits
        """
        console.terse("{0}\n".format(self.testPackifyUnpackify.__doc__))

        fmt = u'3 2 1 1'
        fields = [6, 2, True, False]
        size = 1
        packed = byting.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([212]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '11010100')

        fmt = u''
        fields = []
        size = 0
        packed = byting.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([]))

        fmt = u'3 1'
        fields = [5, True]
        size = 1
        packed = byting.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([0xb0]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '10110000')

        fmt = u'8 6 7 3'
        fields = [0xA5, 0x38, 0x08, 0x01]
        size = 3
        packed = byting.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([0xa5, 0xe0, 0x41]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '101001011110000001000001')
        # 0xa5e040

        fmt = u'3 2 1 1'
        packed = bytearray([212])
        fields = byting.unpackify(fmt=fmt, b=packed, boolean=True)
        self.assertEqual(fields, (6, 2, True, False, False))
        fields = byting.unpackify(fmt=fmt, b=packed, boolean=False)
        self.assertEqual(fields, (6, 2, 1, 0, 0))

        fmt = u''
        packed = bytearray([])
        fields = byting.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, tuple())

        fmt = u'3 1'
        packed = [0xb0]
        fields = byting.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, (5, 1, 0))

        fmt = u'4 3 1'
        packed = [0x0b]
        fields = byting.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, (0, 5, 1))

        fmt = u'8 6 7 3'
        packed = bytearray([0xa5, 0xe0, 0x41])
        fields = byting.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, (0xA5, 0x38, 0x08, 0x01))


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
             'testBytifyUnbytify',
             'testPackifyUnpackify',
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


