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

    def testTagify(self):
        """
        Test tagify function
        """
        console.terse("{0}\n".format(self.testTagify.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        tag = aiding.tagify()
        self.assertEqual(tag, u'')

        tag = aiding.tagify(head='exchange')
        self.assertEqual(tag, 'exchange')

        tag = aiding.tagify(head='exchange', tail='completed')
        self.assertEqual(tag, 'exchange.completed')

        tag = aiding.tagify(head='exchange', tail=['process', 'started'])
        self.assertEqual(tag, 'exchange.process.started')

        tag = aiding.tagify(head='exchange', tail=['process', 'started'], sep='/')
        self.assertEqual(tag, 'exchange/process/started')

        tag = aiding.tagify(tail=['process', 'started'])
        self.assertEqual(tag, 'process.started')

        console.reinit(verbosity=console.Wordage.concise)

    def testEventify(self):
        """
        Test eventify function
        """
        console.terse("{0}\n".format(self.testEventify.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        dt = datetime.datetime.utcnow()
        stamp = dt.isoformat()

        event = aiding.eventify('hello')
        self.assertEqual(event['tag'], 'hello')
        self.assertEqual(event['data'], {})
        #"YYYY-MM-DDTHH:MM:SS.mmmmmm"
        tdt = datetime.datetime.strptime(event['stamp'], "%Y-%m-%dT%H:%M:%S.%f")
        self.assertGreater(tdt, dt)

        event = aiding.eventify(tag=aiding.tagify(head='exchange', tail='started'),
                                stamp=stamp)
        self.assertEqual(event['tag'], 'exchange.started' )
        self.assertEqual(event['stamp'], stamp )

        event = aiding.eventify(tag=aiding.tagify(tail='started', head='exchange'),
                                stamp=stamp,
                                data = odict(name='John'))
        self.assertEqual(event['tag'], 'exchange.started')
        self.assertEqual(event['stamp'], stamp)
        self.assertEqual(event['data'], {'name':  'John',})

        stamp = '2015-08-10T19:26:47.194736'
        event = aiding.eventify(tag='process.started', stamp=stamp, data={'name': 'Jill',})
        self.assertEqual(event, {'tag': 'process.started',
                                 'stamp': '2015-08-10T19:26:47.194736',
                                 'data': {'name': 'Jill',},})

        event = aiding.eventify(tag="with uid", stamp=stamp, uid="abcde")
        self.assertEqual(event, {'data': {},
                                'stamp': '2015-08-10T19:26:47.194736',
                                'tag': 'with uid',
                                'uid': 'abcde'})

        console.reinit(verbosity=console.Wordage.concise)

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

    def testPackifyUnpackify(self):
        """
        Test the packbits
        """
        console.terse("{0}\n".format(self.testPackifyUnpackify.__doc__))

        fmt = u'3 2 1 1'
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

        fmt = u'3 1'
        fields = [5, True]
        size = 1
        packed = aiding.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([0xb0]))
        self.assertEqual(aiding.binize(aiding.unbytify(packed), size*8), '10110000')

        fmt = u'8 6 7 3'
        fields = [0xA5, 0x38, 0x08, 0x01]
        size = 3
        packed = aiding.packify(fmt=fmt, fields=fields, size=size)
        self.assertEqual(packed, bytearray([0xa5, 0xe0, 0x41]))
        self.assertEqual(aiding.binize(aiding.unbytify(packed), size*8), '101001011110000001000001')
        # 0xa5e040

        fmt = u'3 2 1 1'
        packed = bytearray([212])
        fields = aiding.unpackify(fmt=fmt, b=packed, boolean=True)
        self.assertEqual(fields, (6, 2, True, False, False))
        fields = aiding.unpackify(fmt=fmt, b=packed, boolean=False)
        self.assertEqual(fields, (6, 2, 1, 0, 0))

        fmt = u''
        packed = bytearray([])
        fields = aiding.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, tuple())

        fmt = u'3 1'
        packed = [0xb0]
        fields = aiding.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, (5, 1, 0))

        fmt = u'4 3 1'
        packed = [0x0b]
        fields = aiding.unpackify(fmt=fmt, b=packed)
        self.assertEqual(fields, (0, 5, 1))

        fmt = u'8 6 7 3'
        packed = bytearray([0xa5, 0xe0, 0x41])
        fields = aiding.unpackify(fmt=fmt, b=packed)
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
             'testTagify',
             'testEventify',
             'testBinizeUnbinize',
             'testIntifyBytify',
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


