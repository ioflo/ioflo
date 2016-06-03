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
        b = byting.bytify(n, 2, strict=True)
        self.assertEqual(b, bytearray([2, 3]))

        b = bytearray([1, 2, 3])
        n = byting.unbytify(b, reverse=True)
        self.assertEqual(n, 0x030201)
        n = byting.unbytify([1, 2, 3], reverse=True)
        self.assertEqual(n, 0x030201)
        n = byting.unbytify(b'\x01\x02\x03', reverse=True)
        self.assertEqual(n, 0x030201)

        b = byting.bytify(n, reverse=True)
        self.assertEqual(b, bytearray([1, 2, 3]))
        b = byting.bytify(n, 4, reverse=True)
        self.assertEqual(b, bytearray([1, 2, 3, 0]))
        b = byting.bytify(n, 2, reverse=True)
        self.assertEqual(b, bytearray([1, 2, 3]))
        b = byting.bytify(n, 2, reverse=True, strict=True)
        self.assertEqual(b, bytearray([1, 2]))

        n = -1
        b = byting.bytify(n)
        self.assertEqual(b, bytearray([0xff]))
        b = byting.bytify(n, 4)
        self.assertEqual(b, bytearray([0xff, 0xff, 0xff, 0xff]))
        n = -2
        b = byting.bytify(n)
        self.assertEqual(b, bytearray([0xfe]))
        b = byting.bytify(n, 2)
        self.assertEqual(b, bytearray([0xff, 0xfe]))

        n = 0x007ffb
        b = byting.bytify(n, 3)
        self.assertEqual(b, bytearray([0x00, 0x7f, 0xfb]))
        b = byting.bytify(n, 3, reverse=True)
        self.assertEqual(b, bytearray([0xfb, 0x7f, 0x00]))


    def testPackifyUnpackify(self):
        """
        Test the packbits
        """
        console.terse("{0}\n".format(self.testPackifyUnpackify.__doc__))

        fmt = u'3 2 1 1'
        fields = [6, 2, True, False]
        size = 1
        packed = byting.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([0xd4]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '11010100')

        packed = byting.packify(fmt=fmt, fields=fields)
        self.assertEqual(packed, bytearray([0xd4]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '11010100')

        fmt = u''
        fields = []
        size = 0
        packed = byting.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([]))

        packed = byting.packify(fmt=fmt, fields=fields)
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
        packed = byting.packify(fmt=fmt, fields=fields)
        self.assertEqual(packed, bytearray([0xa5, 0xe0, 0x41]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '101001011110000001000001')

        fmt = u'8 6 7 3'
        fields = [0xA5, 0x38, 0x08, 0x01]
        size = 4
        packed = byting.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([0xa5, 0xe0, 0x41, 0x00]))

        fmt = u'3 2 1 1'
        packed = bytearray([0xd4])
        fields = byting.unpackify(fmt=fmt, b=packed, boolean=True)
        self.assertEqual(fields, (6, 2, True, False, False))
        fields = byting.unpackify(fmt=fmt, b=packed, boolean=False)
        self.assertEqual(fields, (6, 2, 1, 0, 0))

        fmt = u''
        packed = bytearray([])
        fields = byting.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, tuple())

        fmt = u'3 1'
        packed = bytearray([0xb0])
        fields = byting.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, (5, 1, 0))

        fmt = u'4 3 1'
        packed = [0x0b]  # converts to bytearray in parameter
        fields = byting.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, (0, 5, 1))

        fmt = u'8 6 7 3'
        packed = bytearray([0xa5, 0xe0, 0x41])
        fields = byting.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, (0xA5, 0x38, 0x08, 0x01))

        fmt = u'8 6 7 3'
        packed = bytearray([0xa5, 0xe0, 0x41, 0xff, 0xff])
        fields = byting.unpackify(fmt=fmt, b=packed, size=3)
        self.assertEqual(fields, (0xA5, 0x38, 0x08, 0x01))

        fmt = u'3 2 1 1'
        fields = [6, 2, True, False]
        size = 1
        packed = byting.packify(fmt=fmt, fields=fields, size=size, reverse=True)
        self.assertEqual(packed, bytearray([0xd4]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '11010100')

        packed = byting.packify(fmt=fmt, fields=fields, reverse=True)
        self.assertEqual(packed, bytearray([0xd4]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '11010100')

        fmt = u''
        fields = []
        size = 0
        packed = byting.packify(fmt=fmt, fields=fields, size=size, reverse=True)
        self.assertEqual(packed, bytearray([]))

        packed = byting.packify(fmt=fmt, fields=fields, reverse=True)
        self.assertEqual(packed, bytearray([]))

        fmt = u'3 1'
        fields = [5, True]
        size = 1
        packed = byting.packify(fmt=fmt, fields=fields, size=size, reverse=True)
        self.assertEqual(packed, bytearray([0xb0]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '10110000')

        fmt = u'8 6 7 3'
        fields = [0xA5, 0x38, 0x08, 0x01]
        size = 3
        packed = byting.packify(fmt=fmt, fields=fields, size=size, reverse=True)
        self.assertEqual(packed, bytearray([0x41, 0xe0, 0xa5]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '010000011110000010100101')
        # 0xa5e040
        packed = byting.packify(fmt=fmt, fields=fields, reverse=True)
        self.assertEqual(packed, bytearray([0x41, 0xe0, 0xa5]))
        self.assertEqual(byting.binize(byting.unbytify(packed), size*8), '010000011110000010100101')

        fmt = u'8 6 7 3'
        fields = [0xA5, 0x38, 0x08, 0x01]
        size = 4
        packed = byting.packify(fmt=fmt, fields=fields, size=size, reverse=True)
        self.assertEqual(packed, bytearray([0x00, 0x41, 0xe0, 0xa5]))

        fmt = u'3 2 1 1'
        packed = bytearray([212])
        fields = byting.unpackify(fmt=fmt, b=packed, boolean=True, reverse=True)
        self.assertEqual(fields, (6, 2, True, False, False))
        fields = byting.unpackify(fmt=fmt, b=packed, boolean=False, reverse=True)
        self.assertEqual(fields, (6, 2, 1, 0, 0))

        fmt = u''
        packed = bytearray([])
        fields = byting.unpackify(fmt=fmt, b=packed, reverse=True)
        self.assertEqual(fields, tuple())

        fmt = u'3 1'
        packed = bytearray([0xb0])
        fields = byting.unpackify(fmt=fmt, b=packed, reverse=True)
        self.assertEqual(fields, (5, 1, 0))

        fmt = u'4 3 1'
        packed = [0x0b]  # converts to bytearray in parameter
        fields = byting.unpackify(fmt=fmt, b=packed, reverse=True)
        self.assertEqual(fields, (0, 5, 1))

        fmt = u'8 6 7 3'
        packed = bytearray([0xa5, 0xe0, 0x41])
        fields = byting.unpackify(fmt=fmt, b=packed, reverse=True)
        self.assertEqual(fields, (0x41, 0x38, 0x14, 0x05))

        fmt = u'8 6 7 3'
        packed = bytearray([0xff, 0xff, 0xa5, 0xe0, 0x41])
        fields = byting.unpackify(fmt=fmt, b=packed, size=3, reverse=True)
        self.assertEqual(fields, (0x41, 0x38, 0x14, 0x05))


    def testPackifyInto(self):
        """
        Test the packbits
        """
        console.terse("{0}\n".format(self.testPackifyInto.__doc__))

        fmt = u'3 2 1 1'
        fields = [6, 2, True, False]
        b = bytearray([0, 0, 0, 0, 0, 0])
        size = byting.packifyInto(b, fmt=fmt, fields=fields, size=1)
        self.assertEqual(size, 1)
        self.assertEqual(b, bytearray([212, 0, 0, 0, 0, 0]))
        self.assertEqual(byting.binize(b[0]), '11010100')

        size = byting.packifyInto(b, fmt=fmt, fields=fields, size=1, offset=2)
        self.assertEqual(size, 1)
        self.assertEqual(b, bytearray([212, 0, 212, 0, 0, 0]))
        self.assertEqual(byting.binize(b[2]), '11010100')

        b[0] =  0x0
        self.assertEqual(b, bytearray([0, 0, 212, 0, 0, 0]))
        size = byting.packifyInto(b, fmt=fmt, fields=fields)
        self.assertEqual(size, 1)
        self.assertEqual(b, bytearray([212, 0, 212, 0, 0, 0]))
        self.assertEqual(byting.binize(b[0]), '11010100')

        b = bytearray([0, 0, 0, 0, 0, 0])
        fmt = u''
        fields = []
        size = byting.packifyInto(b, fmt=fmt, fields=fields, size=0)
        self.assertEqual(size, 0)
        self.assertEqual(b, bytearray([0, 0, 0, 0, 0, 0]))

        size = byting.packifyInto(b, fmt=fmt, fields=fields)
        self.assertEqual(size, 0)
        self.assertEqual(b, bytearray([0, 0, 0, 0, 0, 0]))

        fmt = u'3 1'
        fields = [5, True]
        size = byting.packifyInto(b, fmt=fmt, fields=fields, size=1)
        self.assertEqual(size, 1)
        self.assertEqual(b, bytearray([176, 0, 0, 0, 0, 0]))
        self.assertEqual(byting.binize(b[0]), '10110000')

        b = bytearray([0, 0, 0, 0, 0, 0])
        fmt = u'8 6 7 3'
        fields = [0xA5, 0x38, 0x08, 0x01]
        size = byting.packifyInto(b, fmt=fmt, fields=fields)
        self.assertEqual(size, 3)
        self.assertEqual(b, bytearray([0xa5, 0xe0, 0x41, 0, 0, 0]))

        b = bytearray([0, 0, 0, 0, 0, 0])
        size = byting.packifyInto(b, fmt=fmt, fields=fields, offset=1)
        self.assertEqual(size, 3)
        self.assertEqual(b, bytearray([0, 0xa5, 0xe0, 0x41, 0, 0]))

        b = bytearray()
        fmt = u'8 6 7 3'
        fields = [0xA5, 0x38, 0x08, 0x01]
        size = byting.packifyInto(b, fmt=fmt, fields=fields)
        self.assertEqual(size, 3)
        self.assertEqual(b, bytearray([0xa5, 0xe0, 0x41]))

        fmt = u'3 2 1 1'
        fields = [6, 2, True, False]
        b = bytearray([0, 0, 0, 0, 0, 0])
        size = byting.packifyInto(b, fmt=fmt, fields=fields, size=1, reverse=True)
        self.assertEqual(size, 1)
        self.assertEqual(b, bytearray([212, 0, 0, 0, 0, 0]))
        self.assertEqual(byting.binize(b[0]), '11010100')

        size = byting.packifyInto(b, fmt=fmt, fields=fields, size=1, offset=2, reverse=True)
        self.assertEqual(size, 1)
        self.assertEqual(b, bytearray([212, 0, 212, 0, 0, 0]))
        self.assertEqual(byting.binize(b[2]), '11010100')

        b[0] =  0x0
        self.assertEqual(b, bytearray([0, 0, 212, 0, 0, 0]))
        size = byting.packifyInto(b, fmt=fmt, fields=fields, reverse=True)
        self.assertEqual(size, 1)
        self.assertEqual(b, bytearray([212, 0, 212, 0, 0, 0]))
        self.assertEqual(byting.binize(b[0]), '11010100')

        b = bytearray([0, 0, 0, 0, 0, 0])
        fmt = u''
        fields = []
        size = byting.packifyInto(b, fmt=fmt, fields=fields, size=0, reverse=True)
        self.assertEqual(size, 0)
        self.assertEqual(b, bytearray([0, 0, 0, 0, 0, 0]))

        size = byting.packifyInto(b, fmt=fmt, fields=fields, reverse=True)
        self.assertEqual(size, 0)
        self.assertEqual(b, bytearray([0, 0, 0, 0, 0, 0]))

        fmt = u'3 1'
        fields = [5, True]
        size = byting.packifyInto(b, fmt=fmt, fields=fields, size=1, reverse=True)
        self.assertEqual(size, 1)
        self.assertEqual(b, bytearray([176, 0, 0, 0, 0, 0]))
        self.assertEqual(byting.binize(b[0]), '10110000')

        b = bytearray([0, 0, 0, 0, 0, 0])
        fmt = u'8 6 7 3'
        fields = [0xA5, 0x38, 0x08, 0x01]
        size = byting.packifyInto(b, fmt=fmt, fields=fields, reverse=True)
        self.assertEqual(size, 3)
        self.assertEqual(b, bytearray([0x41, 0xe0, 0xa5, 0, 0, 0]))

        b = bytearray([0, 0, 0, 0, 0, 0])
        size = byting.packifyInto(b, fmt=fmt, fields=fields, offset=1, reverse=True)
        self.assertEqual(size, 3)
        self.assertEqual(b, bytearray([0, 0x41, 0xe0, 0xa5, 0, 0]))

        b = bytearray()
        fmt = u'8 6 7 3'
        fields = [0xA5, 0x38, 0x08, 0x01]
        size = byting.packifyInto(b, fmt=fmt, fields=fields, reverse=True)
        self.assertEqual(size, 3)
        self.assertEqual(b, bytearray([0x41, 0xe0, 0xa5]))

    def testSignExtend(self):
        """
        Test the signExtend function
        """
        console.terse("{0}\n".format(self.testSignExtend.__doc__))
        a =( 2 ** 8) - 11  # 8 bit two's complement rep of -11
        self.assertEqual(a, 0xf5)
        b = bytearray([0xf5])  # make bytearray
        y, x = byting.unpackify(fmt='3 5', b=b)  # assign lower 5 bits to x
        self.assertEqual(x, 0x15)
        z = byting.signExtend(x, n=5)
        self.assertEqual(z, -11)

        a = 11
        self.assertEqual(a, 0x0b)
        b = bytearray([0x0b])
        y, x = byting.unpackify(fmt='3 5', b=b)  # assign lower 5 bits to x
        self.assertEqual(x, 0x0b)
        z = byting.signExtend(x, n=5)
        self.assertEqual(z, 11)

        a = (2 ** 8) - 16
        self.assertEqual(a, 0xf0)
        b = bytearray([0xf0])  # make bytearray
        y, x = byting.unpackify(fmt='3 5', b=b)  # assign lower 5 bits to x
        self.assertEqual(x, 0x10)
        z = byting.signExtend(x, n=5)
        self.assertEqual(z, -16)

        a = 15
        self.assertEqual(a, 0x0f)
        b = bytearray([0x0f])
        y, x = byting.unpackify(fmt='3 5', b=b)  # assign lower 5 bits to x
        self.assertEqual(x, 0x0f)
        z = byting.signExtend(x, n=5)
        self.assertEqual(z, 15)

        a = 0
        self.assertEqual(a, 0x00)
        b = bytearray([0x00])
        y, x = byting.unpackify(fmt='3 5', b=b)  # assign lower 5 bits to x
        self.assertEqual(x, 0x00)
        z = byting.signExtend(x, n=5)
        self.assertEqual(z, 0)



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
             'testPackifyInto',
             'testSignExtend',
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


