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
        self.assertEqual(result, ns2b("TX {0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        data = b"Test data Rx"
        wire.writeRx(ha, data)
        wire.rxLog.seek(0)
        result = wire.rxLog.readline()
        result += wire.rxLog.readline()
        self.assertEqual(result, ns2b("RX {0}\n{1}\n".format(ha, data.decode('ISO-8859-1'))))

        wire.close()

        wire = nonblocking.WireLog(path=logDirpath, same=True)
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

        wire = nonblocking.WireLog(buffify=True)
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

        wire = nonblocking.WireLog(buffify=True, same=True)
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

    def testClientServer(self):
        """
        Test Classes Client (Outgoer) and Server with Incomers
        """
        console.terse("{0}\n".format(self.testClientServer.__doc__))
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

        alpha = nonblocking.Server(port = 6101, bufsize=131072, wlog=wireLog)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))

        beta = nonblocking.Client(ha=alpha.eha, bufsize=131072)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        gamma = nonblocking.Client(ha=alpha.eha, bufsize=131072)
        self.assertIs(gamma.reopen(), True)
        self.assertIs(gamma.connected, False)
        self.assertIs(gamma.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceAccepts()
            if beta.connected and beta.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertEqual(alpha.eha, beta.ha)
        ixBeta = alpha.ixes[beta.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)

        self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.ca)
        self.assertEqual(ixBeta.ha, beta.ha)

        msgOut = b"Beta sends to Alpha"
        count = beta.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = ixBeta.receive()
        self.assertEqual(msgOut, msgIn)

        # receive without sending
        msgIn = ixBeta.receive()
        self.assertEqual(msgIn, None)

        # send multiple
        msgOut1 = b"First Message"
        count = beta.send(msgOut1)
        self.assertEqual(count, len(msgOut1))
        msgOut2 = b"Second Message"
        count = beta.send(msgOut2)
        self.assertEqual(count, len(msgOut2))
        time.sleep(0.05)
        msgIn  = ixBeta.receive()
        self.assertEqual(msgIn, msgOut1 + msgOut2)

        # send from alpha to beta
        msgOut = b"Alpha sends to Beta"
        count = ixBeta.send(msgOut)
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
            msgIn += ixBeta.receive()
        self.assertEqual(count, len(msgOut))
        self.assertEqual(msgOut, msgIn)

        console.terse("Connecting gamma to alpha\n")
        while True:
            gamma.serviceConnect()
            alpha.serviceAccepts()
            if gamma.connected and gamma.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(gamma.connected, True)
        self.assertIs(gamma.cutoff, False)
        self.assertEqual(gamma.ca, gamma.cs.getsockname())
        self.assertEqual(gamma.ha, gamma.cs.getpeername())
        self.assertEqual(alpha.eha, gamma.ha)
        ixGamma = alpha.ixes[gamma.ca]
        self.assertIsNotNone(ixGamma.ca)
        self.assertIsNotNone(ixGamma.cs)

        self.assertEqual(ixGamma.cs.getsockname(), gamma.cs.getpeername())
        self.assertEqual(ixGamma.cs.getpeername(), gamma.cs.getsockname())
        self.assertEqual(ixGamma.ca, gamma.ca)
        self.assertEqual(ixGamma.ha, gamma.ha)

        msgOut = b"Gamma sends to Alpha"
        count = gamma.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = ixGamma.receive()
        self.assertEqual(msgOut, msgIn)

        # receive without sending
        msgIn = ixGamma.receive()
        self.assertEqual(msgIn, None)

        # send from alpha to gamma
        msgOut = b"Alpha sends to Gamma"
        count = ixGamma.send(msgOut)
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
        msgIn = ixBeta.receive()
        self.assertEqual(msgIn, b'')

        # send on alpha after close beta
        msgOut = b"Alpha sends to Beta after close"
        count = ixBeta.send(msgOut)
        self.assertEqual(count, len(msgOut)) #apparently works

        ixBeta.close()
        del alpha.ixes[ixBeta.ca]

        # send on gamma then shutdown sends
        msgOut = b"Gamma sends to Alpha"
        count = gamma.send(msgOut)
        self.assertEqual(count, len(msgOut))
        gamma.shutdownSend()
        time.sleep(0.05)
        msgIn = ixGamma.receive()
        self.assertEqual(msgOut, msgIn)
        msgIn = ixGamma.receive()
        self.assertEqual(msgIn, b'')  # gamma shutdown detected
        # send from alpha to gamma and shutdown
        msgOut = b"Alpha sends to Gamma"
        count = ixGamma.send(msgOut)
        self.assertEqual(count, len(msgOut))

        ixGamma.shutdown()  # shutdown alpha
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

        ixGamma.shutclose()  # close alpha
        del alpha.ixes[ixGamma.ca]
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgIn, b'')  # alpha close is detected
        self.assertIs(gamma.cutoff, True)

        # reopen beta
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceAccepts()
            if beta.connected and beta.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertEqual(alpha.eha, beta.ha)
        ixBeta = alpha.ixes[beta.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)

        self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.ca)
        self.assertEqual(ixBeta.ha, beta.ha)

        msgOut = b"Beta sends to Alpha"
        count = beta.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = ixBeta.receive()
        self.assertEqual(msgOut, msgIn)

        # send from alpha to beta
        msgOut = b"Alpha sends to Beta"
        count = ixBeta.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = beta.receive()
        self.assertEqual(msgOut, msgIn)

        # send then shutdown alpha and then attempt to send
        msgOut1 = b"Alpha sends to Beta"
        count = ixBeta.send(msgOut)
        self.assertEqual(count, len(msgOut1))
        ixBeta.shutdownSend()
        msgOut2 = b"Send on shutdown socket"
        with self.assertRaises(socket.error) as cm:
            count = ixBeta.send(msgOut)
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
        msgIn = ixBeta.receive()
        self.assertEqual(msgOut, msgIn)
        time.sleep(0.05)
        msgIn = ixBeta.receive()
        self.assertEqual(msgIn, None)  # alpha does not detect shutdown
        beta.close()
        time.sleep(0.05)
        msgIn = ixBeta.receive()
        self.assertEqual(msgIn, b'')  # alpha detects closed socket

        ixBeta.close()
        del alpha.ixes[ixBeta.ca]

        # reopen gamma
        self.assertIs(gamma.reopen(), True)
        self.assertIs(gamma.connected, False)
        self.assertIs(gamma.cutoff, False)

        console.terse("Connecting gamma to alpha\n")
        while True:
            gamma.serviceConnect()
            alpha.serviceAccepts()
            if gamma.connected and gamma.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(gamma.connected, True)
        self.assertIs(gamma.cutoff, False)
        self.assertEqual(gamma.ca, gamma.cs.getsockname())
        self.assertEqual(gamma.ha, gamma.cs.getpeername())
        self.assertEqual(alpha.eha, gamma.ha)
        ixGamma = alpha.ixes[gamma.ca]
        self.assertIsNotNone(ixGamma.ca)
        self.assertIsNotNone(ixGamma.cs)

        self.assertEqual(ixGamma.cs.getsockname(), gamma.cs.getpeername())
        self.assertEqual(ixGamma.cs.getpeername(), gamma.cs.getsockname())
        self.assertEqual(ixGamma.ca, gamma.ca)
        self.assertEqual(ixGamma.ha, gamma.ha)

        msgOut = b"Gamma sends to Alpha"
        count = gamma.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = ixGamma.receive()
        self.assertEqual(msgOut, msgIn)

        gamma.close()
        time.sleep(0.05)
        msgIn = ixGamma.receive()
        self.assertEqual(msgIn, b'')  # alpha detects close

        ixGamma.close()
        del alpha.ixes[ixGamma.ca]

        # reopen gamma
        self.assertIs(gamma.reopen(), True)
        self.assertIs(gamma.connected, False)
        self.assertIs(gamma.cutoff, False)

        console.terse("Connecting gamma to alpha\n")
        while True:
            gamma.serviceConnect()
            alpha.serviceAccepts()
            if gamma.connected and gamma.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(gamma.connected, True)
        self.assertIs(gamma.cutoff, False)
        self.assertEqual(gamma.ca, gamma.cs.getsockname())
        self.assertEqual(gamma.ha, gamma.cs.getpeername())
        self.assertEqual(alpha.eha, gamma.ha)
        ixGamma = alpha.ixes[gamma.ca]
        self.assertIsNotNone(ixGamma.ca)
        self.assertIsNotNone(ixGamma.cs)

        self.assertEqual(ixGamma.cs.getsockname(), gamma.cs.getpeername())
        self.assertEqual(ixGamma.cs.getpeername(), gamma.cs.getsockname())
        self.assertEqual(ixGamma.ca, gamma.ca)
        self.assertEqual(ixGamma.ha, gamma.ha)

        # send from alpha to gamma
        msgOut = b"Alpha sends to Gamma"
        count = ixGamma.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgOut, msgIn)

        ixGamma.shutclose()
        del alpha.ixes[ixGamma.ca]
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

    def testClientServerServiceCat(self):
        """
        Test Classes ServerSocketTcpNb service methods that use catRxes

        """
        console.terse("{0}\n".format(self.testClientServerServiceCat.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="tcp", dir=userDirpath)

        logDirpath = os.path.join(tempDirpath, 'log')
        if not os.path.exists(logDirpath):
            os.makedirs(logDirpath)

        wireLogAlpha = nonblocking.WireLog(path=logDirpath, same=True)
        result = wireLogAlpha.reopen(prefix='alpha', midfix='6101')

        wireLogBeta = nonblocking.WireLog(buffify=True)
        result = wireLogBeta.reopen()

        alpha = nonblocking.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))

        beta = nonblocking.Outgoer(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceAccepts()
            if beta.connected and beta.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertEqual(alpha.eha, beta.ha)
        ixBeta = alpha.ixes[beta.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)

        self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.ca)
        self.assertEqual(ixBeta.ha, beta.ha)

        msgOut = b"Beta sends to Alpha"
        beta.transmit(msgOut)
        msgIn = b''
        while not msgIn and beta.txes:
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            msgIn += ixBeta.catRxes()
            time.sleep(0.05)
        self.assertEqual(msgOut, msgIn)

        # send multiple
        msgOut1 = b"First Message"
        beta.transmit(msgOut1)
        msgOut2 = b"Second Message"
        beta.transmit(msgOut2)
        msgIn = b''
        while len(msgIn) < len(msgOut1 + msgOut2):
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            msgIn += ixBeta.catRxes()
            time.sleep(0.05)

        self.assertEqual(msgIn, msgOut1 + msgOut2)

        # build message too big to fit in buffer
        sizes = beta.actualBufSizes()
        size = sizes[0]
        msgOutBig = b""
        count = 0
        while (len(msgOutBig) <= size * 4):
            msgOutBig += ns2b("{0:0>7d} ".format(count))
            count += 1
        self.assertTrue(len(msgOutBig) >= size * 4)

        beta.transmit(msgOutBig)
        msgIn = b''
        count = 0
        while len(msgIn) < len(msgOutBig):
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            msgIn += ixBeta.catRxes()
            time.sleep(0.05)

        self.assertEqual(msgIn, msgOutBig)

        # send from alpha to beta
        msgOut = b"Alpha sends to Beta"
        ixBeta.transmit(msgOut)
        msgIn = b''
        while len(msgIn) < len(msgOut):
            alpha.serviceTxesAllIx()
            beta.serviceReceives()
            msgIn += beta.catRxes()
            time.sleep(0.05)

        self.assertEqual(msgIn, msgOut)

        # send big from alpha to beta
        ixBeta.transmit(msgOutBig)
        msgIn = b''
        while len(msgIn) < len(msgOutBig):
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
            msgIn += beta.catRxes()
            time.sleep(0.05)

        self.assertEqual(msgIn, msgOutBig)

        alpha.close()
        beta.close()

        wlBetaRx = wireLogBeta.getRx()
        self.assertTrue(wlBetaRx.startswith(b"RX ('127.0.0.1', 6101)\nAlpha sends to Beta\n"))
        wlBetaTx = wireLogBeta.getTx()
        self.assertTrue(wlBetaTx.startswith(b"TX ('127.0.0.1', 6101)\nBeta sends to Alpha\n"))

        wireLogAlpha.close()
        wireLogBeta.close()
        shutil.rmtree(tempDirpath)
        console.reinit(verbosity=console.Wordage.concise)

    def testClientServerService(self):
        """
        Test Classes ServerSocketTcpNb service methods
        """
        console.terse("{0}\n".format(self.testClientServerService.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="tcp", dir=userDirpath)

        logDirpath = os.path.join(tempDirpath, 'log')
        if not os.path.exists(logDirpath):
            os.makedirs(logDirpath)

        wireLogAlpha = nonblocking.WireLog(path=logDirpath, same=True)
        result = wireLogAlpha.reopen(prefix='alpha', midfix='6101')

        wireLogBeta = nonblocking.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        alpha = nonblocking.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))

        beta = nonblocking.Outgoer(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceAccepts()
            if beta.connected and beta.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertEqual(alpha.eha, beta.ha)
        ixBeta = alpha.ixes[beta.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)

        self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.ca)
        self.assertEqual(ixBeta.ha, beta.ha)

        msgOut = b"Beta sends to Alpha"
        beta.transmit(msgOut)
        while not ixBeta.rxbs and beta.txes:
            beta.serviceTxes()
            alpha.serviceAllRxAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        index = len(ixBeta.rxbs)

        # send multiple
        msgOut1 = b"First Message"
        beta.transmit(msgOut1)
        msgOut2 = b"Second Message"
        beta.transmit(msgOut2)
        while len(ixBeta.rxbs) < len(msgOut1 + msgOut2):
            beta.serviceTxes()
            alpha.serviceAllRxAllIx()
            time.sleep(0.05)
        msgIn, index = ixBeta.tailRxbs(index)
        self.assertEqual(msgIn, msgOut1 + msgOut2)
        ixBeta.clearRxbs()

        # build message too big to fit in buffer
        sizes = beta.actualBufSizes()
        size = sizes[0]
        msgOutBig = b""
        count = 0
        while (len(msgOutBig) <= size * 4):
            msgOutBig += ns2b("{0:0>7d} ".format(count))
            count += 1
        self.assertTrue(len(msgOutBig) >= size * 4)

        beta.transmit(msgOutBig)
        count = 0
        while len(ixBeta.rxbs) < len(msgOutBig):
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceAllRxAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        ixBeta.clearRxbs()
        self.assertEqual(msgIn, msgOutBig)

        # send from alpha to beta
        msgOut = b"Alpha sends to Beta"
        ixBeta.transmit(msgOut)
        while len(beta.rxbs) < len(msgOut):
            alpha.serviceTxesAllIx()
            beta.serviceAllRx()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        beta.clearRxbs()
        self.assertEqual(msgIn, msgOut)

        # send big from alpha to beta
        ixBeta.transmit(msgOutBig)
        while len(beta.rxbs) < len(msgOutBig):
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceAllRx()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        beta.clearRxbs()
        self.assertEqual(msgIn, msgOutBig)

        alpha.close()
        beta.close()

        wlBetaRx = wireLogBeta.getRx()
        wlBetaTx = wireLogBeta.getTx()
        self.assertEqual(wlBetaRx, wlBetaTx)  # since wlog is same

        wireLogAlpha.close()
        wireLogBeta.close()
        shutil.rmtree(tempDirpath)
        console.reinit(verbosity=console.Wordage.concise)



    def testClientTLS(self):
        """
        Test OutgoerTLS class  NonBlocking TCP/IP with TLS client
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
        beta = nonblocking.OutgoerTLS(ha=serverHa,
                                      bufsize=131072,
                                      wlog=wireLogBeta,
                                      version=ssl.PROTOCOL_TLSv1,
                                      certify=ssl.CERT_NONE,
                                      keypath=None,
                                      certpath=None,
                                      cafilepath=None,
                                      serverHostname="localhost")
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta\n")
        while True:
            beta.serviceConnect()
            if beta.connected:
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        #self.assertEqual(beta.ha, serverHa)

        console.terse("Handshaking beta\n")
        while True:
            beta.serviceHandshake()
            if beta.handshaked:
                break
            time.sleep(0.05)

        self.assertIs(beta.handshaked, True)

        msgOut = b"GET /echo HTTP/1.0\r\n\r\n"
        beta.transmit(msgOut)
        while beta.txes:
            beta.serviceTxes()
            time.sleep(0.05)
            beta.serviceAllRx()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        beta.clearRxbs()
        self.assertTrue(msgIn.startswith(b'HTTP/1.1 200 OK\r\nContent-Length: 103\r\nContent-Type: application/json\r\n'))
        self.assertTrue(msgIn.endswith(b'{"content": null, "query": {}, "verb": "GET", "url": "http://sibook.private:8080/echo", "action": null}'))

        beta.close()

        wlBetaRx = wireLogBeta.getRx()
        wlBetaTx = wireLogBeta.getTx()
        self.assertEqual(wlBetaRx, wlBetaTx)  # since wlog is same

        wireLogBeta.close()
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
    names = ['testConsoleNb',
             'testWireLog',
             'testWireLogBuffify',
             'testSocketUdpNb',
             'testSocketUxdNb',
             'testClientServer',
             'testClientServerServiceCat',
             'testClientServerService',
             'testClientTLS',
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

    #runSome()#only run some

    runOne('testClientTLS')

