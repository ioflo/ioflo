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

from ioflo.base.globaling import *
#from ioflo.test import testing
from ioflo.base.consoling import getConsole
console = getConsole()

from ioflo.aid import nonblocking

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

    def testConsoleNb(self):
        """
        Test Class ConsoleNB
        """
        console.terse("{0}\n".format(self.testConsoleNb.__doc__))

        myconsole = nonblocking.ConsoleNb()
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

        wire = nonblocking.WireLog(path=logDirpath)
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
        self.assertEqual(result, ns2b("{0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        data = b"Test data Rx"
        wire.writeRx(ha, data)
        wire.rxLog.seek(0)
        result = wire.rxLog.readline()
        result += wire.rxLog.readline()
        self.assertEqual(result, ns2b("{0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        wire.close()
        shutil.rmtree(tempDirpath)

    def testWireLogBuffify(self):
        """
        Test Class WireLog
        """
        console.terse("{0}\n".format(self.testWireLogBuffify.__doc__))

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="log", dir=userDirpath)
        logDirpath = os.path.join(tempDirpath, 'log')
        if not os.path.exists(logDirpath):
            os.makedirs(logDirpath)

        wire = nonblocking.WireLog(path=logDirpath, buffify=True)
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
        self.assertEqual(result, ns2b("{0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        data = b"Test data Rx"
        wire.writeRx(ha, data)
        wire.rxLog.seek(0)
        result = wire.rxLog.readline()
        result += wire.rxLog.readline()
        self.assertEqual(result, ns2b("{0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        wire.close()
        shutil.rmtree(tempDirpath)

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

        wireLog = nonblocking.WireLog(path=logDirpath)
        result = wireLog.reopen(prefix='alpha', midfix='6101')

        alpha = nonblocking.SocketUdpNb(port = 6101, wlog=wireLog)
        self.assertIs(alpha.reopen(), True)

        beta = nonblocking.SocketUdpNb(port = 6102)
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

        wireLog.close()
        shutil.rmtree(tempDirpath)
        console.reinit(verbosity=console.Wordage.concise)

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

        wireLog = nonblocking.WireLog(path=logDirpath)
        result = wireLog.reopen(prefix='alpha', midfix='uxd')


        ha = os.path.join(sockDirpath, 'alpha.uxd')
        alpha = nonblocking.SocketUxdNb(ha=ha, umask=0x077, wlog=wireLog)
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

        wireLog.close()
        shutil.rmtree(tempDirpath)
        console.reinit(verbosity=console.Wordage.concise)

    def testServerClientSocketTcpNb(self):
        """
        Test Classes ServerSocketTcpNb and ClientSocketTcpNb
        """
        console.terse("{0}\n".format(self.testServerClientSocketTcpNb.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="tcp", dir=userDirpath)

        logDirpath = os.path.join(tempDirpath, 'log')
        if not os.path.exists(logDirpath):
            os.makedirs(logDirpath)

        wireLog = nonblocking.WireLog(path=logDirpath)
        result = wireLog.reopen(prefix='alpha', midfix='6101')

        alpha = nonblocking.ServerSocketTcpNb(port = 6101, bufsize=131072, wlog=wireLog)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))

        beta = nonblocking.ClientSocketTcpNb(ha=alpha.eha, bufsize=131072)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        gamma = nonblocking.ClientSocketTcpNb(ha=alpha.eha, bufsize=131072)
        self.assertIs(gamma.reopen(), True)
        self.assertIs(gamma.connected, False)
        self.assertIs(gamma.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        accepteds = []
        while True:
            if not beta.connected:
                beta.connect()
            cs, ca = alpha.accept()
            if cs:
                accepteds.append((cs, ca))
            if beta.connected and accepteds:
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(len(accepteds), 1)
        csBeta, caBeta = accepteds[0]
        self.assertIsNotNone(csBeta)
        self.assertIsNotNone(caBeta)

        self.assertEqual(csBeta.getsockname(), beta.cs.getpeername())
        self.assertEqual(csBeta.getpeername(), beta.cs.getsockname())
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertEqual(caBeta, beta.ca)

        msgOut = b"Beta sends to Alpha"
        count = beta.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgOut, msgIn)

        # receive without sending
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgIn, None)

        # send multiple
        msgOut1 = b"First Message"
        count = beta.send(msgOut1)
        self.assertEqual(count, len(msgOut1))
        msgOut2 = b"Second Message"
        count = beta.send(msgOut2)
        self.assertEqual(count, len(msgOut2))
        time.sleep(0.05)
        msgIn  = alpha.receive(csBeta)
        self.assertEqual(msgIn, msgOut1 + msgOut2)

        # send from alpha to beta
        msgOut = b"Alpha sends to Beta"
        count = alpha.send(msgOut, csBeta)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = beta.receive()
        self.assertEqual(msgOut, msgIn)

        # receive without sending
        msgIn = beta.receive()
        self.assertEqual(msgIn, None)

        # build message too big to fit in buffer
        sizes = beta.actualBufSizes()
        size = sizes[0]
        msgOut = b""
        count = 0
        while (len(msgOut) <= size * 4):
            msgOut += ns2b("{0:0>7d} ".format(count))
            count += 1
        self.assertTrue(len(msgOut) >= size * 4)

        msgIn = b''
        count = 0
        while len(msgIn) < len(msgOut):
            if count < len(msgOut):
                count += beta.send(msgOut[count:])
            time.sleep(0.05)
            msgIn += alpha.receive(csBeta)
        self.assertEqual(count, len(msgOut))
        self.assertEqual(msgOut, msgIn)

        console.terse("Connecting gamma to alpha\n")
        accepteds = []
        while True:
            if not gamma.connected:
                gamma.connect()
            cs, ca = alpha.accept()
            if cs:
                accepteds.append((cs, ca))
            if gamma.connected and accepteds:
                break
            time.sleep(0.05)

        self.assertIs(gamma.connected, True)
        self.assertIs(gamma.cutoff, False)
        self.assertEqual(len(accepteds), 1)
        csGamma, caGamma = accepteds[0]
        self.assertIsNotNone(csGamma)
        self.assertIsNotNone(caGamma)

        self.assertEqual(csGamma.getsockname(), gamma.cs.getpeername())
        self.assertEqual(csGamma.getpeername(), gamma.cs.getsockname())
        self.assertEqual(gamma.ca, gamma.cs.getsockname())
        self.assertEqual(gamma.ha, gamma.cs.getpeername())
        self.assertEqual(caGamma, gamma.ca)

        msgOut = b"Gamma sends to Alpha"
        count = gamma.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = alpha.receive(csGamma)
        self.assertEqual(msgOut, msgIn)

        # receive without sending
        msgIn = alpha.receive(csGamma)
        self.assertEqual(msgIn, None)

        # send from alpha to gamma
        msgOut = b"Alpha sends to Gamma"
        count = alpha.send(msgOut, csGamma)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgOut, msgIn)

        # recieve without sending
        msgIn = gamma.receive()
        self.assertEqual(msgIn, None)

        # close beta and then attempt to send
        beta.close()
        msgOut = b"Send on closed socket"
        with self.assertRaises(AttributeError) as cm:
            count = beta.send(msgOut)

        # attempt to receive on closed socket
        with self.assertRaises(AttributeError) as cm:
            msgIn = beta.receive()

        # read on alpha after closed beta
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgIn, b'')

        # send on alpha after close beta
        msgOut = b"Alpha sends to Beta after close"
        count = alpha.send(msgOut, csBeta)
        self.assertEqual(count, len(msgOut)) #apparently works

        csBeta.close()

        # send on gamma then shutdown sends
        msgOut = b"Gamma sends to Alpha"
        count = gamma.send(msgOut)
        self.assertEqual(count, len(msgOut))
        gamma.shutdownSend()
        time.sleep(0.05)
        msgIn = alpha.receive(csGamma)
        self.assertEqual(msgOut, msgIn)
        msgIn = alpha.receive(csGamma)
        self.assertEqual(msgIn, b'')  # gamma shutdown detected
        # send from alpha to gamma and shutdown
        msgOut = b"Alpha sends to Gamma"
        count = alpha.send(msgOut, csGamma)
        self.assertEqual(count, len(msgOut))

        alpha.shutdown(csGamma)  # shutdown alpha
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgOut, msgIn)
        msgIn = gamma.receive()
        self.assertEqual(msgIn, None)  # alpha shutdown not detected
        self.assertIs(gamma.cutoff, False)
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgIn, None)  # alpha shutdown not detected
        self.assertIs(gamma.cutoff, False)

        alpha.shutclose(csGamma)  # close alpha
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgIn, b'')  # alpha close is detected
        self.assertIs(gamma.cutoff, True)

        # reopen beta
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        accepteds = []
        while True:
            if not beta.connected:
                beta.connect()
            cs, ca = alpha.accept()
            if cs:
                accepteds.append((cs, ca))
            if beta.connected and accepteds:
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(len(accepteds), 1)
        csBeta, caBeta = accepteds[0]
        self.assertIsNotNone(csBeta)
        self.assertIsNotNone(caBeta)

        self.assertEqual(csBeta.getsockname(), beta.cs.getpeername())
        self.assertEqual(csBeta.getpeername(), beta.cs.getsockname())
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertEqual(caBeta, beta.ca)

        msgOut = b"Beta sends to Alpha"
        count = beta.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgOut, msgIn)

        # send from alpha to beta
        msgOut = b"Alpha sends to Beta"
        count = alpha.send(msgOut, csBeta)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = beta.receive()
        self.assertEqual(msgOut, msgIn)

        # send then shutdown alpha and then attempt to send
        msgOut1 = b"Alpha sends to Beta"
        count = alpha.send(msgOut, csBeta)
        self.assertEqual(count, len(msgOut1))
        alpha.shutdownSend(csBeta)
        msgOut2 = b"Send on shutdown socket"
        with self.assertRaises(socket.error) as cm:
            count = alpha.send(msgOut, csBeta)
        self.assertTrue(cm.exception.errno == errno.EPIPE)
        time.sleep(0.05)
        msgIn = beta.receive()
        self.assertEqual(msgOut1, msgIn)
        msgIn = beta.receive()
        self.assertEqual(msgIn, b'')  # beta detects shutdown socket
        self.assertIs(beta.cutoff, True)

        msgOut = b"Beta sends to Alpha"
        count = beta.send(msgOut)
        self.assertEqual(count, len(msgOut))
        beta.shutdown()
        time.sleep(0.05)
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgOut, msgIn)
        time.sleep(0.05)
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgIn, None)  # alpha does not detect shutdown
        beta.close()
        time.sleep(0.05)
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgIn, b'')  # alpha detects closed socket

        csBeta.close()

        # reopen gamma
        self.assertIs(gamma.reopen(), True)
        self.assertIs(gamma.connected, False)
        self.assertIs(gamma.cutoff, False)

        console.terse("Connecting gamma to alpha\n")
        accepteds = []
        while True:
            if not gamma.connected:
                gamma.connect()
            cs, ca = alpha.accept()
            if cs:
                accepteds.append((cs, ca))
            if gamma.connected and accepteds:
                break
            time.sleep(0.05)

        self.assertIs(gamma.connected, True)
        self.assertIs(gamma.cutoff, False)

        self.assertEqual(len(accepteds), 1)
        csGamma, caGamma = accepteds[0]
        self.assertIsNotNone(csGamma)
        self.assertIsNotNone(caGamma)

        self.assertEqual(csGamma.getsockname(), gamma.cs.getpeername())
        self.assertEqual(csGamma.getpeername(), gamma.cs.getsockname())
        self.assertEqual(gamma.ca, gamma.cs.getsockname())
        self.assertEqual(gamma.ha, gamma.cs.getpeername())
        self.assertEqual(caGamma, gamma.ca)

        msgOut = b"Gamma sends to Alpha"
        count = gamma.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = alpha.receive(csGamma)
        self.assertEqual(msgOut, msgIn)

        gamma.close()
        time.sleep(0.05)
        msgIn = alpha.receive(csGamma)
        self.assertEqual(msgIn, b'')  # alpha detects close

        csGamma.close()

        # reopen gamma
        self.assertIs(gamma.reopen(), True)
        self.assertIs(gamma.connected, False)
        self.assertIs(gamma.cutoff, False)

        console.terse("Connecting gamma to alpha\n")
        accepteds = []
        while True:
            if not gamma.connected:
                gamma.connect()
            cs, ca = alpha.accept()
            if cs:
                accepteds.append((cs, ca))
            if gamma.connected and accepteds:
                break
            time.sleep(0.05)

        self.assertIs(gamma.connected, True)
        self.assertIs(gamma.cutoff, False)
        self.assertEqual(len(accepteds), 1)
        csGamma, caGamma = accepteds[0]
        self.assertIsNotNone(csGamma)
        self.assertIsNotNone(caGamma)

        self.assertEqual(csGamma.getsockname(), gamma.cs.getpeername())
        self.assertEqual(csGamma.getpeername(), gamma.cs.getsockname())
        self.assertEqual(gamma.ca, gamma.cs.getsockname())
        self.assertEqual(gamma.ha, gamma.cs.getpeername())
        self.assertEqual(caGamma, gamma.ca)

        # send from alpha to gamma
        msgOut = b"Alpha sends to Gamma"
        count = alpha.send(msgOut, csGamma)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgOut, msgIn)

        alpha.shutclose(csGamma)
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgIn, b'')  # gamma detects close
        self.assertIs(gamma.cutoff, True)

        alpha.close()
        beta.close()
        gamma.close()

        wireLog.close()
        shutil.rmtree(tempDirpath)
        console.reinit(verbosity=console.Wordage.concise)

    def testSocketTcpNb(self):
        """
        Test Class SocketTcpNb
        """
        console.terse("{0}\n".format(self.testSocketTcpNb.__doc__))

        alpha = nonblocking.SocketTcpNb(port = 6101)
        self.assertIs(alpha.reopen(), True)
        alphaHa = ("127.0.0.1", alpha.ha[1])

        beta = nonblocking.SocketTcpNb(port = 6102)
        self.assertIs(beta.reopen(), True)
        betaHa = ("127.0.0.1", beta.ha[1])

        gamma = nonblocking.SocketTcpNb(port = 6103)
        self.assertIs(gamma.reopen(), True)
        gammaHa = ("127.0.0.1", gamma.ha[1])

        console.terse("Connecting beta to alpha\n")
        result = beta.connect(alphaHa)
        while alphaHa not in beta.peers:
            beta.service()
            alpha.service()

        betaPeerCa, betaPeerCs = beta.peers.items()[0]
        alphaPeerCa, alphaPeerCs = alpha.peers.items()[0]

        self.assertEqual(betaPeerCs.getpeername(), betaPeerCa)
        self.assertEqual(betaPeerCs.getsockname(), alphaPeerCa)
        self.assertEqual(alphaPeerCs.getpeername(), alphaPeerCa)
        self.assertEqual(alphaPeerCs.getsockname(), betaPeerCa)

        msgOut = b"beta sends to alpha"
        count = beta.send(msgOut, alphaHa)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        receptions = alpha.receiveAll()
        msgIn, src = receptions[0]
        self.assertEqual(msgOut, msgIn)

        # read without sending
        ca, cs = alpha.peers.items()[0]
        msgIn, src = alpha.receive(ca)
        self.assertEqual(msgIn, '')
        self.assertEqual(src, None)

        # send multiple
        msgOut1 = b"First Message"
        count = beta.send(msgOut1, alphaHa)
        self.assertEqual(count, len(msgOut1))
        msgOut2 = b"Second Message"
        count = beta.send(msgOut2, alphaHa)
        self.assertEqual(count, len(msgOut2))
        time.sleep(0.05)
        ca, cs = alpha.peers.items()[0]
        msgIn, src = alpha.receive(ca)
        self.assertEqual(msgIn, msgOut1 + msgOut2)
        self.assertEqual(src, ca)


        # build message too big to fit in buffer
        sizes = beta.actualBufSizes()
        size = sizes[0]
        msgOut = b""
        count = 0
        while (len(msgOut) <= size * 4):
            msgOut += ns2b("{0:0>7d} ".format(count))
            count += 1
        self.assertTrue(len(msgOut) >= size * 4)

        count = 0
        while count < len(msgOut):
            count += beta.send(msgOut[count:], alphaHa)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = b''
        ca, cs = alpha.peers.items()[0]
        count = 0
        while len(msgIn) < len(msgOut):
            rx, src = alpha.receive(ca, bs=len(msgOut))
            count += 1
            msgIn += rx
            time.sleep(0.05)

        self.assertTrue(count > 1)
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src, ca)

        # Close connection on far side and then read from it near side
        ca, cs = beta.peers.items()[0]
        beta.unconnectPeer(ca)
        self.assertEqual(len(beta.peers), 0)
        time.sleep(0.05)
        msgOut = b"Send on unconnected socket"
        with self.assertRaises(ValueError):
            count = beta.send(msgOut, ca)

        #beta.closeshut(cs)
        with self.assertRaises(socket.error) as cm:
            count = cs.send(msgOut)
        self.assertTrue(cm.exception.errno == errno.EBADF)

        ca, cs = alpha.peers.items()[0]
        msgIn, src = alpha.receive(ca)
        self.assertEqual(msgIn, b'')
        self.assertEqual(src, ca)  # means closed if empty but ca not None


        alpha.closeAll()
        beta.closeAll()
        gamma.closeAll()


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
    names = ['testConsoleNb',
             'testWireLog',
             'testWireLogBuffify',
             'testSocketUdpNb',
             'testSocketUxdNb',
             'testServerClientSocketTcpNb',
             'testSocketTcpNb', ]
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

    #runOne('testWireLog')

