# -*- coding: utf-8 -*-
"""
Unittests for tcping module
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
import socket
import errno

from ioflo.aid.sixing import *
from ioflo.aid.consoling import getConsole
from ioflo.aio import wiring
from ioflo.aio.tcp import serving, clienting
from ioflo.base import storing

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
        tempdirpath = os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(
                                os.path.abspath(
                                    sys.modules.get(__name__).__file__))))
        self.certdirpath = os.path.join(tempdirpath, 'test', 'tls', 'certs')

    def tearDown(self):
        """

        """
        pass


    def testTcpClientServer(self):
        """
        Test Classes Client (Outgoer) and Server with Incomers
        """
        console.terse("{0}\n".format(self.testTcpClientServer.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="tcp", dir=userDirpath)

        logDirpath = os.path.join(tempDirpath, 'log')
        if not os.path.exists(logDirpath):
            os.makedirs(logDirpath)

        wireLog = wiring.WireLog(path=logDirpath)
        result = wireLog.reopen(prefix='alpha', midfix='6101')

        store = storing.Store(stamp=0.0)

        alpha = serving.Server(port = 6101, bufsize=131072, wlog=wireLog, store=store)
        self.assertIs(alpha.opened, False)
        self.assertIs(alpha.reopen(), True)
        self.assertIs(alpha.opened, True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))

        beta = clienting.Client(ha=alpha.eha, bufsize=131072, store=store)
        self.assertIs(beta.opened, False)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.opened, True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        gamma = clienting.Client(ha=alpha.eha, bufsize=131072, store=store)
        self.assertIs(gamma.reopen(), True)
        self.assertIs(gamma.accepted, False)
        self.assertIs(gamma.connected, False)
        self.assertIs(gamma.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and beta.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.accepted, True)
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
            alpha.serviceConnects()
            if gamma.connected and gamma.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(gamma.accepted, True)
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
        if 'linux' in sys.platform:
            self.assertEqual(msgIn, b'')  # alpha shutdown detected
            self.assertIs(gamma.cutoff, True)
        else:
            self.assertEqual(msgIn, None)  # alpha shutdown not detected
            self.assertIs(gamma.cutoff, False)
        time.sleep(0.05)
        msgIn = gamma.receive()
        if 'linux' in sys.platform:
            self.assertEqual(msgIn, b'')  # alpha shutdown detected
            self.assertIs(gamma.cutoff, True)
        else:
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
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and beta.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.accepted, True)
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
        if 'linux' in sys.platform:
            self.assertEqual(msgIn, b'')  # alpha does detect shutdown
        else:
            self.assertEqual(msgIn, None)  # alpha does not detect shutdown
        beta.close()
        time.sleep(0.05)
        msgIn = ixBeta.receive()
        self.assertEqual(msgIn, b'')  # alpha detects closed socket

        ixBeta.close()
        del alpha.ixes[ixBeta.ca]

        # reopen gamma
        self.assertIs(gamma.reopen(), True)
        self.assertIs(gamma.accepted, False)
        self.assertIs(gamma.connected, False)
        self.assertIs(gamma.cutoff, False)

        console.terse("Connecting gamma to alpha\n")
        while True:
            gamma.serviceConnect()
            alpha.serviceConnects()
            if gamma.connected and gamma.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(gamma.accepted, True)
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
        self.assertIs(gamma.accepted, False)
        self.assertIs(gamma.connected, False)
        self.assertIs(gamma.cutoff, False)

        console.terse("Connecting gamma to alpha\n")
        while True:
            gamma.serviceConnect()
            alpha.serviceConnects()
            if gamma.connected and gamma.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(gamma.accepted, True)
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

        self.assertIs(alpha.opened, False)
        self.assertIs(beta.opened, False)

        wireLog.close()
        shutil.rmtree(tempDirpath)
        console.reinit(verbosity=console.Wordage.concise)

    def testTcpClientServerServiceCat(self):
        """
        Test Classes ServerSocketTcpNb service methods that use catRxes

        """
        console.terse("{0}\n".format(self.testTcpClientServerServiceCat.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="tcp", dir=userDirpath)

        logDirpath = os.path.join(tempDirpath, 'log')
        if not os.path.exists(logDirpath):
            os.makedirs(logDirpath)

        wireLogAlpha = wiring.WireLog(path=logDirpath, same=True)
        result = wireLogAlpha.reopen(prefix='alpha', midfix='6101')

        wireLogBeta = wiring.WireLog(buffify=True)
        result = wireLogBeta.reopen()

        store = storing.Store(stamp=0.0)

        alpha = serving.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha, store=store)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))

        beta = clienting.Client(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta, store=store)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and beta.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.accepted, True)
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
        beta.tx(msgOut)
        msgIn = b''
        while not msgIn and beta.txes:
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            msgIn += ixBeta.catRxbs()
            time.sleep(0.05)
        self.assertEqual(msgOut, msgIn)

        # send multiple
        msgOut1 = b"First Message"
        beta.tx(msgOut1)
        msgOut2 = b"Second Message"
        beta.tx(msgOut2)
        msgIn = b''
        while len(msgIn) < len(msgOut1 + msgOut2):
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            msgIn += ixBeta.catRxbs()
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

        beta.tx(msgOutBig)
        msgIn = b''
        count = 0
        while len(msgIn) < len(msgOutBig):
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            msgIn += ixBeta.catRxbs()
            time.sleep(0.05)

        self.assertEqual(msgIn, msgOutBig)

        # send from alpha to beta
        msgOut = b"Alpha sends to Beta"
        ixBeta.tx(msgOut)
        msgIn = b''
        while len(msgIn) < len(msgOut):
            alpha.serviceTxesAllIx()
            beta.serviceReceives()
            msgIn += beta.catRxbs()
            time.sleep(0.05)

        self.assertEqual(msgIn, msgOut)

        # send big from alpha to beta
        ixBeta.tx(msgOutBig)
        msgIn = b''
        while len(msgIn) < len(msgOutBig):
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
            msgIn += beta.catRxbs()
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

    def testTcpClientServerService(self):
        """
        Test Classes ServerSocketTcpNb service methods
        """
        console.terse("{0}\n".format(self.testTcpClientServerService.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="tcp", dir=userDirpath)

        logDirpath = os.path.join(tempDirpath, 'log')
        if not os.path.exists(logDirpath):
            os.makedirs(logDirpath)

        wireLogAlpha = wiring.WireLog(path=logDirpath, same=True)
        result = wireLogAlpha.reopen(prefix='alpha', midfix='6101')

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        alpha = serving.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        beta = clienting.Client(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and beta.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.accepted, True)
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
        beta.tx(msgOut)
        while not ixBeta.rxbs and beta.txes:
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        index = len(ixBeta.rxbs)

        # send multiple
        msgOut1 = b"First Message"
        beta.tx(msgOut1)
        msgOut2 = b"Second Message"
        beta.tx(msgOut2)
        while len(ixBeta.rxbs) < len(msgOut1 + msgOut2):
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
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

        beta.tx(msgOutBig)
        count = 0
        while len(ixBeta.rxbs) < len(msgOutBig):
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        ixBeta.clearRxbs()
        self.assertEqual(msgIn, msgOutBig)

        # send from alpha to beta
        msgOut = b"Alpha sends to Beta"
        ixBeta.tx(msgOut)
        while len(beta.rxbs) < len(msgOut):
            alpha.serviceTxesAllIx()
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        beta.clearRxbs()
        self.assertEqual(msgIn, msgOut)

        # send big from alpha to beta
        ixBeta.tx(msgOutBig)
        while len(beta.rxbs) < len(msgOutBig):
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
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

    def testClientAutoReconnect(self):
        """
        Test Classes Client/Outgoer reconnectable
        """
        console.terse("{0}\n".format(self.testClientAutoReconnect.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        store = storing.Store(stamp=0.0)

        beta = clienting.Client(ha=('127.0.0.1', 6101),
                                   bufsize=131072,
                                   wlog=wireLogBeta,
                                   store=store,
                                   timeout=0.2,
                                   reconnectable=True, )
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)
        self.assertIs(beta.store, store)
        self.assertIs(beta.reconnectable, True)

        console.terse("Connecting beta to alpha when alpha not up\n")
        while beta.store.stamp <= 0.25:
            beta.serviceConnect()
            if beta.connected and beta.ca in alpha.ixes:
                break
            beta.store.advanceStamp(0.05)
            time.sleep(0.05)

        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)

        alpha = serving.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha, store=store)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))


        console.terse("Connecting beta to alpha when alpha up\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and beta.ca in alpha.ixes:
                break
            beta.store.advanceStamp(0.05)
            time.sleep(0.05)

        self.assertIs(beta.accepted, True)
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
        beta.tx(msgOut)
        while not ixBeta.rxbs and beta.txes:
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        index = len(ixBeta.rxbs)

        alpha.close()
        beta.close()

        wlBetaRx = wireLogBeta.getRx()
        wlBetaTx = wireLogBeta.getTx()
        self.assertEqual(wlBetaRx, wlBetaTx)  # since wlog is same

        wireLogAlpha.close()
        wireLogBeta.close()

        console.reinit(verbosity=console.Wordage.concise)

    def testTLSConnectionDefault(self):
        """
        Test TLS connection with default settings
        """
        try:
            import ssl
        except ImportError:
            return

        console.terse("{0}\n".format(self.testTLSConnectionDefault.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        #serverKeypath = '/etc/pki/tls/certs/server_key.pem'  # local server private key
        #serverCertpath = '/etc/pki/tls/certs/server_cert.pem'  # local server public cert
        #clientCafilepath = '/etc/pki/tls/certs/client.pem' # remote client public cert

        #clientKeypath = '/etc/pki/tls/certs/client_key.pem'  # local client private key
        #clientCertpath = '/etc/pki/tls/certs/client_cert.pem'  # local client public cert
        #serverCafilepath = '/etc/pki/tls/certs/server.pem' # remote server public cert

        serverKeypath = self.certdirpath + '/server_key.pem'  # local server private key
        serverCertpath = self.certdirpath + '/server_cert.pem'  # local server public cert
        clientCafilepath = self.certdirpath + '/client.pem' # remote client public cert

        clientKeypath = self.certdirpath + '/client_key.pem'  # local client private key
        clientCertpath = self.certdirpath + '/client_cert.pem'  # local client public cert
        serverCafilepath = self.certdirpath + '/server.pem' # remote server public cert

        alpha = serving.ServerTls(host='localhost',
                                      port = 6101,
                                      bufsize=131072,
                                      wlog=wireLogAlpha,
                                      context=None,
                                      version=None,
                                      certify=None,
                                      keypath=serverKeypath,
                                      certpath=serverCertpath,
                                      cafilepath=clientCafilepath,
                                      )
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('127.0.0.1', 6101))

        serverCertCommonName = 'localhost' # match hostname uses servers's cert commonname

        beta = clienting.ClientTls(ha=alpha.ha,
                                      bufsize=131072,
                                      wlog=wireLogBeta,
                                      context=None,
                                      version=None,
                                      certify=None,
                                      hostify=None,
                                      certedhost=serverCertCommonName,
                                      keypath=clientKeypath,
                                      certpath=clientCertpath,
                                      cafilepath=serverCafilepath,
                                      )
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting  and Handshaking beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and len(alpha.ixes) >= 1:
                break
            time.sleep(0.01)

        self.assertIs(beta.accepted, True)
        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertIs(beta.connected, True)

        ixBeta = alpha.ixes[beta.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)
        self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.ca)
        self.assertEqual(ixBeta.ha, beta.ha)

        msgOut = b"Beta sends to Alpha\n"
        beta.tx(msgOut)
        while True:
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            time.sleep(0.01)
            if not beta.txes and ixBeta.rxbs:
                break

        time.sleep(0.05)
        alpha.serviceReceivesAllIx()

        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(ixBeta.rxbs)
        ixBeta.clearRxbs()

        msgOut = b'Alpha sends to Beta\n'
        ixBeta.tx(msgOut)
        while True:
            alpha.serviceTxesAllIx()
            beta.serviceReceives()
            time.sleep(0.01)
            if not ixBeta.txes and beta.rxbs:
                break

        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(beta.rxbs)
        beta.clearRxbs()

        alpha.close()
        beta.close()

        self.assertEqual(wireLogAlpha.getRx(), wireLogAlpha.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogAlpha.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogAlpha.getRx())

        self.assertEqual(wireLogBeta.getRx(), wireLogBeta.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogBeta.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogBeta.getRx())

        wireLogAlpha.close()
        wireLogBeta.close()
        console.reinit(verbosity=console.Wordage.concise)

    def testTLSConnectionVerifyNeither(self):
        """
        Test TLS client server connection with neither verify certs
        """
        try:
            import ssl
        except ImportError:
            return

        console.terse("{0}\n".format(self.testTLSConnectionVerifyNeither.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        #serverKeypath = '/etc/pki/tls/certs/server_key.pem'  # local server private key
        #serverCertpath = '/etc/pki/tls/certs/server_cert.pem'  # local server public cert
        #clientCafilepath = '/etc/pki/tls/certs/client.pem' # remote client public cert

        #clientKeypath = '/etc/pki/tls/certs/client_key.pem'  # local client private key
        #clientCertpath = '/etc/pki/tls/certs/client_cert.pem'  # local client public cert
        #serverCafilepath = '/etc/pki/tls/certs/server.pem' # remote server public cert

        serverKeypath = self.certdirpath + '/server_key.pem'  # local server private key
        serverCertpath = self.certdirpath + '/server_cert.pem'  # local server public cert
        clientCafilepath = self.certdirpath + '/client.pem' # remote client public cert

        clientKeypath = self.certdirpath + '/client_key.pem'  # local client private key
        clientCertpath = self.certdirpath + '/client_cert.pem'  # local client public cert
        serverCafilepath = self.certdirpath + '/server.pem' # remote server public cert

        alpha = serving.ServerTls(host='localhost',
                                      port = 6101,
                                      bufsize=131072,
                                      wlog=wireLogAlpha,
                                      context=None,
                                      version=None,
                                      certify=ssl.CERT_NONE,
                                      keypath=serverKeypath,
                                      certpath=serverCertpath,
                                      cafilepath=clientCafilepath,
                                      )
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('127.0.0.1', 6101))

        serverCertCommonName = 'localhost' # match hostname uses servers's cert commonname

        beta = clienting.ClientTls(ha=alpha.ha,
                                      bufsize=131072,
                                      wlog=wireLogBeta,
                                      context=None,
                                      version=None,
                                      certify=ssl.CERT_NONE,
                                      hostify=False,
                                      certedhost=serverCertCommonName,
                                      keypath=clientKeypath,
                                      certpath=clientCertpath,
                                      cafilepath=serverCafilepath,
                                      )
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting  and Handshaking beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and len(alpha.ixes) >= 1:
                break
            time.sleep(0.01)

        self.assertIs(beta.accepted, True)
        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertIs(beta.connected, True)

        ixBeta = alpha.ixes[beta.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)

        self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.ca)
        self.assertEqual(ixBeta.ha, beta.ha)

        msgOut = b"Beta sends to Alpha\n"
        beta.tx(msgOut)
        while True:
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            time.sleep(0.01)
            if not beta.txes and ixBeta.rxbs:
                break

        time.sleep(0.05)
        alpha.serviceReceivesAllIx()

        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(ixBeta.rxbs)
        ixBeta.clearRxbs()

        msgOut = b'Alpha sends to Beta\n'
        ixBeta.tx(msgOut)
        while True:
            alpha.serviceTxesAllIx()
            beta.serviceReceives()
            time.sleep(0.01)
            if not ixBeta.txes and beta.rxbs:
                break

        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(beta.rxbs)
        beta.clearRxbs()

        alpha.close()
        beta.close()

        self.assertEqual(wireLogAlpha.getRx(), wireLogAlpha.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogAlpha.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogAlpha.getRx())

        self.assertEqual(wireLogBeta.getRx(), wireLogBeta.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogBeta.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogBeta.getRx())

        wireLogAlpha.close()
        wireLogBeta.close()
        console.reinit(verbosity=console.Wordage.concise)

    def testTLSConnectionClientVerifyServerCert(self):
        """
        Test TLS client server connection with neither verify certs
        """
        try:
            import ssl
        except ImportError:
            return

        console.terse("{0}\n".format(self.testTLSConnectionClientVerifyServerCert.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        serverKeypath = os.path.join(self.certdirpath, 'server_key.pem')  # local server private key
        serverCertpath = os.path.join(self.certdirpath, 'server_cert.pem')  # local server public cert
        clientCafilepath = os.path.join(self.certdirpath, 'client.pem') # remote client public cert

        clientKeypath = os.path.join(self.certdirpath, 'client_key.pem')  # local client private key
        clientCertpath = os.path.join(self.certdirpath, 'client_cert.pem')  # local client public cert
        serverCafilepath = os.path.join(self.certdirpath, 'server.pem') # remote server public cert

        alpha = serving.ServerTls(host='localhost',
                                      port = 6101,
                                      bufsize=131072,
                                      wlog=wireLogAlpha,
                                      context=None,
                                      version=None,
                                      certify=ssl.CERT_NONE,
                                      keypath=serverKeypath,
                                      certpath=serverCertpath,
                                      cafilepath=clientCafilepath,
                                      )
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('127.0.0.1', 6101))

        serverCertCommonName = 'localhost' # match hostname uses servers's cert commonname

        beta = clienting.ClientTls(ha=alpha.ha,
                                      bufsize=131072,
                                      wlog=wireLogBeta,
                                      context=None,
                                      version=None,
                                      certify=ssl.CERT_REQUIRED,
                                      hostify=True,
                                      certedhost=serverCertCommonName,
                                      keypath=clientKeypath,
                                      certpath=clientCertpath,
                                      cafilepath=serverCafilepath,
                                      )
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting  and Handshaking beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and len(alpha.ixes) >= 1:
                break
            time.sleep(0.01)

        self.assertIs(beta.accepted, True)
        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertIs(beta.connected, True)

        ixBeta = alpha.ixes[beta.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)

        self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.ca)
        self.assertEqual(ixBeta.ha, beta.ha)

        msgOut = b"Beta sends to Alpha\n"
        beta.tx(msgOut)
        while True:
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            time.sleep(0.01)
            if not beta.txes and ixBeta.rxbs:
                break

        time.sleep(0.05)
        alpha.serviceReceivesAllIx()

        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(ixBeta.rxbs)
        ixBeta.clearRxbs()

        msgOut = b'Alpha sends to Beta\n'
        ixBeta.tx(msgOut)
        while True:
            alpha.serviceTxesAllIx()
            beta.serviceReceives()
            time.sleep(0.01)
            if not ixBeta.txes and beta.rxbs:
                break

        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(beta.rxbs)
        beta.clearRxbs()

        alpha.close()
        beta.close()

        self.assertEqual(wireLogAlpha.getRx(), wireLogAlpha.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogAlpha.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogAlpha.getRx())

        self.assertEqual(wireLogBeta.getRx(), wireLogBeta.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogBeta.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogBeta.getRx())

        wireLogAlpha.close()
        wireLogBeta.close()
        console.reinit(verbosity=console.Wordage.concise)

    def testTLSConnectionServerVerifyClientCert(self):
        """
        Test TLS client server connection with neither verify certs
        """
        try:
            import ssl
        except ImportError:
            return

        console.terse("{0}\n".format(self.testTLSConnectionServerVerifyClientCert.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        serverKeypath = os.path.join(self.certdirpath, 'server_key.pem')  # local server private key
        serverCertpath = os.path.join(self.certdirpath, 'server_cert.pem')  # local server public cert
        clientCafilepath = os.path.join(self.certdirpath, 'client.pem') # remote client public cert

        clientKeypath = os.path.join(self.certdirpath, 'client_key.pem')  # local client private key
        clientCertpath = os.path.join(self.certdirpath, 'client_cert.pem')  # local client public cert
        serverCafilepath = os.path.join(self.certdirpath, 'server.pem') # remote server public cert

        alpha = serving.ServerTls(host='localhost',
                                      port = 6101,
                                      bufsize=131072,
                                      wlog=wireLogAlpha,
                                      context=None,
                                      version=None,
                                      certify=ssl.CERT_REQUIRED,
                                      keypath=serverKeypath,
                                      certpath=serverCertpath,
                                      cafilepath=clientCafilepath,
                                      )
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('127.0.0.1', 6101))

        serverCertCommonName = 'localhost' # match hostname uses servers's cert commonname

        beta = clienting.ClientTls(ha=alpha.ha,
                                      bufsize=131072,
                                      wlog=wireLogBeta,
                                      context=None,
                                      version=None,
                                      certify=ssl.CERT_NONE,
                                      hostify=False,
                                      certedhost=serverCertCommonName,
                                      keypath=clientKeypath,
                                      certpath=clientCertpath,
                                      cafilepath=serverCafilepath,
                                      )
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting  and Handshaking beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and len(alpha.ixes) >= 1:
                break
            time.sleep(0.01)

        self.assertIs(beta.accepted, True)
        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertIs(beta.connected, True)

        ixBeta = alpha.ixes[beta.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)

        self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.ca)
        self.assertEqual(ixBeta.ha, beta.ha)

        msgOut = b"Beta sends to Alpha\n"
        beta.tx(msgOut)
        while True:
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            time.sleep(0.01)
            if not beta.txes and ixBeta.rxbs:
                break

        time.sleep(0.05)
        alpha.serviceReceivesAllIx()

        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(ixBeta.rxbs)
        ixBeta.clearRxbs()

        msgOut = b'Alpha sends to Beta\n'
        ixBeta.tx(msgOut)
        while True:
            alpha.serviceTxesAllIx()
            beta.serviceReceives()
            time.sleep(0.01)
            if not ixBeta.txes and beta.rxbs:
                break

        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(beta.rxbs)
        beta.clearRxbs()

        alpha.close()
        beta.close()

        self.assertEqual(wireLogAlpha.getRx(), wireLogAlpha.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogAlpha.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogAlpha.getRx())

        self.assertEqual(wireLogBeta.getRx(), wireLogBeta.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogBeta.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogBeta.getRx())

        wireLogAlpha.close()
        wireLogBeta.close()
        console.reinit(verbosity=console.Wordage.concise)

    def testTLSConnectionVerifyBoth(self):
        """
        Test TLS client server connection with neither verify certs
        """
        try:
            import ssl
        except ImportError:
            return

        console.terse("{0}\n".format(self.testTLSConnectionVerifyBoth.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        serverKeypath = os.path.join(self.certdirpath, 'server_key.pem')  # local server private key
        serverCertpath = os.path.join(self.certdirpath, 'server_cert.pem')  # local server public cert
        clientCafilepath = os.path.join(self.certdirpath, 'client.pem') # remote client public cert

        clientKeypath = os.path.join(self.certdirpath, 'client_key.pem')  # local client private key
        clientCertpath = os.path.join(self.certdirpath, 'client_cert.pem')  # local client public cert
        serverCafilepath = os.path.join(self.certdirpath, 'server.pem') # remote server public cert

        alpha = serving.ServerTls(host='localhost',
                                      port = 6101,
                                      bufsize=131072,
                                      wlog=wireLogAlpha,
                                      context=None,
                                      version=None,
                                      certify=ssl.CERT_REQUIRED,
                                      keypath=serverKeypath,
                                      certpath=serverCertpath,
                                      cafilepath=clientCafilepath,
                                      )
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('127.0.0.1', 6101))

        serverCertCommonName = 'localhost' # match hostname uses servers's cert commonname

        beta = clienting.ClientTls(ha=alpha.ha,
                                      bufsize=131072,
                                      wlog=wireLogBeta,
                                      context=None,
                                      version=None,
                                      certify=ssl.CERT_REQUIRED,
                                      hostify=True,
                                      certedhost=serverCertCommonName,
                                      keypath=clientKeypath,
                                      certpath=clientCertpath,
                                      cafilepath=serverCafilepath,
                                      )
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting  and Handshaking beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and len(alpha.ixes) >= 1:
                break
            time.sleep(0.01)

        self.assertIs(beta.accepted, True)
        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertIs(beta.connected, True)

        ixBeta = alpha.ixes[beta.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)

        self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.ca)
        self.assertEqual(ixBeta.ha, beta.ha)

        msgOut = b"Beta sends to Alpha\n"
        beta.tx(msgOut)
        while True:
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            time.sleep(0.01)
            if not beta.txes and ixBeta.rxbs:
                break

        time.sleep(0.05)
        alpha.serviceReceivesAllIx()

        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(ixBeta.rxbs)
        ixBeta.clearRxbs()

        msgOut = b'Alpha sends to Beta\n'
        ixBeta.tx(msgOut)
        while True:
            alpha.serviceTxesAllIx()
            beta.serviceReceives()
            time.sleep(0.01)
            if not ixBeta.txes and beta.rxbs:
                break

        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(beta.rxbs)
        beta.clearRxbs()

        alpha.close()
        beta.close()

        self.assertEqual(wireLogAlpha.getRx(), wireLogAlpha.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogAlpha.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogAlpha.getRx())

        self.assertEqual(wireLogBeta.getRx(), wireLogBeta.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogBeta.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogBeta.getRx())

        wireLogAlpha.close()
        wireLogBeta.close()
        console.reinit(verbosity=console.Wordage.concise)

    def testTLSConnectionVerifyBothTLSv1(self):
        """
        Test TLS client server connection with neither verify certs
        """
        try:
            import ssl
        except ImportError:
            return

        console.terse("{0}\n".format(self.testTLSConnectionVerifyBothTLSv1.__doc__))
        console.reinit(verbosity=console.Wordage.profuse)

        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        serverKeypath = os.path.join(self.certdirpath, 'server_key.pem')  # local server private key
        serverCertpath = os.path.join(self.certdirpath, 'server_cert.pem')  # local server public cert
        clientCafilepath = os.path.join(self.certdirpath, 'client.pem') # remote client public cert

        clientKeypath = os.path.join(self.certdirpath, 'client_key.pem')  # local client private key
        clientCertpath = os.path.join(self.certdirpath, 'client_cert.pem')  # local client public cert
        serverCafilepath = os.path.join(self.certdirpath, 'server.pem') # remote server public cert

        alpha = serving.ServerTls(host='localhost',
                                      port = 6101,
                                      bufsize=131072,
                                      wlog=wireLogAlpha,
                                      context=None,
                                      version=ssl.PROTOCOL_TLSv1,
                                      certify=ssl.CERT_REQUIRED,
                                      keypath=serverKeypath,
                                      certpath=serverCertpath,
                                      cafilepath=clientCafilepath,
                                      )
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('127.0.0.1', 6101))

        serverCertCommonName = 'localhost' # match hostname uses servers's cert commonname

        beta = clienting.ClientTls(ha=alpha.ha,
                                      bufsize=131072,
                                      wlog=wireLogBeta,
                                      context=None,
                                      version=ssl.PROTOCOL_TLSv1,
                                      certify=ssl.CERT_REQUIRED,
                                      hostify=True,
                                      certedhost=serverCertCommonName,
                                      keypath=clientKeypath,
                                      certpath=clientCertpath,
                                      cafilepath=serverCafilepath,
                                      )
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting and Handshaking beta to alpha\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.connected and len(alpha.ixes) >= 1:
                break
            time.sleep(0.01)

        self.assertIs(beta.accepted, True)
        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertIs(beta.connected, True)

        ixBeta = alpha.ixes[beta.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)

        self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.ca)
        self.assertEqual(ixBeta.ha, beta.ha)

        msgOut = b"Beta sends to Alpha\n"
        beta.tx(msgOut)
        while True:
            beta.serviceTxes()
            alpha.serviceReceivesAllIx()
            time.sleep(0.01)
            if not beta.txes and ixBeta.rxbs:
                break

        time.sleep(0.05)
        alpha.serviceReceivesAllIx()

        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(ixBeta.rxbs)
        ixBeta.clearRxbs()

        msgOut = b'Alpha sends to Beta\n'
        ixBeta.tx(msgOut)
        while True:
            alpha.serviceTxesAllIx()
            beta.serviceReceives()
            time.sleep(0.01)
            if not ixBeta.txes and beta.rxbs:
                break

        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)
        #index = len(beta.rxbs)
        beta.clearRxbs()

        alpha.close()
        beta.close()

        self.assertEqual(wireLogAlpha.getRx(), wireLogAlpha.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogAlpha.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogAlpha.getRx())

        self.assertEqual(wireLogBeta.getRx(), wireLogBeta.getTx())  # since wlog is same
        self.assertTrue(b"Beta sends to Alpha\n" in wireLogBeta.getRx())
        self.assertTrue(b"Alpha sends to Beta\n" in wireLogBeta.getRx())

        wireLogAlpha.close()
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
    names = [
             'testTcpClientServer',
             'testTcpClientServerServiceCat',
             'testTcpClientServerService',
             'testClientAutoReconnect',
             'testTLSConnectionDefault',
             'testTLSConnectionVerifyNeither',
             'testTLSConnectionClientVerifyServerCert',
             'testTLSConnectionServerVerifyClientCert',
             'testTLSConnectionVerifyBoth',
             'testTLSConnectionVerifyBothTLSv1',
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


