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
from ioflo.aid import odict
from ioflo.test import testing
from ioflo.aid.consoling import getConsole
console = getConsole()

from ioflo.aid import classing
from ioflo.base import registering

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

    def testNonStringIterable(self):
        """
        Test the utility function nonStringIterable
        """
        console.terse("{0}\n".format(self.testNonStringIterable.__doc__))
        a = bytearray(b'abc')
        w = dict(a=1, b=2, c=3)
        x = 'abc'
        y = b'abc'
        z = [1, 2, 3]

        self.assertTrue(isinstance(a, classing.NonStringIterable))
        self.assertTrue(isinstance(w, classing.NonStringIterable))
        self.assertFalse(isinstance(x, classing.NonStringIterable))
        self.assertFalse(isinstance(y, classing.NonStringIterable))
        self.assertTrue(isinstance(z, classing.NonStringIterable))


    def testNonStringSequence(self):
        """
        Test the utility function nonStringSequence
        """
        console.terse("{0}\n".format(self.testNonStringSequence.__doc__))
        a = bytearray(b'abc')
        w = dict(a=1, b=2, c=3)
        x = 'abc'
        y = b'abc'
        z = [1, 2, 3]

        self.assertTrue(isinstance(a, classing.NonStringIterable))
        self.assertFalse(isinstance(w, classing.NonStringSequence))
        self.assertFalse(isinstance(x, classing.NonStringSequence))
        self.assertFalse(isinstance(y, classing.NonStringSequence))
        self.assertTrue(isinstance(z, classing.NonStringSequence))

    def testMetaclassify(self):
        """
        Test the utility decorator metaclassify
        """
        console.terse("{0}\n".format(self.testMetaclassify.__doc__))

        @classing.metaclassify(registering.RegisterType)
        class A(object):
            #__metaclass__ = registering.RegisterType
            def __init__(self, name="", store=None):
                self.name = name
                self.store = store


        self.assertEqual(A.Registry, {'A': (A, None, None, None)})

    def testIsIterator(self):
        """
        Test the utility function isIterator
        """
        o = [1, 2, 3]
        self.assertFalse(classing.isIterator(o))
        i = iter(o)
        self.assertTrue(classing.isIterator(i))

        def genf():
            yield ""
            yield ""

        self.assertFalse(classing.isIterator(genf))
        gen = genf()
        self.assertTrue(classing.isIterator(gen))

    if sys.version_info >= (3, 6):
        def testAttributize(self):
            """
            Test the utility decorator attributize generator
            """
            global headed

            console.terse("{0}\n".format(self.testAttributize.__doc__))

            def gf(skin, x):
                skin.x = 5
                skin.y = 'a'
                cnt = 0
                while cnt < x:
                    yield cnt
                    cnt += 1

            agf = classing.attributize(gf)
            ag = agf(3)
            self.assertTrue(classing.isIterator(ag))
            self.assertFalse(hasattr(ag, 'x'))
            self.assertFalse(hasattr(ag, 'y'))
            n = next(ag)  # body of gf is not run until first next call
            self.assertEqual(n, 0)
            self.assertTrue(hasattr(ag, 'x'))
            self.assertTrue(hasattr(ag, 'y'))
            self.assertEqual(ag.x, 5)
            self.assertEqual(ag.y, 'a')
            n = next(ag)
            self.assertEqual(n, 1)


            # Set up like WSGI for generator function
            @classing.attributize
            def bar(skin, req=None, rep=None):
                """
                Generator function with "skin" parameter for skin wrapper to
                attach attributes
                """
                skin._status = 400
                skin._headers = odict(example="Hi")
                yield b""
                yield b""
                yield b"Hello There"
                return b"Goodbye"

            # now use it like WSGI server does
            msgs = []
            gen = bar()
            self.assertTrue(classing.isIterator(gen))
            self.assertFalse(hasattr(gen, '_status'))
            self.assertFalse(hasattr(gen, '_headers'))

            headed = False

            def write(msg):
                """
                Simulate WSGI write
                """
                global headed

                if not headed:  # add headers
                    if hasattr(gen, "_status"):
                        if gen._status is not None:
                            msgs.append(str(gen._status))
                    if hasattr(gen, "_headers"):
                        for key, val in gen._headers.items():
                            msgs.append("{}={}".format(key, val))

                    headed = True

                msgs.append(msg)

            igen = iter(gen)
            self.assertIs(igen, gen)
            done = False
            while not done:
                try:
                    msg = next(igen)
                except StopIteration as ex:
                    if hasattr(ex, "value") and ex.value:
                        write(ex.value)
                    write(b'')  # in case chunked send empty chunk to terminate
                    done = True
                else:
                    if msg:  # only write if not empty allows async processing
                        write(msg)

            self.assertEqual(msgs, ['400', 'example=Hi', b'Hello There', b'Goodbye', b''])


            # Set up like WSGI for generator method
            class R:
                @classing.attributize
                def bar(self, skin, req=None, rep=None):
                    """
                    Generator function with "skin" parameter for skin wrapper to
                    attach attributes
                    """
                    self.name = "Peter"
                    skin._status = 400
                    skin._headers = odict(example="Hi")
                    yield b""
                    yield b""
                    yield b"Hello There " + self.name.encode()
                    return b"Goodbye"

            # now use it like WSGI server does
            r = R()
            msgs = []
            gen = r.bar()
            self.assertTrue(classing.isIterator(gen))
            self.assertFalse(hasattr(gen, '_status'))
            self.assertFalse(hasattr(gen, '_headers'))

            headed = False

            def write(msg):
                """
                Simulate WSGI write
                """
                global headed

                if not headed:  # add headers
                    if hasattr(gen, "_status"):
                        if gen._status is not None:
                            msgs.append(str(gen._status))
                    if hasattr(gen, "_headers"):
                        for key, val in gen._headers.items():
                            msgs.append("{}={}".format(key, val))

                    headed = True

                msgs.append(msg)

            igen = iter(gen)
            self.assertIs(igen, gen)
            done = False
            while not done:
                try:
                    msg = next(igen)
                except StopIteration as ex:
                    if hasattr(ex, "value") and ex.value:
                        write(ex.value)
                    write(b'')  # in case chunked send empty chunk to terminate
                    done = True
                else:
                    if msg:  # only write if not empty allows async processing
                        write(msg)

            self.assertEqual(msgs, ['400', 'example=Hi', b'Hello There Peter', b'Goodbye', b''])


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
    names = ['testNonStringIterable',
             'testNonStringSequence',
             'testMetaclassify',
             'testIsIterator',
            ]
    tests.extend(map(BasicTestCase, names))
    if sys.version_info >= (3, 6):
        tests.extend(map(BasicTestCase, ['testAttributize']))
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
    #runOne('testSkinGenFunc')


