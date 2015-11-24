# -*- coding: utf-8 -*-
"""
Unittests for http clienting module
"""

import sys
if sys.version > '3':
    xrange = range
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version > '3':
    from urllib.parse import urlsplit, quote, quote_plus, unquote, unquote_plus
else:
    from urlparse import urlsplit
    from urllib import quote, quote_plus, unquote, unquote_plus

import os
import time
import tempfile
import shutil
import socket
import errno

try:
    import simplejson as json
except ImportError:
    import json

# Import ioflo libs
from ioflo.aid.sixing import *
from ioflo.aid.timing import Timer, StoreTimer
from ioflo.aid.odicting import odict
from ioflo.aid.consoling import getConsole
from ioflo.base import storing

from ioflo.aio import wiring, tcp
from ioflo.aio.http import httping, clienting, serving

console = getConsole()


def setUpModule():
    pass

def tearDownModule():
    pass


class BasicTestCase(unittest.TestCase):
    """
    Test Case
    """

    def setUp(self):
        """

        """
        console.reinit(verbosity=console.Wordage.profuse)

    def tearDown(self):
        """

        """
        console.reinit(verbosity=console.Wordage.concise)

    def testNonBlockingRequestEcho(self):
        """
        Test NonBlocking Http client
        """
        console.terse("{0}\n".format(self.testNonBlockingRequestEcho.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        beta = tcp.Client(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to server ...\n")
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

        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 6101
        method = u'GET'
        path = u'/echo?name=fame'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))
        headers = odict([(u'Accept', u'application/json')])
        request =  clienting.Requester(hostname=host,
                                     port=port,
                                     method=method,
                                     path=path,
                                     headers=headers)
        msgOut = request.build()
        lines = [
                   b'GET /echo?name=fame HTTP/1.1',
                   b'Host: 127.0.0.1:6101',
                   b'Accept-Encoding: identity',
                   b'Accept: application/json',
                   b'',
                   b'',
                ]
        for i, line in enumerate(lines):
            self.assertEqual(line, request.lines[i])

        self.assertEqual(request.head, b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')

        console.terse("Beta requests to Alpha\n")
        beta.tx(msgOut)
        while beta.txes and not ixBeta.rxbs :
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.rxbs:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)

        console.terse("Beta processes response \n")
        response = clienting.Respondent(msg=beta.rxbs, method=method)
        while response.parser:
            response.parse()

        response.dictify()

        #self.assertEqual(bytes(response.body), b'{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}')
        self.assertEqual(bytes(response.body), b'')
        self.assertEqual(response.data, {'action': None,
                                         'content': None,
                                         'query': {'name': 'fame'},
                                         'url': 'http://127.0.0.1:8080/echo?name=fame',
                                         'verb': 'GET'})
        self.assertEqual(len(beta.rxbs), 0)
        self.assertEqual(response.headers.items(), [('content-length', '122'),
                                                    ('content-type', 'application/json'),
                                                    ('date', 'Thu, 30 Apr 2015 19:37:17 GMT'),
                                                    ('server', 'IoBook.local')])

        alpha.close()
        beta.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def testNonBlockingRequestStream(self):
        """
        Test NonBlocking Http client with SSE streaming server
        """
        console.terse("{0}\n".format(self.testNonBlockingRequestStream.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True, same=True)
        result = wireLogBeta.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        beta = tcp.Client(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to server ...\n")
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

        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 6061
        method = u'GET'
        path = u'/stream'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))
        headers = odict([(u'Accept', u'application/json')])
        request =  clienting.Requester(hostname=host,
                                     port=port,
                                     method=method,
                                     path=path,
                                     headers=headers)
        msgOut = request.build()
        lines = [
                   b'GET /stream HTTP/1.1',
                   b'Host: 127.0.0.1:6061',
                   b'Accept-Encoding: identity',
                   b'Accept: application/json',
                   b'',
                   b'',
                ]
        for i, line in enumerate(lines):
            self.assertEqual(line, request.lines[i])

        self.assertEqual(request.head, b'GET /stream HTTP/1.1\r\nHost: 127.0.0.1:6061\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, request.head)

        console.terse("Beta requests to Alpha\n")
        beta.tx(msgOut)
        while beta.txes and not ixBeta.rxbs :
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        lines = [
                        b'HTTP/1.0 200 OK\r\n',
                        b'Server: PasteWSGIServer/0.5 Python/2.7.9\r\n',
                        b'Date: Thu, 30 Apr 2015 21:35:25 GMT\r\n'
                        b'Content-Type: text/event-stream\r\n',
                        b'Cache-Control: no-cache\r\n',
                        b'Connection: close\r\n\r\n',
                    ]

        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.rxbs:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)

        console.terse("Beta processes response \n")
        response = clienting.Respondent(msg=beta.rxbs, method=method)

        lines =  [
                    b'retry: 1000\n\n',
                    b'data: START\n\n',
                    b'data: 1\n\n',
                    b'data: 2\n\n',
                    b'data: 3\n\n',
                    b'data: 4\n\n',
                 ]
        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        timer = Timer(duration=0.5)
        while response.parser and not timer.expired:
            alpha.serviceTxesAllIx()
            response.parse()
            beta.serviceReceives()
            time.sleep(0.01)

        if response.parser:
            response.parser.close()
            response.parser = None

        response.dictify()

        self.assertEqual(len(beta.rxbs), 0)
        self.assertEqual(response.eventSource.retry, 1000)
        self.assertEqual(response.retry, response.eventSource.retry)
        self.assertEqual(response.eventSource.leid, None)
        self.assertEqual(response.leid, response.eventSource.leid)
        self.assertTrue(len(response.events) > 2)
        event = response.events.popleft()
        self.assertEqual(event, {'id': None, 'name': '', 'data': 'START'})
        event = response.events.popleft()
        self.assertEqual(event, {'id': None, 'name': '', 'data': '1'})
        event = response.events.popleft()
        self.assertEqual(event, {'id': None, 'name': '', 'data': '2'})
        self.assertTrue(len(response.body) == 0)
        self.assertTrue(len(response.eventSource.raw) == 0)

        alpha.close()
        beta.close()
        wireLogAlpha.close()
        wireLogBeta.close()


    def testNonBlockingRequestStreamChunked(self):
        """
        Test NonBlocking Http client with SSE streaming server with transfer encoding (chunked)
        """
        console.terse("{0}\n".format(self.testNonBlockingRequestStreamChunked.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True, same=True)
        result = wireLogBeta.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        beta = tcp.Client(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to server ...\n")
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

        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 6061
        method = u'GET'
        path = u'/stream'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))
        headers = odict([(u'Accept', u'application/json')])
        request =  clienting.Requester(hostname=host,
                                     port=port,
                                     method=method,
                                     path=path,
                                     headers=headers)
        msgOut = request.build()
        lines = [
                   b'GET /stream HTTP/1.1',
                   b'Host: 127.0.0.1:6061',
                   b'Accept-Encoding: identity',
                   b'Accept: application/json',
                   b'',
                   b'',
                ]
        for i, line in enumerate(lines):
            self.assertEqual(line, request.lines[i])

        self.assertEqual(request.head, b'GET /stream HTTP/1.1\r\nHost: 127.0.0.1:6061\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, request.head)

        console.terse("Beta requests to Alpha\n")
        beta.tx(msgOut)
        while beta.txes and not ixBeta.rxbs :
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        lines = [
                        b'HTTP/1.1 200 OK\r\n',
                        b'Content-Type: text/event-stream\r\n',
                        b'Cache-Control: no-cache\r\n',
                        b'Transfer-Encoding: chunked\r\n',
                        b'Date: Thu, 30 Apr 2015 20:11:35 GMT\r\n',
                        b'Server: IoBook.local\r\n\r\n',
                    ]

        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.rxbs:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)

        console.terse("Beta processes response \n")
        response = clienting.Respondent(msg=beta.rxbs, method=method)

        lines =  [
                    b'd\r\nretry: 1000\n\n\r\n',
                    b'd\r\ndata: START\n\n\r\n',
                    b'9\r\ndata: 1\n\n\r\n',
                    b'9\r\ndata: 2\n\n\r\n',
                    b'9\r\ndata: 3\n\n\r\n',
                    b'9\r\ndata: 4\n\n\r\n',
                 ]
        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        timer = Timer(duration=0.5)
        while response.parser and not timer.expired:
            alpha.serviceTxesAllIx()
            response.parse()
            beta.serviceReceives()
            time.sleep(0.01)

        if response.parser:
            response.parser.close()
            response.parser = None

        response.dictify()

        self.assertEqual(len(beta.rxbs), 0)
        self.assertEqual(response.eventSource.retry, 1000)
        self.assertEqual(response.retry, response.eventSource.retry)
        self.assertEqual(response.eventSource.leid, None)
        self.assertEqual(response.leid, response.eventSource.leid)
        self.assertTrue(len(response.events) > 2)
        event = response.events.popleft()
        self.assertEqual(event, {'id': None, 'name': '', 'data': 'START'})
        event = response.events.popleft()
        self.assertEqual(event, {'id': None, 'name': '', 'data': '1'})
        event = response.events.popleft()
        self.assertEqual(event, {'id': None, 'name': '', 'data': '2'})
        self.assertTrue(len(response.body) == 0)
        self.assertTrue(len(response.eventSource.raw) == 0)

        alpha.close()
        beta.close()
        wireLogAlpha.close()
        wireLogBeta.close()


    def testNonBlockingRequestStreamFancy(self):
        """
        Test NonBlocking Http client to SSE server
        """
        console.terse("{0}\n".format(self.testNonBlockingRequestStreamFancy.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True, same=True)
        result = wireLogBeta.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        beta = tcp.Client(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to server ...\n")
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

        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 6061
        method = u'GET'
        path = u'/fancy?idify=true&multiply=true'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))
        headers = odict([(u'Accept', u'application/json')])
        request =  clienting.Requester(hostname=host,
                                     port=port,
                                     method=method,
                                     path=path,
                                     headers=headers)
        msgOut = request.build()
        lines = [
                   b'GET /fancy?idify=true&multiply=true HTTP/1.1',
                   b'Host: 127.0.0.1:6061',
                   b'Accept-Encoding: identity',
                   b'Accept: application/json',
                   b'',
                   b'',
                ]
        for i, line in enumerate(lines):
            self.assertEqual(line, request.lines[i])

        self.assertEqual(request.head, b'GET /fancy?idify=true&multiply=true HTTP/1.1\r\nHost: 127.0.0.1:6061\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, request.head)

        console.terse("Beta requests to Alpha\n")
        beta.tx(msgOut)
        while beta.txes and not ixBeta.rxbs :
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        lines = [
            b'HTTP/1.0 200 OK\r\n',
            b'Server: PasteWSGIServer/0.5 Python/2.7.9\r\n',
            b'Date: Thu, 30 Apr 2015 21:35:25 GMT\r\n'
            b'Content-Type: text/event-stream\r\n',
            b'Cache-Control: no-cache\r\n',
            b'Connection: close\r\n\r\n',
        ]

        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.rxbs:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)

        console.terse("Beta processes response \n")
        response = clienting.Respondent(msg=beta.rxbs, method=method)

        lines =  [
            b'retry: 1000\n\n',
            b'id: 0\ndata: START\n\n',
            b'id: 1\ndata: 1\ndata: 2\n\n',
            b'id: 2\ndata: 3\ndata: 4\n\n',
            b'id: 3\ndata: 5\ndata: 6\n\n',
            b'id: 4\ndata: 7\ndata: 8\n\n',
        ]
        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        timer = Timer(duration=0.5)
        while response.parser and not timer.expired:
            alpha.serviceTxesAllIx()
            response.parse()
            beta.serviceReceives()
            time.sleep(0.01)

        if response.parser:
            response.parser.close()
            response.parser = None

        response.dictify()

        self.assertEqual(len(beta.rxbs), 0)
        self.assertEqual(response.eventSource.retry, 1000)
        self.assertEqual(response.retry, response.eventSource.retry)
        self.assertTrue(int(response.eventSource.leid) >= 2)
        self.assertEqual(response.leid, response.eventSource.leid)
        self.assertTrue(len(response.events) > 2)
        event = response.events.popleft()
        self.assertEqual(event, {'id': '0', 'name': '', 'data': 'START'})
        event = response.events.popleft()
        self.assertEqual(event, {'id': '1', 'name': '', 'data': '1\n2'})
        event = response.events.popleft()
        self.assertEqual(event, {'id': '2', 'name': '', 'data': '3\n4'})
        self.assertTrue(len(response.body) == 0)
        self.assertTrue(len(response.eventSource.raw) == 0)

        alpha.close()
        beta.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def testNonBlockingRequestStreamFancyChunked(self):
        """
        Test NonBlocking Http client to server Fancy SSE with chunked transfer encoding
        """
        console.terse("{0}\n".format(self.testNonBlockingRequestStreamFancyChunked.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True, same=True)
        result = wireLogBeta.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        beta = tcp.Client(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to server ...\n")
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

        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 6061
        method = u'GET'
        path = u'/fancy?idify=true&multiply=true'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))
        headers = odict([(u'Accept', u'application/json')])
        request =  clienting.Requester(hostname=host,
                                     port=port,
                                     method=method,
                                     path=path,
                                     headers=headers)

        msgOut = request.build()
        lines = [
                   b'GET /fancy?idify=true&multiply=true HTTP/1.1',
                   b'Host: 127.0.0.1:6061',
                   b'Accept-Encoding: identity',
                   b'Accept: application/json',
                   b'',
                   b'',
                ]
        for i, line in enumerate(lines):
            self.assertEqual(line, request.lines[i])

        self.assertEqual(request.head, b'GET /fancy?idify=true&multiply=true HTTP/1.1\r\nHost: 127.0.0.1:6061\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, request.head)

        console.terse("Beta requests to Alpha\n")
        beta.tx(msgOut)
        while beta.txes and not ixBeta.rxbs :
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        lines = [
            b'HTTP/1.1 200 OK\r\n',
            b'Content-Type: text/event-stream\r\n',
            b'Cache-Control: no-cache\r\n',
            b'Transfer-Encoding: chunked\r\n',
            b'Date: Thu, 30 Apr 2015 22:11:53 GMT\r\n',
            b'Server: IoBook.local\r\n\r\n',
        ]

        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.rxbs:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)

        console.terse("Beta processes response \n")
        response = clienting.Respondent(msg=beta.rxbs, method=method)

        lines =  [
            b'd\r\nretry: 1000\n\n\r\n',
            b'6\r\nid: 0\n\r\n',
            b'd\r\ndata: START\n\n\r\n',
            b'6\r\nid: 1\n\r\n',
            b'8\r\ndata: 1\n\r\n',
            b'8\r\ndata: 2\n\r\n',
            b'1\r\n\n\r\n',
            b'6\r\nid: 2\n\r\n',
            b'8\r\ndata: 3\n\r\n',
            b'8\r\ndata: 4\n\r\n',
            b'1\r\n\n\r\n',
            b'6\r\nid: 3\n\r\n',
            b'8\r\ndata: 5\n\r\n',
            b'8\r\ndata: 6\n\r\n',
            b'1\r\n\n\r\n',
            b'6\r\nid: 4\n\r\n8\r\ndata: 7\n\r\n8\r\ndata: 8\n\r\n',
            b'1\r\n\n\r\n',
        ]
        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        timer = Timer(duration=0.5)
        while response.parser and not timer.expired:
            alpha.serviceTxesAllIx()
            response.parse()
            beta.serviceReceives()
            time.sleep(0.01)

        if response.parser:
            response.parser.close()
            response.parser = None

        response.dictify()

        self.assertEqual(len(beta.rxbs), 0)
        self.assertEqual(response.eventSource.retry, 1000)
        self.assertEqual(response.retry, response.eventSource.retry)
        self.assertTrue(int(response.eventSource.leid) >= 2)
        self.assertEqual(response.leid, response.eventSource.leid)
        self.assertTrue(len(response.events) > 2)
        event = response.events.popleft()
        self.assertEqual(event, {'id': '0', 'name': '', 'data': 'START'})
        event = response.events.popleft()
        self.assertEqual(event, {'id': '1', 'name': '', 'data': '1\n2'})
        event = response.events.popleft()
        self.assertEqual(event, {'id': '2', 'name': '', 'data': '3\n4'})
        self.assertTrue(len(response.body) == 0)
        self.assertTrue(len(response.eventSource.raw) == 0)

        alpha.close()
        beta.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def testNonBlockingRequestStreamFancyJson(self):
        """
        Test NonBlocking Http client to server Fancy SSE with chunked transfer encoding
        """
        console.terse("{0}\n".format(self.testNonBlockingRequestStreamFancyJson.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True, same=True)
        result = wireLogBeta.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        beta = tcp.Client(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to server ...\n")
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

        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 6061
        method = u'GET'
        path = u'/fancy?idify=true&jsonify=true'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))
        headers = odict([(u'Accept', u'application/json')])
        request =  clienting.Requester(hostname=host,
                                         port=port,
                                         method=method,
                                         path=path,
                                         headers=headers)
        msgOut = request.build()
        lines = [
            b'GET /fancy?idify=true&jsonify=true HTTP/1.1',
            b'Host: 127.0.0.1:6061',
            b'Accept-Encoding: identity',
            b'Accept: application/json',
            b'',
            b'',
        ]
        for i, line in enumerate(lines):
            self.assertEqual(line, request.lines[i])

        self.assertEqual(request.head, b'GET /fancy?idify=true&jsonify=true HTTP/1.1\r\nHost: 127.0.0.1:6061\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, request.head)

        console.terse("Beta requests to Alpha\n")
        beta.tx(msgOut)
        while beta.txes and not ixBeta.rxbs :
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        lines = [
            b'HTTP/1.0 200 OK\r\n',
            b'Server: PasteWSGIServer/0.5 Python/2.7.9\r\n',
            b'Date: Thu, 30 Apr 2015 21:35:25 GMT\r\n'
            b'Content-Type: text/event-stream\r\n',
            b'Cache-Control: no-cache\r\n',
            b'Connection: close\r\n\r\n',
        ]

        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.rxbs:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)

        console.terse("Beta processes response \n")
        response = clienting.Respondent(msg=beta.rxbs,
                                      method=method,
                                      dictable=True,
                                      )

        lines =  [
            b'retry: 1000\n\n',
            b'id: 0\ndata: START\n\n',
            b'id: 1\ndata: {"count":1}\n\n',
            b'id: 2\n',
            b'data: {"count":2}\n\n',
            b'id: 3\ndata: {"count":3}\n\n',
            b'id: 4\ndata: {"count":4}\n\n',
        ]
        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        timer = Timer(duration=0.5)
        while response.parser and not timer.expired:
            alpha.serviceTxesAllIx()
            response.parse()
            beta.serviceReceives()
            time.sleep(0.01)

        if response.parser:
            response.parser.close()
            response.parser = None

        self.assertEqual(len(beta.rxbs), 0)
        self.assertEqual(response.eventSource.retry, 1000)
        self.assertEqual(response.retry, response.eventSource.retry)
        self.assertTrue(int(response.eventSource.leid) >= 2)
        self.assertEqual(response.leid, response.eventSource.leid)
        self.assertTrue(len(response.events) > 2)
        event = response.events.popleft()
        self.assertEqual(event, {'id': '0', 'name': '', 'data': 'START'})
        event = response.events.popleft()
        self.assertEqual(event, {'id': '1', 'name': '', 'data': {'count': 1}})
        event = response.events.popleft()
        self.assertEqual(event, {'id': '2', 'name': '', 'data': {'count': 2}})
        self.assertTrue(len(response.body) == 0)
        self.assertTrue(len(response.eventSource.raw) == 0)

        alpha.close()
        beta.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def testNonBlockingRequestStreamFancyJsonChunked(self):
        """
        Test NonBlocking Http client to server Fancy SSE with chunked transfer encoding
        """
        console.terse("{0}\n".format(self.testNonBlockingRequestStreamFancyJsonChunked.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True, same=True)
        result = wireLogBeta.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        beta = tcp.Client(ha=alpha.eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.accepted, False)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to server ...\n")
        while True:
            beta.serviceConnect()
            alpha.serviceConnects()
            if beta.accepted and beta.ca in alpha.ixes:
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

        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 6061
        method = u'GET'
        path = u'/fancy?idify=true&jsonify=true'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))
        headers = odict([(u'Accept', u'application/json')])
        request =  clienting.Requester(hostname=host,
                                         port=port,
                                         method=method,
                                         path=path,
                                         headers=headers)
        msgOut = request.build()
        lines = [
            b'GET /fancy?idify=true&jsonify=true HTTP/1.1',
            b'Host: 127.0.0.1:6061',
            b'Accept-Encoding: identity',
            b'Accept: application/json',
            b'',
            b'',
        ]
        for i, line in enumerate(lines):
            self.assertEqual(line, request.lines[i])

        self.assertEqual(request.head, b'GET /fancy?idify=true&jsonify=true HTTP/1.1\r\nHost: 127.0.0.1:6061\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, request.head)

        console.terse("Beta requests to Alpha\n")
        beta.tx(msgOut)
        while beta.txes and not ixBeta.rxbs :
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        lines = [
            b'HTTP/1.1 200 OK\r\n',
            b'Content-Type: text/event-stream\r\n',
            b'Cache-Control: no-cache\r\n',
            b'Transfer-Encoding: chunked\r\n',
            b'Date: Thu, 30 Apr 2015 22:11:53 GMT\r\n',
            b'Server: IoBook.local\r\n\r\n',
        ]

        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.rxbs:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)

        console.terse("Beta processes response \n")
        response = clienting.Respondent(msg=beta.rxbs,
                                      method=method,
                                      dictable=True)

        lines =  [
            b'd\r\nretry: 1000\n\n\r\n',
            b'6\r\nid: 0\n\r\n'
            b'd\r\ndata: START\n\n\r\n',
            b'6\r\nid: 1\n\r\n',
            b'12\r\ndata: {"count":1}\n\r\n',
            b'1\r\n\n\r\n',
            b'6\r\nid: 2\n\r\n12\r\ndata: {"count":2}\n\r\n1\r\n\n\r\n',
            b'6\r\nid: 3\n\r\n12\r\ndata: {"count":3}\n\r\n1\r\n\n\r\n',
            b'6\r\nid: 4\n\r\n12\r\ndata: {"count":4}\n\r\n1\r\n\n\r\n',
        ]
        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        timer = Timer(duration=0.5)
        while response.parser and not timer.expired:
            alpha.serviceTxesAllIx()
            response.parse()
            beta.serviceReceives()
            time.sleep(0.01)

        if response.parser:
            response.parser.close()
            response.parser = None

        response.dictify()

        self.assertEqual(len(beta.rxbs), 0)
        self.assertEqual(response.eventSource.retry, 1000)
        self.assertEqual(response.retry, response.eventSource.retry)
        self.assertTrue(int(response.eventSource.leid) >= 2)
        self.assertEqual(response.leid, response.eventSource.leid)
        self.assertTrue(len(response.events) > 2)
        event = response.events.popleft()
        self.assertEqual(event, {'id': '0', 'name': '', 'data': 'START'})
        event = response.events.popleft()
        self.assertEqual(event, {'id': '1', 'name': '', 'data': {'count': 1}})
        event = response.events.popleft()
        self.assertEqual(event, {'id': '2', 'name': '', 'data': {'count': 2}})
        self.assertTrue(len(response.body) == 0)
        self.assertTrue(len(response.eventSource.raw) == 0)

        alpha.close()
        beta.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def testNonBlockingRequestEchoTLS(self):
        """
        Test NonBlocking HTTPS (TLS/SSL) client
        """
        console.terse("{0}\n".format(self.testNonBlockingRequestEchoTLS.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        serverKeypath = '/etc/pki/tls/certs/server_key.pem'  # local server private key
        serverCertpath = '/etc/pki/tls/certs/server_cert.pem'  # local server public cert
        clientCafilepath = '/etc/pki/tls/certs/client.pem' # remote client public cert

        clientKeypath = '/etc/pki/tls/certs/client_key.pem'  # local client private key
        clientCertpath = '/etc/pki/tls/certs/client_cert.pem'  # local client public cert
        serverCafilepath = '/etc/pki/tls/certs/server.pem' # remote server public cert

        alpha = tcp.ServerTls(host='localhost',
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
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        serverCertCommonName = 'localhost' # match hostname uses servers's cert commonname

        beta = tcp.ClientTls(ha=alpha.ha,
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

        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 6061
        method = u'GET'
        path = u'/echo?name=fame'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))
        headers = odict([(u'Accept', u'application/json')])
        request =  clienting.Requester(hostname=host,
                                     port=port,
                                     method=method,
                                     path=path,
                                     headers=headers)
        msgOut = request.build()
        lines = [
                   b'GET /echo?name=fame HTTP/1.1',
                   b'Host: 127.0.0.1:6061',
                   b'Accept-Encoding: identity',
                   b'Accept: application/json',
                   b'',
                   b'',
                ]
        for i, line in enumerate(lines):
            self.assertEqual(line, request.lines[i])

        self.assertEqual(request.head, b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6061\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6061\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')

        console.terse("Beta requests to Alpha\n")
        beta.tx(msgOut)
        while beta.txes and not ixBeta.rxbs :
            beta.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.rxbs:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.rxbs)
        self.assertEqual(msgIn, msgOut)

        console.terse("Beta processes response \n")
        response = clienting.Respondent(msg=beta.rxbs, method=method)
        while response.parser:
            response.parse()

        response.dictify()

        #self.assertEqual(bytes(response.body), b'{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}')
        self.assertEqual(bytes(response.body), b'')
        self.assertEqual(response.data, {'action': None,
                                         'content': None,
                                         'query': {'name': 'fame'},
                                         'url': 'http://127.0.0.1:8080/echo?name=fame',
                                         'verb': 'GET'}
                        )
        self.assertEqual(len(beta.rxbs), 0)
        self.assertEqual(response.headers.items(), [('content-length', '122'),
                                                    ('content-type', 'application/json'),
                                                    ('date', 'Thu, 30 Apr 2015 19:37:17 GMT'),
                                                    ('server', 'IoBook.local')])

        alpha.close()
        beta.close()

        wireLogAlpha.close()
        wireLogBeta.close()



    def testPatronRequestEcho(self):
        """
        Test Patron request echo non blocking
        """
        console.terse("{0}\n".format(self.testPatronRequestEcho.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Connector ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()
        host = alpha.eha[0]
        port = alpha.eha[1]
        method = u'GET'
        path = u'/echo?name=fame'
        headers = odict([(u'Accept', u'application/json')])


        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     hostname=host,
                                     port=port,
                                     method=method,
                                     path=path,
                                     headers=headers,
                                     )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        console.terse("Connecting beta to server ...\n")
        while True:
            beta.connector.serviceConnect()
            alpha.serviceConnects()
            if beta.connector.connected and beta.connector.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)
        self.assertEqual(beta.connector.ca, beta.connector.cs.getsockname())
        self.assertEqual(beta.connector.ha, beta.connector.cs.getpeername())
        self.assertEqual(alpha.eha, beta.connector.ha)

        ixBeta = alpha.ixes[beta.connector.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)
        self.assertEqual(ixBeta.cs.getsockname(), beta.connector.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.connector.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.connector.ca)
        self.assertEqual(ixBeta.ha, beta.connector.ha)

        msgOut = beta.requester.build()
        lines = [
                   b'GET /echo?name=fame HTTP/1.1',
                   b'Host: 127.0.0.1:6101',
                   b'Accept-Encoding: identity',
                   b'Accept: application/json',
                   b'',
                   b'',
                ]
        for i, line in enumerate(lines):
            self.assertEqual(line, beta.requester.lines[i])

        self.assertEqual(beta.requester.head, b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')

        console.terse("Beta requests to Alpha\n")
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))
        beta.connector.tx(msgOut)
        while beta.connector.txes and not ixBeta.rxbs :
            beta.connector.serviceTxes()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.connector.rxbs:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.connector.serviceReceives()
            time.sleep(0.05)
        msgIn = bytes(beta.connector.rxbs)
        self.assertEqual(msgIn, msgOut)

        console.terse("Beta processes response \n")

        while beta.respondent.parser:
            beta.respondent.parse()

        beta.respondent.dictify()

        self.assertEqual(bytes(beta.respondent.body), b'')
        self.assertEqual(beta.respondent.data, {'action': None,
                                         'content': None,
                                         'query': {'name': 'fame'},
                                         'url': 'http://127.0.0.1:8080/echo?name=fame',
                                         'verb': 'GET'}
                         )
        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertEqual(beta.respondent.headers.items(), [('content-length', '122'),
                                                    ('content-type', 'application/json'),
                                                    ('date', 'Thu, 30 Apr 2015 19:37:17 GMT'),
                                                    ('server', 'IoBook.local')])

        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()



    def testPatronServiceEcho(self):
        """
        Test Patron service request response of echo non blocking
        """
        console.terse("{0}\n".format(self.testPatronServiceEcho.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Connector ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()
        host = alpha.eha[0]
        port = alpha.eha[1]
        method = u'GET'
        path = u'/echo?name=fame'
        headers = odict([(u'Accept', u'application/json')])


        beta = clienting.Patron(bufsize=131072,
                              wlog=wireLogBeta,
                              hostname=host,
                              port=port,
                              method=method,
                              path=path,
                              headers=headers,
                              )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        console.terse("Connecting beta to server ...\n")
        while True:
            beta.connector.serviceConnect()
            alpha.serviceConnects()
            if beta.connector.connected and beta.connector.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)
        self.assertEqual(beta.connector.ca, beta.connector.cs.getsockname())
        self.assertEqual(beta.connector.ha, beta.connector.cs.getpeername())
        self.assertEqual(alpha.eha, beta.connector.ha)

        ixBeta = alpha.ixes[beta.connector.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)
        self.assertEqual(ixBeta.cs.getsockname(), beta.connector.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.connector.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.connector.ca)
        self.assertEqual(ixBeta.ha, beta.connector.ha)

        beta.transmit()

        lines = [
                   b'GET /echo?name=fame HTTP/1.1',
                   b'Host: 127.0.0.1:6101',
                   b'Accept-Encoding: identity',
                   b'Accept: application/json',
                   b'',
                   b'',
                ]
        for i, line in enumerate(lines):
            self.assertEqual(line, beta.requester.lines[i])

        msgOut = beta.connector.txes[0]
        self.assertEqual(beta.requester.head, b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n')

        console.terse("Beta requests to Alpha\n")
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))

        while beta.connector.txes and not ixBeta.rxbs :
            beta.serviceAll()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        console.terse("Beta processes response \n")
        msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.respondent.ended:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)
        self.assertEqual(len(beta.responses), 1)

        self.assertEqual(bytes(beta.respondent.body), b'')
        self.assertEqual(beta.respondent.data, {'action': None,
                                         'content': None,
                                         'query': {'name': 'fame'},
                                         'url': 'http://127.0.0.1:8080/echo?name=fame',
                                         'verb': 'GET'}
                         )
        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertEqual(beta.respondent.headers.items(), [('content-length', '122'),
                                                    ('content-type', 'application/json'),
                                                    ('date', 'Thu, 30 Apr 2015 19:37:17 GMT'),
                                                    ('server', 'IoBook.local')])

        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()



    def testPatronPipelineEcho(self):
        """
        Test Patron pipeline servicing
        """
        console.terse("{0}\n".format(self.testPatronPipelineEcho.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Connector ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()
        host = alpha.eha[0]
        port = alpha.eha[1]

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     hostname=host,
                                     port=port,
                                     reconnectable=True,
                                     )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        console.terse("Connecting beta to server ...\n")
        while True:
            beta.connector.serviceConnect()
            alpha.serviceConnects()
            if beta.connector.connected and beta.connector.ca in alpha.ixes:
                break
            time.sleep(0.05)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)
        self.assertEqual(beta.connector.ca, beta.connector.cs.getsockname())
        self.assertEqual(beta.connector.ha, beta.connector.cs.getpeername())
        self.assertEqual(alpha.eha, beta.connector.ha)

        ixBeta = alpha.ixes[beta.connector.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)
        self.assertEqual(ixBeta.cs.getsockname(), beta.connector.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.connector.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.connector.ca)
        self.assertEqual(ixBeta.ha, beta.connector.ha)

        request = odict([('method', u'GET'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('body', None),
                        ])

        beta.requests.append(request)

        console.terse("Beta requests to Alpha\n")
        console.terse("from {0}:{1}, {2} {3} ...\n".format(beta.connector.ha[0],
                                                         beta.connector.ha[1],
                                                         request['method'],
                                                         request['path']))

        while (beta.requests or beta.connector.txes) and not ixBeta.rxbs :
            beta.serviceAll()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        msgOut = b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n'
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        console.terse("Beta processes response \n")
        msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.respondent.ended:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': '127.0.0.1',
                                         'port': 6101,
                                         'scheme': 'http',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        beta.requests.append(request)

        console.terse("\nBeta requests to Alpha again\n")
        console.terse("from {0}:{1}, {2} {3} ...\n".format(beta.connector.ha[0],
                                                           beta.connector.ha[1],
                                                           request['method'],
                                                           request['path']))

        while ( beta.requests or beta.connector.txes) and not ixBeta.rxbs :
            beta.serviceAll()
            time.sleep(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
        msgIn = bytes(ixBeta.rxbs)
        msgOut = b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n'
        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        console.terse("Beta processes response \n")
        msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
        ixBeta.tx(msgOut)
        while ixBeta.txes or not beta.respondent.ended:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                         'content-type': 'application/json',
                                         'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                         'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request': {'host': '127.0.0.1',
                                                'port': 6101,
                                                'scheme': 'http',
                                                'method': 'GET',
                                                'path': '/echo',
                                                'qargs': {'name': 'fame'},
                                                'fragment': '',
                                                'headers': {'accept': 'application/json'},
                                                'body': b'',
                                                'data': None,
                                                'fargs': None,
                                                }
                                    })

        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def mockEchoService(self, server):
        """
        mock echo server service
        """
        server.serviceConnects()
        if server.ixes:
            server.serviceReceivesAllIx()

            ixClient = server.ixes.values()[0]
            msgIn = bytes(ixClient.rxbs)
            if  msgIn== b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n':
                ixClient.clearRxbs()
                msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
                ixClient.tx(msgOut)
                msgIn = b''
                msgOut = b''

            server.serviceTxesAllIx()

    def testPatronPipelineEchoSimple(self):
        """
        Test Patron pipeline servicing
        """
        console.terse("{0}\n".format(self.testPatronPipelineEchoSimple.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Connector ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()
        host = alpha.eha[0]
        port = alpha.eha[1]

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     hostname=host,
                                     port=port,
                                     reconnectable=True,
                                     )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('body', None),
                        ])

        beta.requests.append(request)

        while (not alpha.ixes or  beta.requests or
               beta.connector.txes or not beta.respondent.ended):
            self.mockEchoService(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': '127.0.0.1',
                                         'port': 6101,
                                         'scheme': 'http',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        beta.requests.append(request)

        while (not alpha.ixes or  beta.requests or
                beta.connector.txes or not beta.respondent.ended):
            self.mockEchoService(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': '127.0.0.1',
                                         'port': 6101,
                                         'scheme': 'http',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def mockEchoServicePath(self, server):
        """
        mock echo server service
        """
        server.serviceConnects()
        if server.ixes:
            server.serviceReceivesAllIx()

            ixClient = server.ixes.values()[0]
            msgIn = bytes(ixClient.rxbs)
            if  msgIn== b'GET /echo?name=fame HTTP/1.1\r\nHost: localhost:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n':
                ixClient.clearRxbs()
                msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
                ixClient.tx(msgOut)
                msgIn = b''
                msgOut = b''

            server.serviceTxesAllIx()

    def testPatronPipelineEchoSimplePath(self):
        """
        Test Patron pipeline servicing using path components for host port scheme
        """
        console.terse("{0}\n".format(self.testPatronPipelineEchoSimplePath.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Connector ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        #host = alpha.eha[0]
        #port = alpha.eha[1]
        path = "http://{0}:{1}/".format('localhost', alpha.eha[1])

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     path=path,
                                     reconnectable=True,
                                     )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('body', None),
                        ])

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
                beta.connector.txes or not beta.respondent.ended):
            self.mockEchoServicePath(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6101,
                                         'scheme': 'http',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
                beta.connector.txes or not beta.respondent.ended):
            self.mockEchoServicePath(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6101,
                                         'scheme': 'http',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def testPatronPipelineEchoSimplePathTrack(self):
        """
        Test Patron pipeline servicing using path components for host port scheme
        Request includes tracking information that is included in reponses copy
        of request
        """
        console.terse("{0}\n".format(self.testPatronPipelineEchoSimplePathTrack.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Connector ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        #host = alpha.eha[0]
        #port = alpha.eha[1]
        path = "http://{0}:{1}/".format('localhost', alpha.eha[1])

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     path=path,
                                     reconnectable=True,
                                     )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('body', None),
                         ('mid', 1),
                         ('drop', '.stuff.reply'),
                        ])

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
                beta.connector.txes or not beta.respondent.ended):
            self.mockEchoServicePath(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6101,
                                         'scheme': 'http',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                         'mid': 1,
                                         'drop': '.stuff.reply'
                                        }
                                    })

        request.update(mid=2, drop='.puff.reply')
        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
                beta.connector.txes or not beta.respondent.ended):
            self.mockEchoServicePath(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6101,
                                         'scheme': 'http',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                         'mid': 2,
                                         'drop': '.puff.reply'
                                        }
                                    })

        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def mockEchoServiceJson(self, server):
        """
        mock echo server service with json data request body
        """
        server.serviceConnects()
        if server.ixes:
            server.serviceReceivesAllIx()

            ixClient = server.ixes.values()[0]
            msgIn = bytes(ixClient.rxbs)
            if msgIn == b'PUT /echo?name=fame HTTP/1.1\r\nHost: localhost:6101\r\nAccept-Encoding: identity\r\nContent-Length: 31\r\nAccept: application/json\r\nContent-Type: application/json; charset=utf-8\r\n\r\n{"first":"John","last":"Smith"}':
                ixClient.clearRxbs()
                msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
                ixClient.tx(msgOut)
                msgIn = b''
                msgOut = b''

            server.serviceTxesAllIx()

    def testPatronPipelineEchoJson(self):
        """
        Test Patron pipeline servicing using path components for host port scheme
        with json body in data
        Request includes tracking information that is included in reponses copy
        of request
        """
        console.terse("{0}\n".format(self.testPatronPipelineEchoJson.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Connector ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        #host = alpha.eha[0]
        #port = alpha.eha[1]
        path = "http://{0}:{1}/".format('localhost', alpha.eha[1])

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     path=path,
                                     reconnectable=True,
                                     )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'PUT'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('data', odict([("first", "John"), ("last", "Smith")])),
                         ('mid', 1),
                         ('drop', '.stuff.reply'),
                        ])

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
                beta.connector.txes or not beta.respondent.ended):
            self.mockEchoServiceJson(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6101,
                                         'scheme': 'http',
                                         'method': 'PUT',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json',
                                              'content-type': 'application/json; charset=utf-8'},
                                         'body': b'',
                                         'data': { 'first': 'John', 'last': 'Smith'},
                                         'fargs': None,
                                         'mid': 1,
                                         'drop': '.stuff.reply'
                                        }
                                    })

        request.update(mid=2, drop='.puff.reply')
        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
                beta.connector.txes or not beta.respondent.ended):
            self.mockEchoServiceJson(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6101,
                                         'scheme': 'http',
                                         'method': 'PUT',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json',
                                              'content-type': 'application/json; charset=utf-8'},
                                         'body': b'',
                                         'data': { 'first': 'John', 'last': 'Smith'},
                                         'fargs': None,
                                         'mid': 2,
                                         'drop': '.puff.reply'
                                        }
                                    })

        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def testPatronPipelineStream(self):
        """
        Test Patron pipeline stream
        """
        console.terse("{0}\n".format(self.testPatronPipelineStream.__doc__))



        store = storing.Store(stamp=0.0)

        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.Server(port = 6101,
                                   bufsize=131072,
                                   wlog=wireLogAlpha,
                                   store=store)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Connector ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()
        host = alpha.eha[0]
        port = alpha.eha[1]


        beta = clienting.Patron(bufsize=131072,
                                 wlog=wireLogBeta,
                                 hostname=host,
                                 port=port,
                                 store=store,
                                 reconnectable=True,
                                 )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        console.terse("Connecting beta to server ...\n")
        while True:
            beta.serviceAll()
            alpha.serviceConnects()
            if beta.connector.connected and beta.connector.ca in alpha.ixes:
                break
            time.sleep(0.05)
            beta.connector.store.advanceStamp(0.05)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)
        self.assertEqual(beta.connector.ca, beta.connector.cs.getsockname())
        self.assertEqual(beta.connector.ha, beta.connector.cs.getpeername())
        self.assertEqual(alpha.eha, beta.connector.ha)

        ixBeta = alpha.ixes[beta.connector.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)
        self.assertEqual(ixBeta.cs.getsockname(), beta.connector.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.connector.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.connector.ca)
        self.assertEqual(ixBeta.ha, beta.connector.ha)

        console.terse("{0}\n".format("Building Request ...\n"))
        request = odict([('method', u'GET'),
                         ('path', u'/stream'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('body', None),
                        ])

        beta.requests.append(request)

        console.terse("Beta requests to Alpha\n")
        console.terse("from {0}:{1}, {2} {3} ...\n".format(beta.connector.ha[0],
                                                         beta.connector.ha[1],
                                                         request['method'],
                                                         request['path']))

        while (beta.requests or beta.connector.txes) and not ixBeta.rxbs:
            beta.serviceAll()
            time.sleep(0.05)
            beta.connector.store.advanceStamp(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
            beta.connector.store.advanceStamp(0.05)

        msgIn = bytes(ixBeta.rxbs)
        msgOut = b'GET /stream HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n'

        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        lines = [
            b'HTTP/1.0 200 OK\r\n',
            b'Server: PasteWSGIServer/0.5 Python/2.7.9\r\n',
            b'Date: Thu, 30 Apr 2015 21:35:25 GMT\r\n'
            b'Content-Type: text/event-stream\r\n',
            b'Cache-Control: no-cache\r\n',
            b'Connection: close\r\n\r\n',
            b'retry: 1000\n\n',
            b'id: 0\ndata: START\n\n',
            b'id: 1\ndata: 1\ndata: 2\n\n',
            b'id: 2\ndata: 3\ndata: 4\n\n',
            b'id: 3\ndata: 5\ndata: 6\n\n',
            b'id: 4\ndata: 7\ndata: 8\n\n',
        ]

        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        timer = StoreTimer(store=store, duration=0.5)
        while ixBeta.txes or not timer.expired:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.connector.store.advanceStamp(0.05)
            beta.serviceAll()
            time.sleep(0.05)
            beta.connector.store.advanceStamp(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)

        #timed out while stream still open so no responses in .responses
        self.assertIs(beta.waited, True)
        self.assertIs(beta.respondent.ended, False)
        self.assertEqual(len(beta.responses), 0)

        # but are events in .events
        self.assertEqual(len(beta.events), 5)
        self.assertEqual(beta.respondent.retry, 1000)
        self.assertEqual(beta.respondent.leid, '4')
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '0', 'name': '', 'data': 'START'})
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '1', 'name': '', 'data': '1\n2'})
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '2', 'name': '', 'data': '3\n4'})
        beta.events.clear()

        # alpha's ixBeta connection shutdown prematurely
        console.terse("Disconnecting server so beta must auto reconnect ...\n")
        alpha.closeIx(beta.connector.ca)
        alpha.removeIx(beta.connector.ca)
        while True:
            beta.serviceAll()
            if not beta.connector.connected:
                break
            time.sleep(0.1)
            beta.connector.store.advanceStamp(0.1)

        self.assertIs(beta.connector.cutoff, False)

        console.terse("Auto reconnecting beta and rerequesting...\n")
        while True:
            beta.serviceAll()
            alpha.serviceConnects()
            if beta.connector.connected and beta.connector.ca in alpha.ixes:
                break
            time.sleep(0.05)
            beta.connector.store.advanceStamp(0.05)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)
        self.assertEqual(beta.connector.ca, beta.connector.cs.getsockname())
        self.assertEqual(beta.connector.ha, beta.connector.cs.getpeername())
        self.assertEqual(alpha.eha, beta.connector.ha)

        ixBeta = alpha.ixes[beta.connector.ca]
        self.assertIsNotNone(ixBeta.ca)
        self.assertIsNotNone(ixBeta.cs)
        self.assertEqual(ixBeta.cs.getsockname(), beta.connector.cs.getpeername())
        self.assertEqual(ixBeta.cs.getpeername(), beta.connector.cs.getsockname())
        self.assertEqual(ixBeta.ca, beta.connector.ca)
        self.assertEqual(ixBeta.ha, beta.connector.ha)

        console.terse("Server receiving...\n")
        while (beta.requests or beta.connector.txes) or not ixBeta.rxbs:
            beta.serviceAll()
            time.sleep(0.05)
            beta.connector.store.advanceStamp(0.05)
            alpha.serviceReceivesAllIx()
            time.sleep(0.05)
            beta.connector.store.advanceStamp(0.05)

        msgIn = bytes(ixBeta.rxbs)
        msgOut = b'GET /stream HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\nLast-Event-Id: 4\r\n\r\n'

        self.assertEqual(msgIn, msgOut)
        ixBeta.clearRxbs()

        console.terse("Alpha responds to Beta\n")
        lines = [
            b'HTTP/1.0 200 OK\r\n',
            b'Server: PasteWSGIServer/0.5 Python/2.7.9\r\n',
            b'Date: Thu, 30 Apr 2015 21:35:25 GMT\r\n'
            b'Content-Type: text/event-stream\r\n',
            b'Cache-Control: no-cache\r\n',
            b'Connection: close\r\n\r\n',
            b'id: 5\ndata: 9\ndata: 10\n\n',
            b'id: 6\ndata: 11\ndata: 12\n\n',
        ]

        msgOut = b''.join(lines)
        ixBeta.tx(msgOut)
        timer = StoreTimer(store=store, duration=0.5)
        while ixBeta.txes or not timer.expired:
            alpha.serviceTxesAllIx()
            time.sleep(0.05)
            beta.connector.store.advanceStamp(0.05)
            beta.serviceAll()
            time.sleep(0.05)
            beta.connector.store.advanceStamp(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)

        #timed out while stream still open so no responses in .responses
        self.assertIs(beta.waited, True)
        self.assertIs(beta.respondent.ended, False)
        self.assertEqual(len(beta.responses), 0)

        # but are events in .events
        self.assertEqual(len(beta.events), 2)
        self.assertEqual(beta.respondent.retry, 1000)
        self.assertEqual(beta.respondent.leid, '6')
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '5', 'name': '', 'data': '9\n10'})
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '6', 'name': '', 'data': '11\n12'})


        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def mockEchoServiceSecure(self, server):
        """
        mock echo server service TLS secure
        """
        server.serviceConnects()
        if server.ixes:
            server.serviceReceivesAllIx()

            ixClient = server.ixes.values()[0]
            msgIn = bytes(ixClient.rxbs)
            if  msgIn== b'GET /echo?name=fame HTTP/1.1\r\nHost: localhost:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n':
                ixClient.clearRxbs()
                msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
                ixClient.tx(msgOut)
                msgIn = b''
                msgOut = b''

            server.serviceTxesAllIx()

    def testPatronPipelineEchoSimpleSecure(self):
        """
        Test Patron pipeline servicing
        """
        console.terse("{0}\n".format(self.testPatronPipelineEchoSimpleSecure.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        serverKeypath = '/etc/pki/tls/certs/server_key.pem'  # local server private key
        serverCertpath = '/etc/pki/tls/certs/server_cert.pem'  # local server public cert
        clientCafilepath = '/etc/pki/tls/certs/client.pem' # remote client public cert

        clientKeypath = '/etc/pki/tls/certs/client_key.pem'  # local client private key
        clientCertpath = '/etc/pki/tls/certs/client_cert.pem'  # local client public cert
        serverCafilepath = '/etc/pki/tls/certs/server.pem' # remote server public cert

        serverCertCommonName = 'localhost' # match hostname uses servers's cert commonname

        alpha = tcp.ServerTls(host=serverCertCommonName,
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
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Patron ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()
        host = alpha.eha[0]
        port = alpha.eha[1]

        beta = clienting.Patron(hostname=serverCertCommonName,
                              port=alpha.eha[1],
                              bufsize=131072,
                              wlog=wireLogBeta,
                              scheme='https',
                              reconnectable=True,
                              certedhost=serverCertCommonName,
                              keypath=clientKeypath,
                              certpath=clientCertpath,
                              cafilepath=serverCafilepath,
                            )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('body', None),
                        ])

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
               beta.connector.txes or not beta.respondent.ended):
            self.mockEchoServiceSecure(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6101,
                                         'scheme': 'https',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
               beta.connector.txes or not beta.respondent.ended):
            self.mockEchoServiceSecure(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6101,
                                         'scheme': 'https',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def testPatronPipelineEchoSimpleSecurePath(self):
        """
        Test Patron pipeline servicing
        """
        console.terse("{0}\n".format(self.testPatronPipelineEchoSimpleSecurePath.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        serverKeypath = '/etc/pki/tls/certs/server_key.pem'  # local server private key
        serverCertpath = '/etc/pki/tls/certs/server_cert.pem'  # local server public cert
        clientCafilepath = '/etc/pki/tls/certs/client.pem' # remote client public cert

        clientKeypath = '/etc/pki/tls/certs/client_key.pem'  # local client private key
        clientCertpath = '/etc/pki/tls/certs/client_cert.pem'  # local client public cert
        serverCafilepath = '/etc/pki/tls/certs/server.pem' # remote server public cert

        serverCertCommonName = 'localhost' # match hostname uses servers's cert commonname

        alpha = tcp.ServerTls(host=serverCertCommonName,
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
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Patron ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()
        #host = alpha.eha[0]
        #port = alpha.eha[1]
        path = "https://{0}:{1}/".format(serverCertCommonName, alpha.eha[1])

        beta = clienting.Patron(path=path,
                              bufsize=131072,
                              wlog=wireLogBeta,
                              reconnectable=True,
                              keypath=clientKeypath,
                              certpath=clientCertpath,
                              cafilepath=serverCafilepath,
                            )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('body', None),
                        ])

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
               beta.connector.txes or not beta.respondent.ended):
            self.mockEchoServiceSecure(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6101,
                                         'scheme': 'https',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
               beta.connector.txes or not beta.respondent.ended):
            self.mockEchoServiceSecure(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6101,
                                         'scheme': 'https',
                                         'method': 'GET',
                                         'path': '/echo',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


    def mockRedirectService(self, server):
        """
        mock echo server service
        """
        server.serviceConnects()
        if server.ixes:
            server.serviceReceivesAllIx()

            ixClient = server.ixes.values()[0]
            msgIn = bytes(ixClient.rxbs)
            if msgIn == b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n':
                ixClient.clearRxbs()
                msgOut = b'HTTP/1.1 307 Temporary Redirect\r\nContent-Type: text/plain\r\nContent-Length: 0\r\nAccess-Control-Allow-Origin: *\r\nLocation: http://localhost:6101/redirect?name=fame\r\n\r\n'
                ixClient.tx(msgOut)
                msgIn = b''
                msgOut = b''

            elif  msgIn== b'GET /redirect?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n':
                ixClient.clearRxbs()
                msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
                ixClient.tx(msgOut)
                msgIn = b''
                msgOut = b''

            server.serviceTxesAllIx()

    def testPatronRedirectSimple(self):
        """
        Test Patron redirect
        """
        console.terse("{0}\n".format(self.testPatronRedirectSimple.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Connector ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()
        host = alpha.eha[0]
        port = alpha.eha[1]

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     hostname=host,
                                     port=port,
                                     reconnectable=True,
                                     )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('body', None),
                        ])

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
               beta.connector.txes or not beta.respondent.ended):
            self.mockRedirectService(alpha)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'redirects': [{'body': bytearray(b''),
                                                   'data': None,
                                                   'headers': {'access-control-allow-origin': '*',
                                                               'content-length': '0',
                                                               'content-type': 'text/plain',
                                                               'location': 'http://localhost:6101/redirect?name=fame'},
                                                   'reason': 'Temporary Redirect',
                                                   'error': None,
                                                   'errored': False,
                                                   'request': {'body': b'',
                                                               'data': None,
                                                               'fargs': None,
                                                               'fragment': '',
                                                               'headers': {'accept': 'application/json'},
                                                               'host': '127.0.0.1',
                                                               'method': 'GET',
                                                               'path': '/echo',
                                                               'port': 6101,
                                                               'qargs': {'name': 'fame'},
                                                               'scheme': 'http'},
                                                   'status': 307,
                                                   'version': (1, 1)}],
                                    'request':
                                        {'host': '127.0.0.1',
                                         'port': 6101,
                                         'scheme': 'http',
                                         'method': 'GET',
                                         'path': '/redirect',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })



        alpha.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()



    def mockRedirectComplexServiceA(self, server):
        """
        mock echo server service
        """
        server.serviceConnects()
        if server.ixes:
            server.serviceReceivesAllIx()

            ixClient = server.ixes.values()[0]
            msgIn = bytes(ixClient.rxbs)
            if msgIn == b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n':
                ixClient.clearRxbs()
                msgOut = b'HTTP/1.1 307 Temporary Redirect\r\nContent-Type: text/plain\r\nContent-Length: 0\r\nAccess-Control-Allow-Origin: *\r\nLocation: http://localhost:6103/redirect?name=fame\r\n\r\n'
                ixClient.tx(msgOut)
                msgIn = b''
                msgOut = b''

            server.serviceTxesAllIx()

    def mockRedirectComplexServiceG(self, server):
        """
        mock echo server service
        """
        server.serviceConnects()
        if server.ixes:
            server.serviceReceivesAllIx()

            ixClient = server.ixes.values()[0]
            msgIn = bytes(ixClient.rxbs)

            if  msgIn== b'GET /redirect?name=fame HTTP/1.1\r\nHost: localhost:6103\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n':
                ixClient.clearRxbs()
                msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
                ixClient.tx(msgOut)
                msgIn = b''
                msgOut = b''

            server.serviceTxesAllIx()


    def testPatronRedirectComplex(self):
        """
        Test Patron redirect
        """
        console.terse("{0}\n".format(self.testPatronRedirectComplex.__doc__))



        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.Server(port = 6101, bufsize=131072, wlog=wireLogAlpha)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        wireLogGamma = wiring.WireLog(buffify=True, same=True)
        result = wireLogGamma.reopen()

        gamma = tcp.Server(port = 6103, bufsize=131072, wlog=wireLogGamma)
        self.assertIs(gamma.reopen(), True)
        self.assertEqual(gamma.ha, ('0.0.0.0', 6103))
        self.assertEqual(gamma.eha, ('127.0.0.1', 6103))

        console.terse("{0}\n".format("Building Connector ...\n"))

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()
        host = alpha.eha[0]
        port = alpha.eha[1]

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     hostname=host,
                                     port=port,
                                     reconnectable=True,
                                     )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('body', None),
                        ])

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
               beta.connector.txes or not beta.respondent.ended):
            self.mockRedirectComplexServiceA(alpha)
            self.mockRedirectComplexServiceG(gamma)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'redirects': [{'body': bytearray(b''),
                                                   'data': None,
                                                   'headers': {'access-control-allow-origin': '*',
                                                               'content-length': '0',
                                                               'content-type': 'text/plain',
                                                               'location': 'http://localhost:6103/redirect?name=fame'},
                                                   'reason': 'Temporary Redirect',
                                                   'error': None,
                                                   'errored': False,
                                                   'request': {'body': b'',
                                                               'data': None,
                                                               'fargs': None,
                                                               'fragment': '',
                                                               'headers': {'accept': 'application/json'},
                                                               'host': '127.0.0.1',
                                                               'method': 'GET',
                                                               'path': '/echo',
                                                               'port': 6101,
                                                               'qargs': {'name': 'fame'},
                                                               'scheme': 'http'},
                                                   'status': 307,
                                                   'version': (1, 1)}],
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6103,
                                         'scheme': 'http',
                                         'method': 'GET',
                                         'path': '/redirect',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        alpha.close()
        gamma.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogGamma.close()
        wireLogBeta.close()



    def mockRedirectComplexServiceASecure(self, server):
        """
        mock echo server service
        """
        server.serviceConnects()
        if server.ixes:
            server.serviceReceivesAllIx()

            ixClient = server.ixes.values()[0]
            msgIn = bytes(ixClient.rxbs)
            if msgIn == b'GET /echo?name=fame HTTP/1.1\r\nHost: localhost:6101\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n':
                ixClient.clearRxbs()
                msgOut = b'HTTP/1.1 307 Temporary Redirect\r\nContent-Type: text/plain\r\nContent-Length: 0\r\nAccess-Control-Allow-Origin: *\r\nLocation: https://localhost:6103/redirect?name=fame\r\n\r\n'
                ixClient.tx(msgOut)
                msgIn = b''
                msgOut = b''

            server.serviceTxesAllIx()

    def mockRedirectComplexServiceGSecure(self, server):
        """
        mock echo server service
        """
        server.serviceConnects()
        if server.ixes:
            server.serviceReceivesAllIx()

            ixClient = server.ixes.values()[0]
            msgIn = bytes(ixClient.rxbs)

            if  msgIn== b'GET /redirect?name=fame HTTP/1.1\r\nHost: localhost:6103\r\nAccept-Encoding: identity\r\nAccept: application/json\r\n\r\n':
                ixClient.clearRxbs()
                msgOut = b'HTTP/1.1 200 OK\r\nContent-Length: 122\r\nContent-Type: application/json\r\nDate: Thu, 30 Apr 2015 19:37:17 GMT\r\nServer: IoBook.local\r\n\r\n{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'
                ixClient.tx(msgOut)
                msgIn = b''
                msgOut = b''

            server.serviceTxesAllIx()

    def testPatronRedirectComplexSecure(self):
        """
        Test Patron redirect
        """
        console.terse("{0}\n".format(self.testPatronRedirectComplexSecure.__doc__))



        serverCertCommonName = 'localhost' # match hostname uses servers's cert commonname
        serverKeypath = '/etc/pki/tls/certs/server_key.pem'  # local server private key
        serverCertpath = '/etc/pki/tls/certs/server_cert.pem'  # local server public cert
        clientCafilepath = '/etc/pki/tls/certs/client.pem' # remote client public cert

        wireLogAlpha = wiring.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = tcp.ServerTls(host=serverCertCommonName,
                                   port = 6101,
                                   bufsize=131072,
                                   wlog=wireLogAlpha,
                                   context=None,
                                   version=None,
                                   certify=None,
                                   keypath=serverKeypath,
                                   certpath=serverCertpath,
                                   cafilepath=clientCafilepath,)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('127.0.0.1', 6101))
        self.assertEqual(alpha.eha, ('127.0.0.1', 6101))

        wireLogGamma = wiring.WireLog(buffify=True, same=True)
        result = wireLogGamma.reopen()

        gamma = tcp.ServerTls(host=serverCertCommonName,
                                   port = 6103,
                                   bufsize=131072,
                                   wlog=wireLogGamma,
                                   context=None,
                                   version=None,
                                   certify=None,
                                   keypath=serverKeypath,
                                   certpath=serverCertpath,
                                   cafilepath=clientCafilepath)
        self.assertIs(gamma.reopen(), True)
        self.assertEqual(gamma.ha, ('127.0.0.1', 6103))
        self.assertEqual(gamma.eha, ('127.0.0.1', 6103))

        console.terse("{0}\n".format("Building Connector ...\n"))

        clientKeypath = '/etc/pki/tls/certs/client_key.pem'  # local client private key
        clientCertpath = '/etc/pki/tls/certs/client_cert.pem'  # local client public cert
        serverCafilepath = '/etc/pki/tls/certs/server.pem' # remote server public cert

        wireLogBeta = wiring.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()
        host = serverCertCommonName
        port = alpha.eha[1]

        beta = clienting.Patron(bufsize=131072,
                              wlog=wireLogBeta,
                              hostname=host,
                              port=port,
                              reconnectable=True,
                              scheme='https',
                              certedhost=serverCertCommonName,
                              keypath=clientKeypath,
                              certpath=clientCertpath,
                              cafilepath=serverCafilepath,)

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/echo?name=fame'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json')])),
                         ('body', None),
                        ])

        beta.requests.append(request)

        while (not alpha.ixes or beta.requests or
               beta.connector.txes or not beta.respondent.ended):
            self.mockRedirectComplexServiceASecure(alpha)
            self.mockRedirectComplexServiceGSecure(gamma)
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertEqual(len(beta.connector.rxbs), 0)
        self.assertIs(beta.waited, False)
        self.assertIs(beta.respondent.ended, True)

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response, {'version': (1, 1),
                                    'status': 200,
                                    'reason': 'OK',
                                    'headers':
                                        {'content-length': '122',
                                        'content-type': 'application/json',
                                        'date': 'Thu, 30 Apr 2015 19:37:17 GMT',
                                        'server': 'IoBook.local'},
                                    'body': bytearray(b''),
                                    'data': {'action': None,
                                             'content': None,
                                             'query': {'name': 'fame'},
                                             'url': 'http://127.0.0.1:8080/echo?name=fame',
                                             'verb': 'GET'},
                                    'error': None,
                                    'errored': False,
                                    'redirects': [{'body': bytearray(b''),
                                                   'data': None,
                                                   'headers': {'access-control-allow-origin': '*',
                                                               'content-length': '0',
                                                               'content-type': 'text/plain',
                                                               'location': 'https://localhost:6103/redirect?name=fame'},
                                                   'reason': 'Temporary Redirect',
                                                   'error': None,
                                                   'errored': False,
                                                   'request': {'body': b'',
                                                               'data': None,
                                                               'fargs': None,
                                                               'fragment': '',
                                                               'headers': {'accept': 'application/json'},
                                                               'host': 'localhost',
                                                               'method': 'GET',
                                                               'path': '/echo',
                                                               'port': 6101,
                                                               'qargs': {'name': 'fame'},
                                                               'scheme': 'https'},
                                                   'status': 307,
                                                   'version': (1, 1)}],
                                    'request':
                                        {'host': 'localhost',
                                         'port': 6103,
                                         'scheme': 'https',
                                         'method': 'GET',
                                         'path': '/redirect',
                                         'qargs': {'name': 'fame'},
                                         'fragment': '',
                                         'headers':
                                             {'accept': 'application/json'},
                                         'body': b'',
                                         'data': None,
                                         'fargs': None,
                                        }
                                    })

        alpha.close()
        gamma.close()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogGamma.close()
        wireLogBeta.close()


    def testMultiPartForm(self):
        """
        Test multipart form for Requester
        """
        console.terse("{0}\n".format(self.testMultiPartForm.__doc__))



        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 6101
        method = u'POST'
        path = u'/echo?name=fame'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, path))
        headers = odict([(u'Accept', u'application/json'),
                         (u'Content-Type', u'multipart/form-data')])
        fargs = odict([("text",  "This is the life,\nIt is the best.\n"),
                       ("html", "<html><body></body><html>")])
        request =  clienting.Requester(hostname=host,
                                     port=port,
                                     method=method,
                                     path=path,
                                     headers=headers)
        msgOut = request.build(fargs=fargs)

        self.assertTrue(b'Content-Disposition: form-data; name="text"\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nThis is the life,\nIt is the best.\n\r\n' in msgOut)
        self.assertTrue(b'Content-Disposition: form-data; name="html"\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n<html><body></body><html>\r\n' in msgOut)
        self.assertTrue(request.head.startswith(b'POST /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:6101\r\nAccept-Encoding: identity\r\nContent-Length: 325\r\nAccept: application/json\r\nContent-Type: multipart/form-data; boundary='))



    def testQueryQuoting(self):
        """
        Test agorithm for parsing and reassembling query
        """
        console.terse("{0}\n".format(self.testQueryQuoting.__doc__))


        location = u'https%3A%2F%2Fapi.twitter.com%2F1.1%2Faccount%2Fverify_credentials.json?oauth_consumer_key=meWtb1jEOCQciCgqheqiQoU&oauth_nonce=eb616fe02004000&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1437580412&oauth_token=1048104-WpGhCC4Fbj9Bp5PaTTuN0laSqD4vxCb2B7xh62YD&oauth_version=1.0&oauth_signature=KBD3DdNVZBjyOd0fqQ9X17ack%3D'
        path, sep, query = location.partition('?')
        path = unquote(path)
        if sep:
            location = sep.join([path, query])
        else:
            location = path

        #location = unquote(location)
        self.assertEqual(location, u'https://api.twitter.com/1.1/account/verify_credentials.json?oauth_consumer_key=meWtb1jEOCQciCgqheqiQoU&oauth_nonce=eb616fe02004000&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1437580412&oauth_token=1048104-WpGhCC4Fbj9Bp5PaTTuN0laSqD4vxCb2B7xh62YD&oauth_version=1.0&oauth_signature=KBD3DdNVZBjyOd0fqQ9X17ack%3D')

        splits = urlsplit(location)
        query = splits.query
        self.assertEqual(query, u'oauth_consumer_key=meWtb1jEOCQciCgqheqiQoU&oauth_nonce=eb616fe02004000&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1437580412&oauth_token=1048104-WpGhCC4Fbj9Bp5PaTTuN0laSqD4vxCb2B7xh62YD&oauth_version=1.0&oauth_signature=KBD3DdNVZBjyOd0fqQ9X17ack%3D')
        querySplits = query.split(u'&')
        self.assertEqual(querySplits, [u'oauth_consumer_key=meWtb1jEOCQciCgqheqiQoU',
                                        u'oauth_nonce=eb616fe02004000',
                                        u'oauth_signature_method=HMAC-SHA1',
                                        u'oauth_timestamp=1437580412',
                                        u'oauth_token=1048104-WpGhCC4Fbj9Bp5PaTTuN0laSqD4vxCb2B7xh62YD',
                                        u'oauth_version=1.0',
                                        u'oauth_signature=KBD3DdNVZBjyOd0fqQ9X17ack%3D'])
        qargs = odict()
        for queryPart in querySplits:  # this prevents duplicates even if desired
            if queryPart:
                if '=' in queryPart:
                    key, val = queryPart.split('=', 1)
                    val = unquote(val)
                else:
                    key = queryPart
                    val = True
                qargs[key] = val

        self.assertEqual(qargs, {u'oauth_consumer_key': u'meWtb1jEOCQciCgqheqiQoU',
                                 u'oauth_nonce': u'eb616fe02004000',
                                 u'oauth_signature_method': u'HMAC-SHA1',
                                 u'oauth_timestamp': u'1437580412',
                                 u'oauth_token': u'1048104-WpGhCC4Fbj9Bp5PaTTuN0laSqD4vxCb2B7xh62YD',
                                 u'oauth_version': u'1.0',
                                 u'oauth_signature': u'KBD3DdNVZBjyOd0fqQ9X17ack='})
        qargParts = [u"{0}={1}".format(key, quote_plus(str(val)))
                     for key, val in qargs.items()]
        newQuery = '&'.join(qargParts)
        self.assertEqual(newQuery, u'oauth_consumer_key=meWtb1jEOCQciCgqheqiQoU&oauth_nonce=eb616fe02004000&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1437580412&oauth_token=1048104-WpGhCC4Fbj9Bp5PaTTuN0laSqD4vxCb2B7xh62YD&oauth_version=1.0&oauth_signature=KBD3DdNVZBjyOd0fqQ9X17ack%3D')




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
             'testNonBlockingRequestEcho',
             'testNonBlockingRequestStream',
             'testNonBlockingRequestStreamChunked',
             'testNonBlockingRequestStreamFancy',
             'testNonBlockingRequestStreamFancyChunked',
             'testNonBlockingRequestStreamFancyJson',
             'testNonBlockingRequestStreamFancyJsonChunked',
             'testNonBlockingRequestEchoTLS',
             'testPatronRequestEcho',
             'testPatronServiceEcho',
             'testPatronPipelineEcho',
             'testPatronPipelineEchoSimple',
             'testPatronPipelineEchoSimplePath',
             'testPatronPipelineEchoSimplePathTrack',
             'testPatronPipelineEchoJson',
             'testPatronPipelineStream',
             'testPatronPipelineEchoSimpleSecure',
             'testPatronPipelineEchoSimpleSecurePath',
             'testPatronRedirectSimple',
             'testPatronRedirectComplex',
             'testPatronRedirectComplexSecure',
             'testMultiPartForm',
             'testQueryQuoting',
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

    #

    #runAll() #run all unittests

    runSome()#only run some

    #runOne('testValetServiceBottle')
    #runOne('testValetServiceBasic')
