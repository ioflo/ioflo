# -*- coding: utf-8 -*-
"""
Unit Test Template
"""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os

from ioflo.test import testing
from ioflo.base.consoling import getConsole
console = getConsole()


from ioflo.base import acting
from ioflo.base import deeding
from ioflo.base import storing


def setUpModule():
    console.reinit(verbosity=console.Wordage.concise)

def tearDownModule():
    pass


class BasicTestCase(testing.FrameIofloTestCase):
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

    def testActorify(self):
        """
        Test the actorify decorator
        """
        console.terse("{0}\n".format(self.testActorify.__doc__))
        @acting.actorify("BlueBeard")
        def bearded(self, x=1, y=2):
            """
            Actor action method
            """
            z = x +  y
            return (self, z)

        self.assertIn("BlueBeard", acting.Actor.Registry)
        actor, inits, ioinits, parms = acting.Actor.__fetch__("BlueBeard")
        self.assertIs(actor._Parametric, True)
        self.assertDictEqual(actor.Inits, {})
        self.assertDictEqual(actor.Ioinits, {})
        self.assertDictEqual(actor.Parms, {})
        self.assertDictEqual(inits, {})
        self.assertDictEqual(ioinits, {})
        self.assertDictEqual(parms, {})

        actor = actor()  # create instance
        self.assertIsInstance(actor, acting.Actor )
        self.assertEqual(actor.__class__.__name__, "BlueBeard")
        if sys.version > '3':
            self.assertEqual(actor.action.__self__.__class__.__name__, "BlueBeard")
            self.assertIs(actor.action.__func__, bearded)
            self.assertIs(actor.action.__self__, actor)
        else:
            self.assertEqual(actor.action.im_class.__name__, "BlueBeard")
            self.assertIs(actor.action.im_func, bearded)
            self.assertIs(actor.action.im_self, actor)
        self.assertEqual(actor.action.__doc__, '\n            Actor action method\n            ')
        self.assertEqual(actor.action.__name__, 'bearded')

        me, z = actor()  # perform action
        self.assertIs(me, actor)
        self.assertEqual(z, 3)


    def testDeedify(self):
        """
        Test the deedify decorator
        """
        console.terse("{0}\n".format(self.testDeedify.__doc__))
        @deeding.deedify("BlackSmith")
        def blackened(self, x=3, y=2):
            """
            Deed action method
            """
            z = x + y
            return (self, z)

        self.assertIn("BlackSmith", deeding.Deed.Registry)
        actor, inits, ioinits, parms = deeding.Deed.__fetch__("BlackSmith")
        self.assertIs(actor._Parametric, False)
        self.assertDictEqual(actor.Inits, {})
        self.assertDictEqual(actor.Ioinits, {})
        self.assertDictEqual(actor.Parms, {})
        self.assertDictEqual(inits, {})
        self.assertDictEqual(ioinits, {})
        self.assertDictEqual(parms, {})

        actor = actor()  # create instance
        self.assertIsInstance(actor, deeding.Deed )
        self.assertEqual(actor.__class__.__name__, "BlackSmith")
        if sys.version > '3':
            self.assertEqual(actor.action.__self__.__class__.__name__, "BlackSmith")
            self.assertIs(actor.action.__func__, blackened)
            self.assertIs(actor.action.__self__, actor)
        else:
            self.assertEqual(actor.action.im_class.__name__, "BlackSmith")
            self.assertIs(actor.action.im_func, blackened)
            self.assertIs(actor.action.im_self, actor)
        self.assertEqual(actor.action.__doc__, '\n            Deed action method\n            ')
        self.assertEqual(actor.action.__name__, 'blackened')

        me, z = actor()  # perform action
        self.assertIs(me, actor)
        self.assertEqual(z, 5)

    def testFrameDeed(self):
        """
        Test adding a Deed to a frame and running it
        """
        console.terse("{0}\n".format(self.testFrameDeed.__doc__))
        @deeding.deedify("TestDeed")
        def action(self, a="Felgercarb", **kwa):
            """
            Deed action method
            """
            share = self.store.create(".test.a").update(value=a)

        self.assertIn("TestDeed", deeding.Deed.Registry)
        act = self.addDeed("TestDeed")
        self.assertIsInstance(act, acting.Act)
        self.assertIn(act, self.frame.reacts)
        self.assertEqual(act.actor, "TestDeed")
        self.assertEqual(act.frame, self.frame.name)

        self.resolve()  # resolve House
        self.assertIs(act.frame, self.frame)
        self.assertIs(act.frame.framer, self.framer)
        self.assertIs(act.actor.store, self.store)
        self.assertIn(act.actor.name, deeding.Deed.Registry)
        self.assertEqual(act.actor.name, "TestDeed")
        self.assertIsInstance(act.actor, deeding.Deed)
        self.assertEqual(act.actor.__class__.__name__, "TestDeed")
        if sys.version > '3':
            self.assertEqual(act.actor.action.__self__.__class__.__name__, "TestDeed")
            self.assertIs(act.actor.action.__func__, action)
            self.assertIs(act.actor.action.__self__, act.actor)
        else:
            self.assertEqual(act.actor.action.im_class.__name__, "TestDeed")
            self.assertIs(act.actor.action.im_func, action)
            self.assertIs(act.actor.action.im_self, act.actor)
        self.assertEqual(act.actor.action.__doc__, '\n            Deed action method\n            ')
        self.assertEqual(act.actor.action.__name__, 'action')

        self.assertIs(self.store.fetch(".test.a"), None)
        self.frame.recur()  # run reacts in frame
        share = self.store.fetch(".test.a")
        self.assertIsInstance(share, storing.Share )
        self.assertEqual(share.value, "Felgercarb")


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
    names = ['testActorify',
             'testDeedify',
             'testFrameDeed', ]
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


