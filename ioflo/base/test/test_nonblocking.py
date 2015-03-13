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

def TestSocketUxdNB():
    """Class SocketUxdNb self test """
    console.reinit(verbosity=console.Wordage.verbose)
    try:
        print("Testing SocketUxdNb")
        serverA = aiding.SocketUxdNb(ha = '/tmp/local/uxdA', umask=0x077)
        serverA.reopen()
        serverB = aiding.SocketUxdNb(ha = '/tmp/local/uxdB', umask=0x077)
        serverB.reopen()
        serverC = aiding.SocketUxdNb(ha = '/tmp/local/uxdC', umask=0x077)
        serverC.reopen()

        serverA.send("A sends to B",serverB.ha)
        print(serverB.receive())
        serverA.send("A sends to C",serverC.ha)
        print(serverC.receive())
        serverA.send("A sends to A",serverA.ha)
        print(serverA.receive())
        serverB.send("B sends to A",serverA.ha)
        print(serverA.receive())
        serverC.send("C sends to A",serverA.ha)
        print(serverA.receive())
        serverB.send("B sends to B",serverB.ha)
        print(serverB.receive())
        serverC.send("C sends to C",serverC.ha)
        print(serverC.receive())

        serverA.send("A sends to B again",serverB.ha)
        print(serverB.receive())
        serverA.send("A sends to C again",serverC.ha)
        print(serverC.receive())
        serverA.send("A sends to A again",serverA.ha)
        print(serverA.receive())
        serverB.send("B sends to A again",serverA.ha)
        print(serverA.receive())
        serverC.send("C sends to A again",serverA.ha)
        print(serverA.receive())
        serverB.send("B sends to B again",serverB.ha)
        print(serverB.receive())
        serverC.send("C sends to C again",serverC.ha)
        print(serverC.receive())

        print(serverA.receive())
        print(serverB.receive())
        print(serverC.receive())


    finally:
        serverA.close()
        serverB.close()
        serverC.close()







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
             'testSocketUdpNB', ]
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

    #runOne('testSocketUdpNB')

