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

    def testAddNegSubMult(self):
        """
        Test the vector add and neg and sub multfunctions
        """
        console.terse("{0}\n".format(self.testAddNegSubMult.__doc__))

        from ioflo.aid.vectoring import add, neg, sub, mult

        u = (1, 2, 3)
        v = (4, 5, 6)
        w = add(u, v)
        self.assertEqual(w, (5, 7, 9))

        w = neg(u)
        self.assertEqual(w, (-1, -2, -3))

        w = add(u, neg(v))
        self.assertEqual(w, (-3, -3, -3))

        w = sub(u, v)
        self.assertEqual(w, (-3, -3, -3))

        w = mult(2, u)
        self.assertEqual(w, (2, 4, 6))

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

    def testProjection(self):
        """
        Test the proj function
        """
        console.terse("{0}\n".format(self.testProjection.__doc__))

        from ioflo.aid.vectoring import proj

        u = [1, 2, 3]  # list
        v = [4, 5, 6]
        w = proj(u, v)
        vv = (1.6623376623376622, 2.0779220779220777, 2.493506493506493)
        for e1, e2 in zip(w, vv):
            self.assertAlmostEqual(e1, e2)

        u = [0, 0, 1]
        v = [0, 0, 2]
        w = proj(u, v)
        self.assertEqual(w, (0.0, 0.0, 1.0))

        u = [0, 0, 1]
        v = [0, 0, 0]
        w = proj(u, v)
        self.assertEqual(w, (0, 0, 0))

    def testTrip(self):
        """
        Test the trip function
        """
        console.terse("{0}\n".format(self.testTrip.__doc__))

        from ioflo.aid.vectoring import trip, ccw, cw

        u = (1, 1)
        v = (-1, 1)
        m = trip(u, v)
        self.assertEqual(m, 2)
        l = ccw(u, v)
        self.assertTrue(l)
        r = cw(u, v)
        self.assertFalse(r)

        n = trip(v, u)
        self.assertEqual(n, -m)
        l = ccw(v, u)
        self.assertFalse(l)
        r = cw(v, u)
        self.assertTrue(r)

        p = trip(u, u)
        self.assertEqual(p, 0)
        l = ccw(u, u)
        self.assertFalse(l)
        r = cw(u, u)
        self.assertFalse(r)

    def testTween(self):
        """
        Test the tween functions
        """
        console.terse("{0}\n".format(self.testTween.__doc__))

        from ioflo.aid.vectoring import tween, tween2

        p = (3, 3, 3)
        u = (2, 2, 2)
        v = (4, 4, 4)
        result = tween(p, u, v)
        self.assertTrue(result)

        p = (5, 5, 5)
        u = (2, 2, 2)
        v = (4, 4, 4)
        result = tween(p, u, v)
        self.assertFalse(result)

        p = (1, 1, 1)
        u = (2, 2, 2)
        v = (4, 4, 4)
        result = tween(p, u, v)
        self.assertFalse(result)

        p = (3, 3, 0)
        u = (2, 2, 2)
        v = (4, 4, 4)
        result = tween(p, u, v)
        self.assertFalse(result)

        p = (2, 2, 2)
        u = (2, 2, 2)
        v = (4, 4, 4)
        result = tween(p, u, v)
        self.assertTrue(result)

        p = (4, 4, 4)
        u = (2, 2, 2)
        v = (4, 4, 4)
        result = tween(p, u, v)
        self.assertTrue(result)

        p = (2, 2, 2)
        u = (2, 2, 2)
        v = (2, 2, 2)
        result = tween(p, u, v)
        self.assertTrue(result)

        p = (4, 4, 4)
        u = (2, 2, 2)
        v = (2, 2, 2)
        result = tween(p, u, v)
        self.assertFalse(result)

        p = (3, 3)
        u = (2, 2)
        v = (4, 4)
        result = tween2(p, u, v)
        self.assertTrue(result)

        p = (5, 5)
        u = (2, 2)
        v = (4, 4)
        result = tween2(p, u, v)
        self.assertFalse(result)

        p = (1, 1)
        u = (2, 2)
        v = (4, 4)
        result = tween2(p, u, v)
        self.assertFalse(result)

        p = (3, 0)
        u = (2, 2)
        v = (4, 4)
        result = tween2(p, u, v)
        self.assertFalse(result)

        p = (2, 2)
        u = (2, 2)
        v = (4, 4)
        result = tween2(p, u, v)
        self.assertTrue(result)

        p = (4, 4)
        u = (2, 2)
        v = (4, 4)
        result = tween2(p, u, v)
        self.assertTrue(result)

        p = (2, 2)
        u = (2, 2)
        v = (2, 2)
        result = tween2(p, u, v)
        self.assertTrue(result)

        p = (4, 4)
        u = (2, 2)
        v = (2, 2)
        result = tween2(p, u, v)
        self.assertFalse(result)



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


    def testWind(self):
        """
        Test the winding count of point in polygon test
        """
        console.terse("{0}\n".format(self.testWind.__doc__))

        from ioflo.aid.vectoring import wind, inside

        # counter clockwise wind
        p = (1, 1)
        vs = ((0, 0), (2, 0), (2, 2), (0, 2))  # ccw
        ccw = wind(p, vs)
        self.assertEqual(ccw, 1)
        self.assertTrue(inside(p, vs))

        # clockwise wind
        vs = ((0, 0), (0, 2), (2, 2), (2, 0)) # cw
        cw = wind(p, vs)
        self.assertEqual(cw, -1)
        self.assertEqual(cw, -ccw)
        self.assertTrue(inside(p, vs))

        # point not in polygon
        p = (-1, -1)
        vs = ((0, 0), (2, 0), (2, 2), (0, 2))  # ccw
        w = wind(p, vs)
        self.assertEqual(w, 0)
        self.assertFalse(inside(p, vs))

        vs = ((0, 0), (0, 2), (2, 2), (2, 0)) # cw
        w = wind(p, vs)
        self.assertEqual(w, 0)
        self.assertFalse(inside(p, vs))

        # point is vertex and is not in polygon
        p = (2, 0)
        vs = ((0, 0), (2, 0), (2, 2), (0, 2))  # ccw
        self.assertTrue(p in vs)
        w = wind(p, vs)
        self.assertEqual(w, 0)

        vs = ((0, 0), (0, 2), (2, 2), (2, 0))  # ccw
        self.assertTrue(p in vs)
        w = wind(p, vs)
        self.assertEqual(w, 0)

        # point is vertex and is not in polygon
        p = (1, 1)
        vs = ((0, 0), (1, 1), (2, 0), (2, 2), (0, 2))  # ccw
        self.assertTrue(p in vs)
        w = wind(p, vs)
        self.assertEqual(w, 0)

        vs = ((0, 0), (0, 2), (2, 2), (2, 0), (1, 1))  # ccw
        self.assertTrue(p in vs)
        w = wind(p, vs)
        self.assertEqual(w, 0)

        # point on side and is not in polygon
        p = (1, 0)
        vs = ((0, 0), (2, 0), (2, 2), (0, 2))  # ccw
        w = wind(p, vs)
        self.assertEqual(w, 0)

        vs = ((0, 0), (0, 2), (2, 2), (2, 0))  # ccw
        w = wind(p, vs)
        self.assertEqual(w, 0)

        # side collinear with p y intercept
        p = (0.5, 1)
        vs = ((0, 0), (1, 1), (2, 1), (2, 2), (0, 2))  # ccw
        w = wind(p, vs)
        self.assertEqual(w, 1)

        vs = ((0, 0), (0, 2), (2, 2), (2, 1), (1, 1))  # ccw
        w = wind(p, vs)
        self.assertEqual(w, -1)




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
             'testAddNegSubMult',
             'testNormalize',
             'testDotProduct',
             'testProjection',
             'testTrip',
             'testTween',
             'testCross3Product',
             'testWind',
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


