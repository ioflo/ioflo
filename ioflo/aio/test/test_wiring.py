# -*- coding: utf-8 -*-
"""
Unittests for wiring (wire logging) module
Over the wire logs
"""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os
import tempfile
import shutil

from ioflo.aid.sixing import *
from ioflo.aid.consoling import getConsole
from ioflo.aio import wiring

console = getConsole()


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
        pass


    def tearDown(self):
        """

        """
        pass

    def testWireLog(self):
        """
        Test Class WireLog
        """
        console.terse("{0}\n".format(self.testWireLog.__doc__))

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="log", dir=userDirpath)
        logDirpath = os.path.join(tempDirpath, 'log')
        if not os.path.exists(logDirpath):
            os.makedirs(logDirpath)

        wire = wiring.WireLog(path=logDirpath)
        prefix = 'localhost'
        midfix = '5000'
        result = wire.reopen(prefix=prefix, midfix=midfix)

        self.assertIsNotNone(wire.rxLog)
        self.assertIsNotNone(wire.txLog)
        self.assertFalse(wire.rxLog.closed)
        self.assertFalse(wire.txLog.closed)
        self.assertTrue(wire.rxLog.name.endswith('_rx.txt'))
        self.assertTrue(wire.txLog.name.endswith('_tx.txt'))
        self.assertTrue("{0}_{1}_".format(prefix, midfix) in wire.rxLog.name)
        self.assertTrue("{0}_{1}_".format(prefix, midfix) in wire.txLog.name)

        ha = ('127.0.0.1', 5000)
        data = b"Test data Tx"
        wire.writeTx(ha, data)
        wire.txLog.seek(0)
        result = wire.txLog.readline()
        result += wire.txLog.readline()
        self.assertEqual(result, ns2b("TX {0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        data = b"Test data Rx"
        wire.writeRx(ha, data)
        wire.rxLog.seek(0)
        result = wire.rxLog.readline()
        result += wire.rxLog.readline()
        self.assertEqual(result, ns2b("RX {0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        wire.close()

        wire = wiring.WireLog(path=logDirpath, same=True)
        prefix = 'localhost'
        midfix = '5000'
        result = wire.reopen(prefix=prefix, midfix=midfix)

        self.assertIsNotNone(wire.rxLog)
        self.assertIsNotNone(wire.txLog)
        self.assertFalse(wire.rxLog.closed)
        self.assertFalse(wire.txLog.closed)
        self.assertIs(wire.rxLog, wire.txLog)
        self.assertEqual(wire.rxLog.name, wire.txLog.name)
        self.assertTrue(wire.rxLog.name.endswith('.txt'))
        self.assertTrue(wire.txLog.name.endswith('.txt'))
        self.assertTrue("{0}_{1}_".format(prefix, midfix) in wire.rxLog.name)
        self.assertTrue("{0}_{1}_".format(prefix, midfix) in wire.txLog.name)

        ha = ('127.0.0.1', 5000)
        data = b"Test data Tx"
        wire.writeTx(ha, data)
        wire.txLog.seek(0)
        result = wire.txLog.readline()
        result += wire.txLog.readline()
        self.assertEqual(result, ns2b("TX {0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))
        spot = wire.txLog.tell()

        data = b"Test data Rx"
        wire.writeRx(ha, data)
        wire.rxLog.seek(spot)
        result = wire.rxLog.readline()
        result += wire.rxLog.readline()
        self.assertEqual(result, ns2b("RX {0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        wire.close()
        shutil.rmtree(tempDirpath)

    def testWireLogBuffify(self):
        """
        Test Class WireLog
        """
        console.terse("{0}\n".format(self.testWireLogBuffify.__doc__))

        wire = wiring.WireLog(buffify=True)
        prefix = 'localhost'
        midfix = '5000'
        result = wire.reopen(prefix=prefix, midfix=midfix)

        self.assertIsNotNone(wire.rxLog)
        self.assertIsNotNone(wire.txLog)
        self.assertFalse(wire.rxLog.closed)
        self.assertFalse(wire.txLog.closed)

        ha = ('127.0.0.1', 5000)
        data = b"Test data Tx"
        wire.writeTx(ha, data)
        wire.txLog.seek(0)
        result = wire.txLog.readline()
        result += wire.txLog.readline()
        self.assertEqual(result, ns2b("TX {0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        data = b"Test data Rx"
        wire.writeRx(ha, data)
        wire.rxLog.seek(0)
        result = wire.rxLog.readline()
        result += wire.rxLog.readline()
        self.assertEqual(result, ns2b("RX {0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        wire.close()

        wire = wiring.WireLog(buffify=True, same=True)
        prefix = 'localhost'
        midfix = '5000'
        result = wire.reopen(prefix=prefix, midfix=midfix)

        self.assertIsNotNone(wire.rxLog)
        self.assertIsNotNone(wire.txLog)
        self.assertFalse(wire.rxLog.closed)
        self.assertFalse(wire.txLog.closed)
        self.assertIs(wire.rxLog, wire.txLog)

        ha = ('127.0.0.1', 5000)
        data = b"Test data Tx"
        wire.writeTx(ha, data)
        wire.txLog.seek(0)
        result = wire.txLog.readline()
        result += wire.txLog.readline()
        self.assertEqual(result, ns2b("TX {0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))
        spot = wire.txLog.tell()

        data = b"Test data Rx"
        wire.writeRx(ha, data)
        wire.rxLog.seek(spot)
        result = wire.rxLog.readline()
        result += wire.rxLog.readline()
        self.assertEqual(result, ns2b("RX {0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        wire.close()


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
             'testWireLog',
             'testWireLogBuffify',
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

    #runOne('testClientAutoReconnect')


