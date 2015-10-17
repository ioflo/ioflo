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
from ioflo.aid.consoling import getConsole
console = getConsole()

from ioflo.aid import blending


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

    def testBlending(self):
        """
        Test the blend functions
        """
        console.terse("{0}\n".format(self.testBlending.__doc__))
        u = .25
        s = .75
        steps = 10
        u = abs(u)
        s = abs(s)
        steps = abs(steps)
        span = u + s
        ss = span / steps
        out = []
        for x in xrange(-(steps + 1), steps + 2, 1):
            d = x * ss
            b = blending.blend0(d,u,s)
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(-1.1, 0.0),
                                (-1.0, 0.0),
                                (-0.9, 0.133),
                                (-0.8, 0.267),
                                (-0.7, 0.4),
                                (-0.6, 0.533),
                                (-0.5, 0.667),
                                (-0.4, 0.8),
                                (-0.3, 0.933),
                                (-0.2, 1.0),
                                (-0.1, 1.0),
                                (0.0, 1.0),
                                (0.1, 1.0),
                                (0.2, 1.0),
                                (0.3, 0.933),
                                (0.4, 0.8),
                                (0.5, 0.667),
                                (0.6, 0.533),
                                (0.7, 0.4),
                                (0.8, 0.267),
                                (0.9, 0.133),
                                (1.0, 0.0),
                                (1.1, 0.0)])

        out = []
        for x in xrange(-(steps + 1), steps + 2, 1):
            d = x * ss
            b = blending.blend1(d,u,s)
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(-1.1, 1.0),
                                (-1.0, 1.0),
                                (-0.9, 1.0),
                                (-0.8, 1.0),
                                (-0.7, 1.0),
                                (-0.6, 1.0),
                                (-0.5, 1.0),
                                (-0.4, 1.0),
                                (-0.3, 1.0),
                                (-0.2, 1.0),
                                (-0.1, 0.564),
                                (0.0, 0.0),
                                (0.1, 0.564),
                                (0.2, 1.0),
                                (0.3, 1.0),
                                (0.4, 1.0),
                                (0.5, 1.0),
                                (0.6, 1.0),
                                (0.7, 1.0),
                                (0.8, 1.0),
                                (0.9, 1.0),
                                (1.0, 1.0),
                                (1.1, 1.0)])

        out = []
        for x in xrange(-(steps + 1), steps + 2, 1):
            d = x * ss
            b = blending.blend2(d,u,s)
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(-1.1, 1.0),
                                (-1.0, 1.0),
                                (-0.9, 1.0),
                                (-0.8, 1.0),
                                (-0.7, 0.997),
                                (-0.6, 0.987),
                                (-0.5, 0.95),
                                (-0.4, 0.853),
                                (-0.3, 0.66),
                                (-0.2, 0.381),
                                (-0.1, 0.113),
                                (0.0, 0.0),
                                (0.1, 0.113),
                                (0.2, 0.381),
                                (0.3, 0.66),
                                (0.4, 0.853),
                                (0.5, 0.95),
                                (0.6, 0.987),
                                (0.7, 0.997),
                                (0.8, 1.0),
                                (0.9, 1.0),
                                (1.0, 1.0),
                                (1.1, 1.0)])

        out = []
        for x in xrange(-(steps + 1), steps + 2, 1):
            d = x * ss
            b = blending.blend3(d,u,s)
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(-1.1, 0.996),
                                (-1.0, 0.99),
                                (-0.9, 0.976),
                                (-0.8, 0.947),
                                (-0.7, 0.895),
                                (-0.6, 0.809),
                                (-0.5, 0.684),
                                (-0.4, 0.521),
                                (-0.3, 0.339),
                                (-0.2, 0.168),
                                (-0.1, 0.045),
                                (0.0, 0.0),
                                (0.1, 0.045),
                                (0.2, 0.168),
                                (0.3, 0.339),
                                (0.4, 0.521),
                                (0.5, 0.684),
                                (0.6, 0.809),
                                (0.7, 0.895),
                                (0.8, 0.947),
                                (0.9, 0.976),
                                (1.0, 0.99),
                                (1.1, 0.996)])

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
    names = ['testBlending',
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


