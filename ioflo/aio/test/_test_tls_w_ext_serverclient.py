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
import socket
import errno

from ioflo.aid.sixing import *
from ioflo.aid.consoling import getConsole
console = getConsole()

from ioflo.aio import nonblocking

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


    def testClientTLS(self):
        """
        Test OutgoerTLS class  NonBlocking TCP/IP with TLS client
        Wrapped with ssl context
        """
        try:
            import ssl
        except ImportError:
            return

        console.terse("{0}\n".format(self.testClientTLS.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        wireLogBeta = nonblocking.WireLog(buffify=True, same=True)
        result = wireLogBeta.reopen()
        #serverHa = ("127.0.0.1", 8080)
        serverHa = ("localhost", 8080)
        #serverHa = ("google.com", 443)

        keypath = '/etc/pki/tls/certs/client_key.pem'  # local private key
        certpath = '/etc/pki/tls/certs/client_cert.pem'  # local public cert
        cafilepath = '/etc/pki/tls/certs/localhost.crt' # remote public cert
        beta = nonblocking.OutgoerTls(ha=serverHa,
                                      bufsize=131072,
                                      wlog=wireLogBeta,
                                      context=None,
                                      version=ssl.PROTOCOL_TLSv1,
                                      certify=ssl.CERT_REQUIRED,
                                      keypath=keypath,
                                      certpath=certpath,
                                      cafilepath=cafilepath,
                                      hostify=True,
                                      certedhost="localhost")
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta\n")
        while True:
            beta.serviceConnect()
            if beta.accepted:
                break
            time.sleep(0.05)

        self.assertIs(beta.accepted, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        #self.assertEqual(beta.ha, serverHa)

        console.terse("Handshaking beta\n")
        while True:
            beta.serviceConnect()
            if beta.connected:
                break
            time.sleep(0.01)

        self.assertIs(beta.connected, True)

        msgOut = b"GET /echo HTTP/1.0\r\n\r\n"
        beta.tx(msgOut)
        while beta.txes:
            beta.serviceTxes()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        beta.clearRxbs()
        self.assertTrue(msgIn.startswith(b'HTTP/1.1 200 OK\r\nContent-Length: '))
        self.assertTrue(msgIn.endswith(b'/echo", "action": null}'))

        beta.close()

        # repeat but only call serviceConnect which calls connect
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting and Handshaking beta\n")
        while True:
            beta.serviceConnect()
            if beta.connected:
                break
            time.sleep(0.01)

        self.assertIs(beta.accepted, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertIs(beta.connected, True)

        msgOut = b"GET /echo HTTP/1.0\r\n\r\n"
        beta.tx(msgOut)
        while beta.txes:
            beta.serviceTxes()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        beta.clearRxbs()
        self.assertTrue(msgIn.startswith(b'HTTP/1.1 200 OK\r\nContent-Length: '))
        self.assertTrue(msgIn.endswith(b'/echo", "action": null}'))

        beta.close()

        wlBetaRx = wireLogBeta.getRx()
        wlBetaTx = wireLogBeta.getTx()
        self.assertEqual(wlBetaRx, wlBetaTx)  # since wlog is same

        wireLogBeta.close()
        console.reinit(verbosity=console.Wordage.concise)

    def testClientTLSDefault(self):
        """
        Test OutgoerTLS class  NonBlocking TCP/IP with TLS client
        Wrapped with ssl default context
        """
        try:
            import ssl
        except ImportError:
            return

        console.terse("{0}\n".format(self.testClientTLSDefault.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        wireLogBeta = nonblocking.WireLog(buffify=True, same=True)
        result = wireLogBeta.reopen()
        #serverHa = ("127.0.0.1", 8080)
        serverHa = ("localhost", 8080)
        #serverHa = ("google.com", 443)

        keypath = '/etc/pki/tls/certs/client_key.pem'  # local private key
        certpath = '/etc/pki/tls/certs/client_cert.pem'  # local public cert
        cafilepath = '/etc/pki/tls/certs/localhost.crt' # remote public cert
        beta = nonblocking.OutgoerTls(ha=serverHa,
                                      bufsize=131072,
                                      wlog=wireLogBeta,
                                      context=None,
                                      version=None,
                                      certify=None,
                                      keypath=keypath,
                                      certpath=certpath,
                                      cafilepath=cafilepath,
                                      hostify=None,
                                      certedhost="localhost")
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting  and Handshaking beta\n")
        while True:
            beta.serviceConnect()
            if beta.connected:
                break
            time.sleep(0.01)

        self.assertIs(beta.accepted, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertIs(beta.connected, True)

        msgOut = b"GET /echo HTTP/1.0\r\n\r\n"
        beta.tx(msgOut)
        while beta.txes:
            beta.serviceTxes()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        beta.clearRxbs()
        self.assertTrue(msgIn.startswith(b'HTTP/1.1 200 OK\r\nContent-Length: '))
        self.assertTrue(msgIn.endswith(b'/echo", "action": null}'))

        beta.close()

        wlBetaRx = wireLogBeta.getRx()
        wlBetaTx = wireLogBeta.getTx()
        self.assertEqual(wlBetaRx, wlBetaTx)  # since wlog is same

        wireLogBeta.close()
        console.reinit(verbosity=console.Wordage.concise)

    def testClientServerTLSService(self):
        """
        Test Classes ServerTLS service methods
        """
        try:
            import ssl
        except ImportError:
            return

        console.terse("{0}\n".format(self.testClientServerTLSService.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        wireLogAlpha = nonblocking.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = nonblocking.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        serverKeypath = '/etc/pki/tls/certs/server_key.pem'  # local private key
        serverCertpath = '/etc/pki/tls/certs/server_cert.pem'  # local public cert
        clientCafilepath = '/etc/pki/tls/certs/client.pem' # remote public cert

        alpha = nonblocking.ServerTls(host='localhost',
                                      port = 6101,
                                      bufsize=131072,
                                      wlog=wireLogAlpha,
                                      certify=ssl.CERT_NONE,
                                      keypath=serverKeypath,
                                      certpath=serverCertpath,
                                      cafilepath=clientCafilepath,
                                      )
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('127.0.0.1', 6101))

        #beta = nonblocking.OutgoerTLS(ha=alpha.eha,
                                      #bufsize=131072,
                                      #wlog=wireLogBeta)
        #self.assertIs(beta.reopen(), True)
        #self.assertIs(beta.accepted, False)
        #self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        while True:
            #beta.serviceConnect()
            alpha.serviceConnects()
            #if beta.accepted and beta.ca in alpha.ixes:
                #break
            if len(alpha.ixes) == 1:
                break
            time.sleep(0.05)

        #self.assertIs(beta.accepted, True)
        #self.assertIs(beta.cutoff, False)
        #self.assertEqual(beta.ca, beta.cs.getsockname())
        #self.assertEqual(beta.ha, beta.cs.getpeername())
        #self.assertEqual(alpha.eha, beta.ha)
        #ixBeta = alpha.ixes[beta.ca]
        #self.assertIsNotNone(ixBeta.ca)
        #self.assertIsNotNone(ixBeta.cs)

        #self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        #self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        #self.assertEqual(ixBeta.ca, beta.ca)
        #self.assertEqual(ixBeta.ha, beta.ha)

        #msgOut = b"Beta sends to Alpha"
        #beta.transmit(msgOut)
        #while not ixBeta.rxbs and beta.txes:
            #beta.serviceTxes()
            #alpha.serviceAllRxAllIx()
            #time.sleep(0.05)
        #msgIn = bytes(ixBeta.rxbs)
        #self.assertEqual(msgIn, msgOut)
        #index = len(ixBeta.rxbs)

        ix = alpha.ixes.values()[0]
        while True:
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
            if ix.rxbs:
                break

        time.sleep(0.05)
        alpha.serviceReceivesAllIx()

        msgIn = bytes(ix.rxbs)
        #self.assertEqual(msgIn, msgOut)
        index = len(ix.rxbs)

        msgOut = b'Wait what?'
        ix.tx(msgOut)
        while ix.txes:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)


        alpha.close()
        #beta.close()

        wireLogAlpha.close()
        #wireLogBeta.close()
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
             'testClientTLS',
             'testClientTLSDefault',
             'testClientServerTLSService',
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

    #runOne('testClientTLS')


