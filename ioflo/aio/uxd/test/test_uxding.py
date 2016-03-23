# -*- coding: utf-8 -*-
"""
Unittests for uxding module
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
from ioflo.aio.uxd import uxding

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


    def testSocketUxdNb(self):
        """
        Test Class SocketUxdNb
        """
        console.terse("{0}\n".format(self.testSocketUxdNb.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="uxd", dir=userDirpath)

        sockDirpath = os.path.join(tempDirpath, 'uxd')
        if not os.path.exists(sockDirpath):
            os.makedirs(sockDirpath)

        logDirpath = os.path.join(tempDirpath, 'log')
        if not os.path.exists(logDirpath):
            os.makedirs(logDirpath)

        wireLog = wiring.WireLog(path=logDirpath)
        result = wireLog.reopen(prefix='alpha', midfix='uxd')


        ha = os.path.join(sockDirpath, 'alpha.uxd')
        alpha = uxding.SocketUxdNb(ha=ha, umask=0x077, wlog=wireLog)
        self.assertIs(alpha.opened, False)
        result = alpha.reopen()
        self.assertIs(result, True)
        self.assertIs(alpha.opened, True)
        self.assertEqual(alpha.ha, ha)

        ha = os.path.join(sockDirpath, 'beta.uxd')
        beta = uxding.SocketUxdNb(ha=ha, umask=0x077)
        result = beta.reopen()
        self.assertIs(result, True)
        self.assertEqual(beta.ha, ha)

        ha = os.path.join(sockDirpath, 'gamma.uxd')
        gamma = uxding.SocketUxdNb(ha=ha, umask=0x077)
        result = gamma.reopen()
        self.assertIs(result, True)
        self.assertEqual(gamma.ha, ha)

        txMsg = b"Alpha sends to Beta"
        alpha.send(txMsg, beta.ha)
        rxMsg, sa = beta.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, alpha.ha)

        txMsg = b"Alpha sends to Gamma"
        alpha.send(txMsg, gamma.ha)
        rxMsg, sa = gamma.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, alpha.ha)

        txMsg = b"Alpha sends to Alpha"
        alpha.send(txMsg, alpha.ha)
        rxMsg, sa = alpha.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, alpha.ha)

        txMsg = b"Beta sends to Alpha"
        beta.send(txMsg, alpha.ha)
        rxMsg, sa = alpha.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, beta.ha)

        txMsg = b"Beta sends to Gamma"
        beta.send(txMsg, gamma.ha)
        rxMsg, sa = gamma.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, beta.ha)

        txMsg = b"Beta sends to Beta"
        beta.send(txMsg, beta.ha)
        rxMsg, sa = beta.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, beta.ha)

        txMsg = b"Gamma sends to Alpha"
        gamma.send(txMsg, alpha.ha)
        rxMsg, sa = alpha.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, gamma.ha)

        txMsg = b"Gamma sends to Beta"
        gamma.send(txMsg, beta.ha)
        rxMsg, sa = beta.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, gamma.ha)

        txMsg = b"Gamma sends to Gamma"
        gamma.send(txMsg, gamma.ha)
        rxMsg, sa = gamma.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, gamma.ha)


        pairs = [(alpha, beta), (alpha, gamma), (alpha, alpha),
                 (beta, alpha), (beta, gamma), (beta, beta),
                 (gamma, alpha), (gamma, beta), (gamma, gamma),]
        names = [('alpha', 'beta'), ('alpha', 'gamma'), ('alpha', 'alpha'),
                 ('beta', 'alpha'), ('beta', 'gamma'), ('beta', 'beta'),
                 ('gamma', 'alpha'), ('gamma', 'beta'), ('gamma', 'gamma'),]

        for i, pair in enumerate(pairs):
            txer, rxer = pair
            txName, rxName =  names[i]
            txMsg = ns2b("{0} sends to {1} again".format(txName.capitalize(), rxName.capitalize()))
            txer.send(txMsg, rxer.ha)
            rxMsg, sa = rxer.receive()
            self.assertEqual(txMsg, rxMsg)
            self.assertEqual(sa, txer.ha)


        rxMsg, sa = alpha.receive()
        self.assertIs(b'', rxMsg)
        self.assertIs(None, sa)

        rxMsg, sa = beta.receive()
        self.assertIs(b'', rxMsg)
        self.assertIs(None, sa)

        rxMsg, sa = gamma.receive()
        self.assertIs(b'', rxMsg)
        self.assertIs(None, sa)

        alpha.close()
        beta.close()
        gamma.close()

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
             'testSocketUxdNb',
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


