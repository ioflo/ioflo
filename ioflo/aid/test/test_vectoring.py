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
import array

from ioflo.aid.sixing import *
from ioflo.test import testing
from ioflo.aid.consoling import getConsole


console = getConsole()

from ioflo.aid import vectoring


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

    def testMagnitude(self):
        """
        Test the mag and mag2 functions
        """
        console.terse("{0}\n".format(self.testMagnitude.__doc__))

        from ioflo.aid.vectoring import mag, mag2

        v = [1, 2, 3]  # list
        m = mag(v)
        self.assertAlmostEqual(m, 3.7416573867739413)

        m2 = mag2(v)
        self.assertEqual(m2, 14)

        v = (1, 2, 3)  # tuple
        m = mag(v)
        self.assertAlmostEqual(m, 3.7416573867739413)

        m2 = mag2(v)
        self.assertEqual(m2, 14)

        v = array.array('i', [1, 2, 3])  # array
        m = mag(v)
        self.assertAlmostEqual(m, 3.7416573867739413)

        m2 = mag2(v)
        self.assertEqual(m2, 14)

        v = bytearray([1, 2, 3])
        m = mag(v)
        self.assertAlmostEqual(m, 3.7416573867739413)

        m2 = mag2(v)
        self.assertEqual(m2, 14)

        v = [0, 0, 0]
        m = mag(v)
        self.assertEqual(m, 0.0)

        m2 = mag2(v)
        self.assertEqual(m2, 0.0)

        v = [1, 0, 0]
        m = mag(v)
        self.assertEqual(m, 1.0)

        m2 = mag2(v)
        self.assertEqual(m2, 1)

        v = [-1, -2, -3]  # list
        m = mag(v)
        self.assertAlmostEqual(m, 3.7416573867739413)

        m2 = mag2(v)
        self.assertEqual(m2, 14)

        v = [-1, 0.5, -2.5]  # list
        m = mag(v)
        self.assertAlmostEqual(m, 2.7386127875258306)

        m2 = mag2(v)
        self.assertEqual(m2, 7.5)

    def testNormalize(self):
        """
        Test the norm function
        """
        console.terse("{0}\n".format(self.testNormalize.__doc__))

        from ioflo.aid.vectoring import norm, mag

        v = [1, 2, 3]  # list
        n = norm(v)
        m = mag(n)
        self.assertAlmostEqual(m, 1.0)

        z = [0.2672612419124244, 0.5345224838248488, 0.8017837257372732]
        for e1, e2 in zip(n, z):
            self.assertAlmostEqual(e1, e2)

        v = [0, 0, 0]  # special case
        n = norm(v)
        m = mag(n)
        self.assertAlmostEqual(m, 0.0)

        v = [1, 0, 0]
        n = norm(v)
        m = mag(n)
        self.assertEqual(m, 1.0)

        z = [1.0, 0.0, 0.0]
        for e1, e2 in zip(n, z):
            self.assertEqual(e1, e2)

        v = [-1, -2, 3]  # list
        n = norm(v)
        m = mag(n)
        self.assertAlmostEqual(m, 1.0)

        z = [-0.2672612419124244, -0.5345224838248488, 0.8017837257372732]
        for e1, e2 in zip(n, z):
            self.assertAlmostEqual(e1, e2)

        v = (0.49999999999999994, 0.8660254037844386)
        n = norm(v, check=True)
        m = mag(n)
        self.assertEqual(m, 1.0)

    def testDotProduct(self):
        """
        Test the dot function
        """
        console.terse("{0}\n".format(self.testDotProduct.__doc__))

        from ioflo.aid.vectoring import dot, norm, mag

        u = [1, 2, 3]  # list
        v = [4, 5, 6]
        m = dot(u, v)
        self.assertEqual(m, 32)
        n = dot(v, u)
        self.assertEqual(m, n)

        v = [0, 0, 0]
        m = dot(u, v)
        self.assertEqual(m, 0.0)

        v = [0, 0, 1]
        m = dot(u, v)
        self.assertEqual(m, 3)
        self.assertEqual(m, u[2])

        v = [0, 0, -1]
        m = dot(u, v)
        self.assertEqual(m, -3)
        self.assertEqual(m, -u[2])

    def testPerp2Product(self):
        """
        Test the perp2 function
        """
        console.terse("{0}\n".format(self.testPerp2Product.__doc__))

        from ioflo.aid.vectoring import perp2, ccw, cw

        u = (1, 1)
        v = (-1, 1)
        m = perp2(u, v)
        self.assertEqual(m, 2)
        l = ccw(u, v)
        self.assertTrue(l)
        r = cw(u, v)
        self.assertFalse(r)

        n = perp2(v, u)
        self.assertEqual(n, -m)
        l = ccw(v, u)
        self.assertFalse(l)
        r = cw(v, u)
        self.assertTrue(r)

        p = perp2(u, u)
        self.assertEqual(p, 0)
        l = ccw(u, u)
        self.assertFalse(l)
        r = cw(u, u)
        self.assertFalse(r)

    def testCross3Product(self):
        """
        Test the dot function
        """
        console.terse("{0}\n".format(self.testCross3Product.__doc__))

        from ioflo.aid.vectoring import cross3

        u = (1, 2, 3)
        v = (-1, -2, 3)
        w = cross3(u, v)
        self.assertEqual(w, (12, -6, 0))

        u = (1, 1, 0)
        v = (-1, 1, 0)
        w = cross3(u, v)
        self.assertEqual(w, (0, 0, 2))

        w = cross3(v, u)
        self.assertEqual(w, (0, 0, -2))

    def testAddNeg(self):
        """
        Test the vector add and neg functions
        """
        console.terse("{0}\n".format(self.testAddNeg.__doc__))

        from ioflo.aid.vectoring import add, neg

        u = (1, 2, 3)
        v = (4, 5, 6)
        w = add(u, v)
        self.assertEqual(w, (5, 7, 9))

        w = neg(u)
        self.assertEqual(w, (-1, -2, -3))

        w = add(u, neg(v))
        self.assertEqual(w, (-3, -3, -3))






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
             'testMagnitude',
             'testNormalize',
             'testDotProduct',
             'testPerp2Product',
             'testCross3Product',
             'testAddNeg',
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


