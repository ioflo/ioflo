# -*- coding: utf-8 -*-
"""
Unittests for nonblocking module
"""

import sys
if sys.version > '3':
    xrange = range
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os
import time
import tempfile
import shutil

#from ioflo.test import testing
from ioflo.base.consoling import getConsole
console = getConsole()

from ioflo.base import nonblocking

def setUpModule():
    console.reinit(verbosity=console.Wordage.concise)

def tearDownModule():
    pass

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

    def testConsoleNB(self):
        """
        Test Class ConsoleNB
        """
        console.terse("{0}\n".format(self.testConsoleNB.__doc__))

        myconsole = nonblocking.ConsoleNB()
        result = myconsole.open()
        #self.assertIs(result, False)
        #self.assertIs(result, True)

        #cout = "Enter 'hello' and hit return: "
        #myconsole.put(cout)
        #cin = ''
        #while not cin:
            #cin = myconsole.getLine()
        #myconsole.put("You typed: " + cin)
        #self.assertEqual('hello\n', cin)

        myconsole.close()

    def testSocketUdpNB(self):
        """
        Test Class SocketUdpNb
        """
        console.terse("{0}\n".format(self.testSocketUdpNB.__doc__))
        console.reinit(verbosity=console.Wordage.verbose)
        alpha = nonblocking.SocketUdpNb(port = 6101)
        self.assertIs(alpha.reopen(), True)

        beta = nonblocking.SocketUdpNb(port = 6102)
        self.assertIs(beta.reopen(), True)

        console.terse("Sending alpha to beta\n")
        msgOut = "alpha sends to beta"
        alpha.send(msgOut, beta.ha)
        time.sleep(0.05)
        msgIn, src = beta.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], alpha.ha[1])

        console.terse("Sending alpha to alpha\n")
        msgOut = "alpha sends to alpha"
        alpha.send(msgOut, alpha.ha)
        time.sleep(0.05)
        msgIn, src = alpha.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], alpha.ha[1])


        console.terse("Sending beta to alpha\n")
        msgOut = "beta sends to alpha"
        beta.send(msgOut, alpha.ha)
        time.sleep(0.05)
        msgIn, src = alpha.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], beta.ha[1])


        console.terse("Sending beta to beta\n")
        msgOut = "beta sends to beta"
        beta.send(msgOut, beta.ha)
        time.sleep(0.05)
        msgIn, src = beta.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], beta.ha[1])

        alpha.close()
        beta.close()
        console.reinit(verbosity=console.Wordage.concise)

    def testSocketUxdNB(self):
        """
        Test Class SocketUxdNb
        """
        console.terse("{0}\n".format(self.testSocketUxdNB.__doc__))
        console.reinit(verbosity=console.Wordage.verbose)

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="uxd", dir=userDirpath)
        sockDirpath = os.path.join(tempDirpath, 'uxd')
        if not os.path.exists(sockDirpath):
            os.makedirs(sockDirpath)

        ha = os.path.join(sockDirpath, 'alpha.uxd')
        alpha = nonblocking.SocketUxdNb(ha=ha, umask=0x077)
        result = alpha.reopen()
        self.assertIs(result, True)
        self.assertEqual(alpha.ha, ha)

        ha = os.path.join(sockDirpath, 'beta.uxd')
        beta = nonblocking.SocketUxdNb(ha=ha, umask=0x077)
        result = beta.reopen()
        self.assertIs(result, True)
        self.assertEqual(beta.ha, ha)

        ha = os.path.join(sockDirpath, 'gamma.uxd')
        gamma = nonblocking.SocketUxdNb(ha=ha, umask=0x077)
        result = gamma.reopen()
        self.assertIs(result, True)
        self.assertEqual(gamma.ha, ha)

        txMsg = "Alpha sends to Beta"
        alpha.send(txMsg, beta.ha)
        rxMsg, sa = beta.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, alpha.ha)

        txMsg = "Alpha sends to Gamma"
        alpha.send(txMsg, gamma.ha)
        rxMsg, sa = gamma.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, alpha.ha)

        txMsg = "Alpha sends to Alpha"
        alpha.send(txMsg, alpha.ha)
        rxMsg, sa = alpha.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, alpha.ha)

        txMsg = "Beta sends to Alpha"
        beta.send(txMsg, alpha.ha)
        rxMsg, sa = alpha.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, beta.ha)

        txMsg = "Beta sends to Gamma"
        beta.send(txMsg, gamma.ha)
        rxMsg, sa = gamma.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, beta.ha)

        txMsg = "Beta sends to Beta"
        beta.send(txMsg, beta.ha)
        rxMsg, sa = beta.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, beta.ha)

        txMsg = "Gamma sends to Alpha"
        gamma.send(txMsg, alpha.ha)
        rxMsg, sa = alpha.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, gamma.ha)

        txMsg = "Gamma sends to Beta"
        gamma.send(txMsg, beta.ha)
        rxMsg, sa = beta.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, gamma.ha)

        txMsg = "Gamma sends to Gamma"
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
            txMsg = "{0} sends to {1} again".format(txName.capitalize(), rxName.capitalize())
            txer.send(txMsg, rxer.ha)
            rxMsg, sa = rxer.receive()
            self.assertEqual(txMsg, rxMsg)
            self.assertEqual(sa, txer.ha)


        rxMsg, sa = alpha.receive()
        self.assertIs('', rxMsg)
        self.assertIs(None, sa)

        rxMsg, sa = beta.receive()
        self.assertIs('', rxMsg)
        self.assertIs(None, sa)

        rxMsg, sa = gamma.receive()
        self.assertIs('', rxMsg)
        self.assertIs(None, sa)

        alpha.close()
        beta.close()
        gamma.close()

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
    names = ['testConsoleNB',
             'testSocketUdpNB',
             'testSocketUxdNB', ]
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

    #runSome()#only run some

    runOne('testSocketUxdNB')

