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

if sys.version > '3':
    from http.client import HTTPConnection
else:
    from httplib import HTTPConnection

try:
    import simplejson as json
except ImportError:
    import json

# Import ioflo libs
from ioflo.base.globaling import *
from ioflo.base.odicting import odict
#from ioflo.test import testing

from ioflo.aid import nonblocking
from ioflo.aid import httping
from ioflo.base.aiding import Timer

from ioflo.base.consoling import getConsole
console = getConsole()


from ioflo.aid import httping

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

    def testBasic(self):
        """
        Test Basic
        """
        console.terse("{0}\n".format(self.testBasic.__doc__))

        console.terse("{0}\n".format("Connecting ...\n"))
        hc = HTTPConnection('127.0.0.1', port=8080, timeout=1.0,)

        hc.connect()

        console.terse("{0}\n".format("Get '/echo?name=fame' ...\n"))
        headers = odict([('Accept', 'application/json')])
        hc.request(method='GET', url='/echo?name=fame', body=None, headers=headers )
        response = hc.getresponse()
        console.terse(str(response.fileno()) + "\n")  # must call this before read
        console.terse(str(response.getheaders()) + "\n")
        console.terse(str(response.msg)  + "\n")
        console.terse(str(response.version) + "\n")
        console.terse(str(response.status) + "\n")
        console.terse(response.reason + "\n")
        console.terse(str(response.read()) + "\n")

        console.terse("{0}\n".format("Post ...\n"))
        headers = odict([('Accept', 'application/json'), ('Content-Type', 'application/json')])
        body = odict([('name', 'Peter'), ('occupation', 'Engineer')])
        body = ns2b(json.dumps(body, separators=(',', ':'),encoding='utf-8'))
        hc.request(method='POST', url='/demo', body=body, headers=headers )
        response = hc.getresponse()
        console.terse(str(response.fileno()) + "\n") # must call this before read
        console.terse(str(response.getheaders()) + "\n")
        console.terse(str(response.msg)  + "\n")
        console.terse(str(response.version) + "\n")
        console.terse(str(response.status) + "\n")
        console.terse(response.reason+ "\n")
        console.terse(str(response.read()) + "\n")

        #console.terse("{0}\n".format("SSE stream ...\n"))
        #body = b''
        #headers = odict([('Accept', 'application/json'), ('Content-Type', 'application/json')])
        #hc.request(method='GET', url='/stream', body=body, headers=headers )
        #response = hc.getresponse()
        #console.terse(str(response.fileno()) + "\n") # must call this before read
        #console.terse(str(response.getheaders()) + "\n")
        #console.terse(str(response.msg)  + "\n")
        #console.terse(str(response.version) + "\n")
        #console.terse(str(response.status) + "\n")
        #console.terse(response.reason+ "\n")
        #console.terse(str(response.read()) + "\n")

        hc.close()

    def testNonBlockingRequestEcho(self):
        """
        Test NonBlocking Http client
        """
        console.terse("{0}\n".format(self.testNonBlockingRequestEcho.__doc__))

        console.reinit(verbosity=console.Wordage.profuse)

        wireLogBeta = nonblocking.WireLog(buffify=True)
        result = wireLogBeta.reopen()

        #alpha = nonblocking.Server(port = 6101, bufsize=131072, wlog=wireLog)
        #self.assertIs(alpha.reopen(), True)
        #self.assertEqual(alpha.ha, ('0.0.0.0', 6101))

        eha = ('127.0.0.1', 8080)
        beta = nonblocking.Outgoer(ha=eha, bufsize=131072)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to server ...\n")
        while True:
            beta.serviceConnect()
            #alpha.serviceAccepts()
            if beta.connected:  # and beta.ca in alpha.ixes
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertEqual(eha, beta.ha)

        #ixBeta = alpha.ixes[beta.ca]
        #self.assertIsNotNone(ixBeta.ca)
        #self.assertIsNotNone(ixBeta.cs)
        #self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        #self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        #self.assertEqual(ixBeta.ca, beta.ca)
        #self.assertEqual(ixBeta.ha, beta.ha)

        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 8080
        method = u'GET'
        url = u'/echo?name=fame'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, url))
        headers = odict([('Accept', 'application/json')])
        request =  httping.HttpRequestNb(host=host,
                                     port=port,
                                     method=method,
                                     url=url,
                                     headers=headers)
        msgOut = request.build()
        lines = [
                   b'GET /echo?name=fame HTTP/1.1',
                   b'Host: 127.0.0.1:8080',
                   b'Accept-Encoding: identity',
                   b'Content-Length: 0',
                   b'Accept: application/json',
                   b'',
                   b'',
                ]
        for i, line in enumerate(lines):
            self.assertEqual(line, request.lines[i])

        self.assertEqual(request.head, b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nAccept-Encoding: identity\r\nContent-Length: 0\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, b'GET /echo?name=fame HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nAccept-Encoding: identity\r\nContent-Length: 0\r\nAccept: application/json\r\n\r\n')

        beta.transmit(msgOut)
        while beta.txes or not beta.rxbs:
            beta.serviceTxes()
            beta.serviceAllRx()
            time.sleep(0.05)
        beta.serviceAllRx()

        msgIn, index = beta.tailRxbs(0)
        self.assertTrue(msgIn.endswith(b'{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'))

        #response = httping.HttpResponseNb(msgIn, method=method, url=url)
        response = httping.HttpResponseNb(beta.rxbs, method=method, url=url)

        while response.parser:
            response.parse()

        self.assertEqual(bytes(response.body), b'{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}')

        self.assertEqual(len(beta.rxbs), 0)

        #alpha.close()
        beta.close()

        wireLogBeta.close()
        console.reinit(verbosity=console.Wordage.concise)

    def testNonBlockingRequestStream(self):
        """
        Test NonBlocking Http client
        """
        console.terse("{0}\n".format(self.testNonBlockingRequestStream.__doc__))

        console.reinit(verbosity=console.Wordage.profuse)

        wireLogBeta = nonblocking.WireLog(buffify=True)
        result = wireLogBeta.reopen()

        #alpha = nonblocking.Server(port = 6101, bufsize=131072, wlog=wireLog)
        #self.assertIs(alpha.reopen(), True)
        #self.assertEqual(alpha.ha, ('0.0.0.0', 6101))

        eha = ('127.0.0.1', 8080)
        beta = nonblocking.Outgoer(ha=eha, bufsize=131072, wlog=wireLogBeta)
        self.assertIs(beta.reopen(), True)
        self.assertIs(beta.connected, False)
        self.assertIs(beta.cutoff, False)

        console.terse("Connecting beta to server ...\n")
        while True:
            beta.serviceConnect()
            #alpha.serviceAccepts()
            if beta.connected:  # and beta.ca in alpha.ixes
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertIs(beta.cutoff, False)
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertEqual(eha, beta.ha)

        #ixBeta = alpha.ixes[beta.ca]
        #self.assertIsNotNone(ixBeta.ca)
        #self.assertIsNotNone(ixBeta.cs)
        #self.assertEqual(ixBeta.cs.getsockname(), beta.cs.getpeername())
        #self.assertEqual(ixBeta.cs.getpeername(), beta.cs.getsockname())
        #self.assertEqual(ixBeta.ca, beta.ca)
        #self.assertEqual(ixBeta.ha, beta.ha)

        console.terse("{0}\n".format("Building Request ...\n"))
        host = u'127.0.0.1'
        port = 8080
        method = u'GET'
        url = u'/stream'
        console.terse("{0} from  {1}:{2}{3} ...\n".format(method, host, port, url))
        headers = odict([('Accept', 'application/json')])
        request =  httping.HttpRequestNb(host=host,
                                     port=port,
                                     method=method,
                                     url=url,
                                     headers=headers)
        msgOut = request.build()
        lines = [
                   b'GET /stream HTTP/1.1',
                   b'Host: 127.0.0.1:8080',
                   b'Accept-Encoding: identity',
                   b'Content-Length: 0',
                   b'Accept: application/json',
                   b'',
                   b'',
                ]
        for i, line in enumerate(lines):
            self.assertEqual(line, request.lines[i])

        self.assertEqual(request.head, b'GET /stream HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nAccept-Encoding: identity\r\nContent-Length: 0\r\nAccept: application/json\r\n\r\n')
        self.assertEqual(msgOut, request.head)

        beta.transmit(msgOut)
        while beta.txes or not beta.rxbs:
            beta.serviceTxes()
            beta.serviceAllRx()
            time.sleep(0.05)
        beta.serviceAllRx()

        msgIn, index = beta.tailRxbs(0)
        #self.assertTrue(msgIn.endswith(b'{"content": null, "query": {"name": "fame"}, "verb": "GET", "url": "http://127.0.0.1:8080/echo?name=fame", "action": null}'))

        #response = httping.HttpResponseNb(msgIn, method=method, url=url)
        response = httping.HttpResponseNb(beta.rxbs, method=method, url=url,  wlog=wireLogBeta)

        timer = Timer(duration=3.0)
        while response.parser and not timer.expired:
            response.parse()
            beta.serviceAllRx()
            time.sleep(0.01)

        if response.parser:
            response.parser.close()
            response.parser = None

        self.assertTrue(response.body.startswith(b'retry: 1000\n\ndata: START\n\ndata: 1\n\ndata: 2\n\ndata: 3\n\n'))

        #self.assertEqual(len(beta.rxbs), 0)

        #alpha.close()
        beta.close()

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
    names = ['testBasic',
             'testNonBlockingRequestEcho',
             'testNonBlockingRequestStream', ]
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

    #runOne('testBasic')
    #runOne('testNonBlockingRequestEcho')
    runOne('testNonBlockingRequestStream')
