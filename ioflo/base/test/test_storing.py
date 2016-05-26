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


from ioflo.base import storing


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

    def testData(self):
        """
        Test Data Class
        """
        console.terse("{0}\n".format(self.testData.__doc__))

        data = storing.Data()
        show = data._show()
        self.assertEqual(show, 'Data: \n')
        self.assertEqual(repr(data), 'Data([])')
        data.x = 1
        data.y = 2
        data.a = 3
        # order preserving
        self.assertEqual(data.__dict__.keys(), ["x", "y", "a"])
        self.assertEqual(data.__dict__.values(), [1, 2, 3])
        self.assertEqual(data.__dict__.items(), [("x", 1),
                                                 ("y", 2),
                                                 ("a", 3)])
        show = data._show()
        self.assertEqual(show, 'Data: x=1 y=2 a=3\n')
        self.assertEqual(repr(data), "Data([('x', 1), ('y', 2), ('a', 3)])")
        stuff = data._sift()
        self.assertEqual(stuff, odict([("x", 1),
                                        ("y", 2),
                                        ("a", 3)]))
        self.assertEqual(stuff.keys(), data.__dict__.keys())

        stuff = data._sift(("y", "x"))
        self.assertEqual(stuff,odict([("y", 2),
                                        ("x", 1)]) )
        self.assertEqual(stuff.keys(), ["y", "x"])

        stuff = data._sift([])
        self.assertEqual(stuff,odict() )
        self.assertEqual(stuff.keys(), [])

        with self.assertRaises(AttributeError) as ex:
            data._b = 4
        self.assertEqual(repr(data), "Data([('x', 1), ('y', 2), ('a', 3)])")
        data._change([("z", 4), ("b", 5)])
        self.assertEqual(data.__dict__.keys(), ["x", "y", "a", "z", "b"])
        self.assertEqual(data.__dict__.values(), [1, 2, 3, 4, 5])
        self.assertEqual(data.__dict__.items(), [("x", 1),
                                                 ("y", 2),
                                                 ("a", 3),
                                                 ("z", 4),
                                                 ("b", 5)])

        items = [("x", 1),
                        ("y", 2),
                        ("a", 3),
                        ("z", 4),
                        ("b", 5)]
        stuff = odict(items)

        data = storing.Data(stuff)
        self.assertEqual(repr(data),
                         "Data([('x', 1), ('y', 2), ('a', 3), ('z', 4), ('b', 5)])")

        data = storing.Data(items)
        self.assertEqual(repr(data),
                         "Data([('x', 1), ('y', 2), ('a', 3), ('z', 4), ('b', 5)])")

        data = storing.Data(error=None)
        self.assertEqual(data.error, None)

        haul = odict([('error', None),
                      ('panSpeed', 50),
                      ('tiltSpeed', 75)])

        data._change(haul)
        self.assertEqual(data.panSpeed, haul['panSpeed'])
        self.assertEqual(data.tiltSpeed, haul['tiltSpeed'])
        # order preserving
        self.assertEqual(data.__dict__.keys(), ["error", "panSpeed", "tiltSpeed"])
        self.assertEqual(data.__dict__.values(), [None, 50, 75])
        self.assertEqual(data.__dict__.items(), [("error", None),
                                                 ("panSpeed", 50),
                                                 ("tiltSpeed", 75)])

        stuff = data._sift(haul.keys())
        self.assertEqual(haul, stuff)

        show = data._show()
        self.assertEqual(show, 'Data: error=None panSpeed=50 tiltSpeed=75\n')

        haul = odict([('panSpeed', 0),
                      ('tiltSpeed', 0)])

        data = storing.Data([('error', None)], haul)
        self.assertEqual(data.error, None)
        show = data._show()
        self.assertEqual(show, 'Data: error=None panSpeed=0 tiltSpeed=0\n')



    def testShare(self):
        """
        Test Share Class
        """
        console.terse("{0}\n".format(self.testShare.__doc__))

        share = storing.Share()
        self.assertEqual(share.name, '')
        self.assertEqual(share.store, None)
        self.assertEqual(share.stamp, None)
        self.assertIsInstance(share.data, storing.Data)
        self.assertEqual(share.data.__dict__, odict())
        self.assertEqual(share.value, None)
        self.assertEqual(share.truth, None)
        self.assertEqual(share.unit, None)
        self.assertEqual(share.owner, None)
        self.assertEqual(share.deck, storing.Deck([]))
        self.assertEqual(share.marks, odict([]))

        share = storing.Share()
        share.data.error = None
        self.assertEqual(share.data.error, None)
        self.assertEqual(share['error'], None)

        haul = odict([('error', None),
                      ('panSpeed', 50),
                      ('tiltSpeed', 75)])

        share.update(haul)
        self.assertEqual(share.data.panSpeed, haul['panSpeed'])
        self.assertEqual(share.data.tiltSpeed, haul['tiltSpeed'])
        # order preserving
        self.assertEqual(share.keys(), ["error", "panSpeed", "tiltSpeed"])
        self.assertEqual(share.values(), [None, 50, 75])
        self.assertEqual(share.items(), [("error", None),
                                                 ("panSpeed", 50),
                                                 ("tiltSpeed", 75)])

        stuff = share.sift(haul.keys())
        self.assertEqual(haul, stuff)

        show = share.data._show()
        self.assertEqual(show, 'Data: error=None panSpeed=50 tiltSpeed=75\n')

        haul = odict([('panSpeed', 0),
                      ('tiltSpeed', 0)])

        share = storing.Share().update([('error', None)], haul)
        self.assertEqual(share.data.error, None)
        show = share.data._show()
        self.assertEqual(show, 'Data: error=None panSpeed=0 tiltSpeed=0\n')

        show = share.show()  # need to make this more useful
        self.assertEqual(show, 'Name  Value None\nerror = None panSpeed = 0 tiltSpeed = 0\n')


    def testStore(self):
        """
        Test Store Class
        """
        console.terse("{0}\n".format(self.testStore.__doc__))
        storing.Store.Clear()  # clear registry of Store instance entries

        store = storing.Store()
        self.assertEqual(store.name, 'Store1')
        self.assertEqual(store.house, None)
        self.assertEqual(store.stamp, None)
        self.assertIsInstance(store.shares, storing.Node)
        self.assertIn("meta", store.shares)
        self.assertIn("realtime", store.shares)
        self.assertIn("time", store.shares)
        self.assertEqual(store.metaShr, storing.Node([]))
        self.assertIsInstance(store.realTimeShr, storing.Share)
        self.assertIsInstance(store.timeShr, storing.Share)

        share = storing.Share(name='auto.depth')
        store.add(share).create(depth=10.0)
        self.assertIs(store.fetch('auto.depth'), share)
        self.assertIs(share.data.depth, 10.0)
        with  self.assertRaises(AttributeError) as  ex:
            share.data.value
        self.assertIs(share.value, None)

        path = 'auto.heading'
        store.create(path).create(heading=20.0)
        share = store.fetch(path)
        self.assertEqual(share.data.heading, 20.0)
        share.create(heading=25.0)
        self.assertEqual(share.data.heading, 20.0)

        shareA = store.create(path)
        self.assertIs(share, shareA)

        with self.assertRaises(ValueError) as  ex:
            store.add(storing.Share(name=path))

        shareA = storing.Share(name=path)
        store.change(shareA)
        self.assertIs(store.fetch(path), shareA)
        self.assertIsNot(store.fetch(path), share)
        shareA.value = 25.0
        self.assertEqual(shareA.value, 25.0)

        path = 'auto.speed'
        share = storing.Share(name=path)
        with self.assertRaises(ValueError) as  ex:
            store.change(share)
        store.add(share)
        self.assertIs(store.fetch(share.name), share)

        store.expose(valued=True)
        storing.Store.Clear()

def Test():
    """Module self test """


    try:
        Store.Clear()

        store = Store()
        print("Store shares = %s" % store.shares)

        store.add(Share(name = 'autopilot.depth')).create(depth = 0.0)
        print( store.fetch('autopilot.depth').data.depth)
        try:
            print( store.fetch('autopilot.depth').data.value)
        except AttributeError as e1:
            print( e1.message)
        print( store.fetch('autopilot.depth').value)
        print( "Store shares = %s" % store.shares)

        store.create('autopilot.heading').create(heading = 0.0)
        print( store.fetch('autopilot.heading').data.heading)
        try:
            print( store.fetch('autopilot.heading').data.value)
        except AttributeError as e1:
            print( e1.message)
        print( store.fetch('autopilot.heading').value)
        print( "Store shares = %s" % store.shares)

        s = Share(store = store, name = 'autopilot.heading')
        s.create(value = 60.0)
        s.create(value = 50.0)
        print( s.data.value)
        print( s.value)
        print( s.data.value)
        print( s.value)
        store.change(s)
        print( "Store shares = %s" % store.shares)

        try:
            store.add(Share(name = 'autopilot.depth'))
        except ValueError as e1:
            print( e1.message)
        print( "Store shares = %s" % store.shares)

        try:
            store.change(Share(name = 'autopilot.speed'))
        except ValueError as e1:
            print( e1.message)
        print( "Store shares = %s" % store.shares)

        print( "autopilot.heading = %s" % store.fetch('autopilot.heading'))
        print( "autopilot = %s" % store.fetch('autopilot'))
        print( "dog = %s" % store.fetch('dog'))

        store.expose()

    except ValueError as e1:
        print( e1.message)

    return store



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
                'testData',
                'testShare',
                'testStore',
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




