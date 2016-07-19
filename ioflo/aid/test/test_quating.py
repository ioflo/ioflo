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

from ioflo.aid import quaternioning


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

    def testQMag(self):
        """
        Test the qmag and qmag2 functions
        """
        console.terse("{0}\n".format(self.testQMag.__doc__))

        from ioflo.aid.quaternioning import qmag, qmag2

        q = [1, 1, 2, 3]  # list
        m = qmag(q)
        self.assertAlmostEqual(m, 3.872983346207417)

        m2 = qmag2(q)
        self.assertEqual(m2, 15)

        q = (1, 1, 2, 3)  # tuple
        m = qmag(q)
        self.assertAlmostEqual(m, 3.872983346207417)

        m2 = qmag2(q)
        self.assertEqual(m2, 15)

        q = [0, 0, 0, 0]
        m = qmag(q)
        self.assertEqual(m, 0.0)

        m2 = qmag2(q)
        self.assertEqual(m2, 0.0)

        q = [1, 0, 0, 0]
        m = qmag(q)
        self.assertEqual(m, 1.0)

        m2 = qmag2(q)
        self.assertEqual(m2, 1)

    def testQNorm(self):
        """
        Test the qnorm function
        """
        console.terse("{0}\n".format(self.testQNorm.__doc__))

        from ioflo.aid.quaternioning import qnorm, qmag

        q = [1, 1, 2, 3]  # list
        n = qnorm(q)
        m = qmag(n)
        self.assertAlmostEqual(m, 1.0)

        z = (0.2581988897471611, 0.2581988897471611, 0.5163977794943222, 0.7745966692414834)
        for e1, e2 in zip(n, z):
            self.assertAlmostEqual(e1, e2)

        q = [0, 0, 0, 0]  # special case
        n = qnorm(q)
        m = qmag(n)
        self.assertAlmostEqual(m, 0.0)

        q = [1, 0, 0, 0]
        n = qnorm(q)
        m = qmag(n)
        self.assertEqual(m, 1.0)

        z = [1.0, 0.0, 0.0, 0.0]
        for e1, e2 in zip(n, z):
            self.assertEqual(e1, e2)

        q = (0.0, 0.0, 0.49999999999999994, 0.8660254037844386)
        n = qnorm(q, check=True)
        m = qmag(n)
        self.assertEqual(m, 1.0)

    def testQConj(self):
        """
        Test the qconj function
        """
        console.terse("{0}\n".format(self.testQConj.__doc__))

        from ioflo.aid.quaternioning import qnorm, qmag, qconj

        q = [1, 1, 2, 3]  # list
        cq = qconj(q)

        z = (1, -1, -2, -3)
        for e1, e2 in zip(cq, z):
            self.assertEqual(e1, e2)

        q = [0, 0, 0, 0]  # special case
        cq = qconj(q)
        for e1, e2 in zip(cq, q):
            self.assertEqual(e1, e2)


        q = [1, 0, 0, 0] # special case
        cq = qconj(q)
        for e1, e2 in zip(cq, q):
            self.assertEqual(e1, e2)


    def testQMul(self):
        """
        Test the qmul function
        """
        console.terse("{0}\n".format(self.testQMul.__doc__))

        from ioflo.aid.quaternioning import qnorm, qmag, qconj, qmul

        q1 = (1, 2, 3, 4)
        q2 = (4, 3, 2, 1)
        q = qmul(q1, q2)

        qq = (-12, 6, 24, 12)
        for e1, e2 in zip(q, qq):
            self.assertEqual(e1, e2)

        rq = qmul(q2, q1)  # not commutative

        qq = (-12, 16, 4, 22)
        for e1, e2 in zip(rq, qq):
            self.assertEqual(e1, e2)

        q1 = (0, 0, 0, 0)  # zero case
        q2 = (4, 3, 2, 1)
        q = qmul(q1, q2)

        qq = (0, 0, 0, 0)
        for e1, e2 in zip(q, qq):
            self.assertEqual(e1, e2)

        q1 = (1, 0, 0, 0)  # identity case
        q2 = (5, 4 , 3, 2)
        q = qmul(q1, q2)

        for e1, e2 in zip(q, q2):
            self.assertEqual(e1, e2)

        q1 = (1, 0, 0, 0)  # identity case commutes
        q2 = (5, 4 , 3, 2)
        q = qmul(q2, q1)

        for e1, e2 in zip(q, q2):
            self.assertEqual(e1, e2)

        q1 = (5, 4, 3, 2)
        q2 = qconj(q1)
        q = qmul(q1, q2)  # qq*

        qq = (54, 0, 0, 0)
        for e1, e2 in zip(q, qq):
            self.assertEqual(e1, e2)

        q3 = qmul(q2, q1)  # q*q == qq*

        for e1, e2 in zip(q, q3):
            self.assertEqual(e1, e2)

        q1 = qnorm((5, 4, 3, 2))  # unit vector
        q2 = qconj(q1)  # conjugate of unit vector is inverse
        q = qmul(q1, q2)

        qq = (1.0, 0, 0, 0)
        for e1, e2 in zip(q, qq):
            self.assertEqual(e1, e2)



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
             'testQMag',
             'testQNorm',
             'testQConj',
             'testQMul',
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


