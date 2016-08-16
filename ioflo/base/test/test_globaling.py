# -*- coding: utf-8 -*-
"""
Unittests
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
from ioflo.aid import getConsole, odict

console = getConsole()


from ioflo.base import globaling


def setUpModule():
    console.reinit(verbosity=console.Wordage.concise)

def tearDownModule():
    console.reinit(verbosity=console.Wordage.concise)

class BasicTestCase(unittest.TestCase):
    """
    Test Case
    """

    def setUp(self):
        """

        """
        console.reinit(verbosity=console.Wordage.profuse)

    def tearDown(self):
        """

        """
        console.reinit(verbosity=console.Wordage.concise)

    def testPointRegex(self):
        """
        Test Point Regex Instances
        """
        console.terse("{0}\n".format(self.testPointRegex.__doc__))

        text = "-25.6x30.45y"
        match = globaling.REO_PointXY.findall(text)
        x, y = match[0]
        x = float(x)
        y = float(y)
        self.assertEqual(x, -25.6)
        self.assertEqual(y, 30.45)

        text = "-25.6X+30.45Y"
        match = globaling.REO_PointXY.findall(text)
        x, y = match[0]
        x = float(x)
        y = float(y)
        self.assertEqual(x, -25.6)
        self.assertEqual(y, 30.45)

        text = "-25.6x30.45Y"
        match = globaling.REO_PointXY.findall(text)
        x, y = match[0]
        x = float(x)
        y = float(y)
        self.assertEqual(x, -25.6)
        self.assertEqual(y, 30.45)

        text = "+25x-30y"
        match = globaling.REO_PointXY.findall(text)
        x, y = match[0]
        x = float(x)
        y = float(y)
        self.assertEqual(x, 25.0)
        self.assertEqual(y, -30.0)

        text = "25.x+30.y"
        match = globaling.REO_PointXY.findall(text)
        x, y = match[0]
        x = float(x)
        y = float(y)
        self.assertEqual(x, 25.0)
        self.assertEqual(y, 30.0)

        text = "-25.6n30.45e"
        match = globaling.REO_PointNE.findall(text)
        n, e = match[0]
        n = float(n)
        e = float(e)
        self.assertEqual(n, -25.6)
        self.assertEqual(e, 30.45)

        text = "-25.6N+30.45E"
        match = globaling.REO_PointNE.findall(text)
        n, e = match[0]
        n = float(n)
        e = float(e)
        self.assertEqual(n, -25.6)
        self.assertEqual(e, 30.45)

        text = "-25.6n30.45E"
        match = globaling.REO_PointNE.findall(text)
        n, e = match[0]
        n = float(n)
        e = float(e)
        self.assertEqual(n, -25.6)
        self.assertEqual(e, 30.45)

        text = "25n-30e"
        match = globaling.REO_PointNE.findall(text)
        n, e = match[0]
        n = float(n)
        e = float(e)
        self.assertEqual(n, 25.0)
        self.assertEqual(e, -30.0)

        text = "+25.n30.e"
        match = globaling.REO_PointNE.findall(text)
        n, e = match[0]
        n = float(n)
        e = float(e)
        self.assertEqual(n, 25.0)
        self.assertEqual(e, 30.0)

        text = "25.6f-30.45s"
        match = globaling.REO_PointFS.findall(text)
        f, s = match[0]
        f = float(f)
        s = float(s)
        self.assertEqual(f, 25.6)
        self.assertEqual(s, -30.45)

        text = "-25.6F+30.45S"
        match = globaling.REO_PointFS.findall(text)
        f, s = match[0]
        f = float(f)
        s = float(s)
        self.assertEqual(f, -25.6)
        self.assertEqual(s, 30.45)


        text = "25.6x-30.45y-15.4z"
        match = globaling.REO_PointXYZ.findall(text)
        x, y, z = match[0]
        x = float(x)
        y = float(y)
        z = float(z)
        self.assertEqual(x, 25.6)
        self.assertEqual(y, -30.45)
        self.assertEqual(z, -15.4)

        text = "-25.6X+30.45Y15.4Z"
        match = globaling.REO_PointXYZ.findall(text)
        x, y, z = match[0]
        x = float(x)
        y = float(y)
        z = float(z)
        self.assertEqual(x, -25.6)
        self.assertEqual(y, 30.45)
        self.assertEqual(z, 15.4)

        text = "25.6n-30.45e-15.4d"
        match = globaling.REO_PointNED.findall(text)
        n, e, d = match[0]
        n = float(n)
        e = float(e)
        d = float(d)
        self.assertEqual(n, 25.6)
        self.assertEqual(e, -30.45)
        self.assertEqual(d, -15.4)

        text = "-25.6N+30.45E15.4D"
        match = globaling.REO_PointNED.findall(text)
        n, e, d  = match[0]
        n = float(n)
        e = float(e)
        d = float(d)
        self.assertEqual(n, -25.6)
        self.assertEqual(e, 30.45)
        self.assertEqual(d, 15.4)

        text = "25.6f-30.45s-15.4b"
        match = globaling.REO_PointFSB.findall(text)
        f, s, b = match[0]
        f = float(f)
        s = float(s)
        b = float(b)
        self.assertEqual(f, 25.6)
        self.assertEqual(s, -30.45)
        self.assertEqual(b, -15.4)

        text = "-25.6F+30.45S15.4B"
        match = globaling.REO_PointFSB.findall(text)
        f, s, b = match[0]
        f = float(f)
        s = float(s)
        b = float(b)
        self.assertEqual(f, -25.6)
        self.assertEqual(s, 30.45)
        self.assertEqual(b, 15.4)


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
                'testPointRegex',
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

    #runAll() #run all unittests

    runSome()#only run some

    #runOne('testBasic')




