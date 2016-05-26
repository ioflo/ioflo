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

from ioflo.aid import odicting


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

    def testODict(self):
        """
        Test the odict class
        """
        console.terse("{0}\n".format(self.testODict.__doc__))

        x = odicting.odict()
        x["a"] = 5
        self.assertEqual(x.items(), [('a', 5)])
        x["a"] = 6
        self.assertEqual(x.items(), [('a', 6)])

        items = [("x", 1),
                 ("y", 2),
                 ("a", 3)]
        keys = [key for key, val in items]
        values = [val for  key, val in  items]
        od = odicting.odict(items)
        self.assertEqual(od.keys(), keys)
        self.assertEqual(od.values(), values)
        self.assertEqual(od.items(), items)

        fields = ['y', 'x']
        stuff = od.sift(fields)
        self.assertEqual(stuff.items(), [('y', 2), ('x', 1)])

        stuff = od.sift()
        self.assertEqual(stuff.items(), od.items())

    def testMoDict(self):
        """
        Test the modict
        """
        console.terse("{0}\n".format(self.testMoDict.__doc__))

        x = odicting.modict()
        x["a"] = 5
        self.assertEqual(x.items(), [('a', 5)])
        x["a"] = 6
        self.assertEqual(x.items(), [('a', 6)])
        self.assertEqual(x.listitems(), [('a', [5, 6])] )

        y = x.setdefault("a", 10)
        self.assertEqual(y, 6)
        z = x.setdefault("b", 1)
        self.assertEqual(z, 1)
        self.assertEqual(x.listitems(), [('a', [5, 6]), ('b', [1])])




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
                'testODict',
                'testMoDict',
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


