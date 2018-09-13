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

        out = []
        for x in xrange(-(steps + 1), steps + 2, 1):
            d = x * ss
            b = blending.blendSpike(d, u, s)
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(-1.1, 0.363),
                               (-1.0, 0.392),
                               (-0.9, 0.422),
                               (-0.8, 0.455),
                               (-0.7, 0.49),
                               (-0.6, 0.529),
                               (-0.5, 0.57),
                               (-0.4, 0.614),
                               (-0.3, 0.662),
                               (-0.2, 0.714),
                               (-0.1, 0.769),
                               (0.0, 0.829),
                               (0.1, 0.894),
                               (0.2, 0.963),
                               (0.3, 0.963),
                               (0.4, 0.894),
                               (0.5, 0.829),
                               (0.6, 0.769),
                               (0.7, 0.714),
                               (0.8, 0.662),
                               (0.9, 0.614),
                               (1.0, 0.57),
                               (1.1, 0.529)])

        out = []
        for x in xrange(-(steps + 1), steps + 2, 1):
            d = x * ss
            b = blending.blendSigmoidInc(d, u, s)
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(-1.1, 0.266),
                               (-1.0, 0.281),
                               (-0.9, 0.297),
                               (-0.8, 0.313),
                               (-0.7, 0.329),
                               (-0.6, 0.346),
                               (-0.5, 0.363),
                               (-0.4, 0.38),
                               (-0.3, 0.398),
                               (-0.2, 0.416),
                               (-0.1, 0.435),
                               (0.0, 0.453),
                               (0.1, 0.472),
                               (0.2, 0.491),
                               (0.3, 0.509),
                               (0.4, 0.528),
                               (0.5, 0.547),
                               (0.6, 0.565),
                               (0.7, 0.584),
                               (0.8, 0.602),
                               (0.9, 0.62),
                               (1.0, 0.637),
                               (1.1, 0.654)])

        out = []
        for x in xrange(-(steps + 1), steps + 2, 1):
            d = x * ss
            b = blending.blendSigmoidDec(d, u, s)
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(-1.1, 0.734),
                               (-1.0, 0.719),
                               (-0.9, 0.703),
                               (-0.8, 0.687),
                               (-0.7, 0.671),
                               (-0.6, 0.654),
                               (-0.5, 0.637),
                               (-0.4, 0.62),
                               (-0.3, 0.602),
                               (-0.2, 0.584),
                               (-0.1, 0.565),
                               (0.0, 0.547),
                               (0.1, 0.528),
                               (0.2, 0.509),
                               (0.3, 0.491),
                               (0.4, 0.472),
                               (0.5, 0.453),
                               (0.6, 0.435),
                               (0.7, 0.416),
                               (0.8, 0.398),
                               (0.9, 0.38),
                               (1.0, 0.363),
                               (1.1, 0.346)])

        out = []
        for x in xrange(-(steps + 1), steps + 2, 1):
            d = x * ss
            b = blending.blendConcaveInc(d, 0)  
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(-1.1, 0.323),
                               (-1.0, 0.333),
                               (-0.9, 0.345),
                               (-0.8, 0.357),
                               (-0.7, 0.37),
                               (-0.6, 0.385),
                               (-0.5, 0.4),
                               (-0.4, 0.417),
                               (-0.3, 0.435),
                               (-0.2, 0.455),
                               (-0.1, 0.476),
                               (0.0, 0.5),
                               (0.1, 0.526),
                               (0.2, 0.556),
                               (0.3, 0.588),
                               (0.4, 0.625),
                               (0.5, 0.667),
                               (0.6, 0.714),
                               (0.7, 0.769),
                               (0.8, 0.833),
                               (0.9, 0.909),
                               (1.0, 1.0),
                               (1.1, 1.0)])

        out = []
        for x in xrange((steps), steps + 20, 1):
            d = x * ss
            b = blending.blendConcaveDec(d)  
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(1.0, 1.0),
                               (1.1, 0.909),
                               (1.2, 0.833),
                               (1.3, 0.769),
                               (1.4, 0.714),
                               (1.5, 0.667),
                               (1.6, 0.625),
                               (1.7, 0.588),
                               (1.8, 0.556),
                               (1.9, 0.526),
                               (2.0, 0.5),
                               (2.1, 0.476),
                               (2.2, 0.455),
                               (2.3, 0.435),
                               (2.4, 0.417),
                               (2.5, 0.4),
                               (2.6, 0.385),
                               (2.7, 0.37),
                               (2.8, 0.357),
                               (2.9, 0.345)])

        out = []
        for x in xrange((steps - 5), steps + 15, 1):
            d = x * ss
            b = blending.blendConcaveCombined(d)  
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(0.5, 0.5), 
                                (0.6, 0.556), 
                                (0.7, 0.625), 
                                (0.8, 0.714), 
                                (0.9, 0.833), 
                                (1.0, 1.0), 
                                (1.1, 1.0), 
                                (1.2, 1.0), 
                                (1.3, 1.0), 
                                (1.4, 1.0), 
                                (1.5, 1.0), 
                                (1.6, 0.833), 
                                (1.7, 0.714), 
                                (1.8, 0.625), 
                                (1.9, 0.556), 
                                (2.0, 0.5), 
                                (2.1, 0.455), 
                                (2.2, 0.417), 
                                (2.3, 0.385), 
                                (2.4, 0.357)])

        out = []
        for x in range(-(steps + 1), steps + 2, 1):
            d = x * ss
            b = blending.blendTriangular(d, 0)  
            out.append((round(d, 3), round(b, 3)))

        self.assertEqual(out, [(-1.1, 0.0), 
                                (-1.0, 0.0), 
                                (-0.9, 0.0), 
                                (-0.8, 0.0), 
                                (-0.7, 0.0), 
                                (-0.6, 0.0), 
                                (-0.5, 0.0), 
                                (-0.4, 0.0), 
                                (-0.3, 0.0), 
                                (-0.2, 0.0), 
                                (-0.1, 0.0), 
                                (0.0, 0.0), 
                                (0.1, 0.25), 
                                (0.2, 0.5), 
                                (0.3, 0.75), 
                                (0.4, 1.0), 
                                (0.5, 0.8), 
                                (0.6, 0.6), 
                                (0.7, 0.4), 
                                (0.8, 0.2), 
                                (0.9, 0.0), 
                                (1.0, 0.0), 
                                (1.1, 0.0)])


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


