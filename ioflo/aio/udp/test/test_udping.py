# -*- coding: utf-8 -*-
"""
Unittests for udp async io (nonblocking) module
"""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os
import time
import tempfile
import shutil

from ioflo.aid.sixing import *
from ioflo.aid.consoling import getConsole
from ioflo.aio import wiring
from ioflo.aio.udp import udping

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

    def testSocketUdpNb(self):
        """
        Test Class SocketUdpNb
        """
        console.terse("{0}\n".format(self.testSocketUdpNb.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="log", dir=userDirpath)

        logDirpath = os.path.join(tempDirpath, 'log')
        if not os.path.exists(logDirpath):
            os.makedirs(logDirpath)

        wireLog = wiring.WireLog(path=logDirpath)
        result = wireLog.reopen(prefix='alpha', midfix='6101')

        alpha = udping.SocketUdpNb(port = 6101, wlog=wireLog)
        self.assertIs(alpha.opened, False)
        self.assertIs(alpha.reopen(), True)
        self.assertIs(alpha.opened, True)

        beta = udping.SocketUdpNb(port = 6102)
        self.assertIs(beta.reopen(), True)

        console.terse("Sending alpha to beta\n")
        msgOut = b"alpha sends to beta"
        alpha.send(msgOut, beta.ha)
        time.sleep(0.05)
        msgIn, src = beta.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], alpha.ha[1])

        console.terse("Sending alpha to alpha\n")
        msgOut = b"alpha sends to alpha"
        alpha.send(msgOut, alpha.ha)
        time.sleep(0.05)
        msgIn, src = alpha.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], alpha.ha[1])

        console.terse("Sending beta to alpha\n")
        msgOut = b"beta sends to alpha"
        beta.send(msgOut, alpha.ha)
        time.sleep(0.05)
        msgIn, src = alpha.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], beta.ha[1])

        console.terse("Sending beta to beta\n")
        msgOut = b"beta sends to beta"
        beta.send(msgOut, beta.ha)
        time.sleep(0.05)
        msgIn, src = beta.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], beta.ha[1])

        alpha.close()
        beta.close()

        self.assertIs(alpha.opened, False)

        wireLog.close()
        shutil.rmtree(tempDirpath)
        console.reinit(verbosity=console.Wordage.concise)



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
             'testSocketUdpNb',
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


