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
from ioflo.base.globaling import *
from ioflo.aid.odicting import odict
#from ioflo.test import testing

from ioflo.aid import nonblocking
from ioflo.aid.timing import Timer, StoreTimer
from ioflo.base import storing

from ioflo.aid.consoling import getConsole
console = getConsole()


from ioflo.aid.http import httping, clienting, serving

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

    def testPorterServiceEcho(self):
        """
        Test Porter service request response of echo non blocking
        """
        console.terse("{0}\n".format(self.testPorterServiceEcho.__doc__))



        store = storing.Store(stamp=0.0)

        console.terse("{0}\n".format("Building Valet ...\n"))
        wireLogAlpha = nonblocking.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = serving.Porter(port = 6101,
                              bufsize=131072,
                              wlog=wireLogAlpha,
                              store=store)
        self.assertIs(alpha.servant.reopen(), True)
        self.assertEqual(alpha.servant.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.servant.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Patron ...\n"))
        wireLogBeta = nonblocking.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        path = "http://{0}:{1}/".format('localhost', alpha.servant.eha[1])

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     store=store,
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
                         ('headers', odict([('Accept', 'application/json'),
                                            ('Content-Length', 0)])),
                        ])

        beta.requests.append(request)

        while (beta.requests or beta.connector.txes or not beta.responses or
               not alpha.servant.ixes or not alpha.idle()):
            alpha.serviceAll()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)

        self.assertEqual(len(alpha.servant.ixes), 1)
        self.assertEqual(len(alpha.stewards), 1)
        requestant = alpha.stewards.values()[0].requestant
        self.assertEqual(requestant.method, request['method'])
        self.assertEqual(requestant.url, request['path'])
        self.assertEqual(requestant.headers, {'accept': 'application/json',
                                                'accept-encoding': 'identity',
                                                'content-length': '0',
                                                'host': 'localhost:6101'})


        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response['data'],{'body': '',
                                        'data': None,
                                        'fragment': '',
                                        'headers': {'accept': 'application/json',
                                                    'accept-encoding': 'identity',
                                                    'content-length': '0',
                                                    'host': 'localhost:6101'},
                                        'method': 'GET',
                                        'path': '/echo',
                                        'qargs': {'name': 'fame'},
                                        'version': 'HTTP/1.1'})

        responder = alpha.stewards.values()[0].responder
        self.assertEqual(responder.status, response['status'])
        self.assertEqual(responder.headers, response['headers'])

        alpha.servant.closeAll()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()

    def testValetServiceBasic(self):
        """
        Test Valet WSGI service request response
        """
        console.terse("{0}\n".format(self.testValetServiceBasic.__doc__))

        store = storing.Store(stamp=0.0)

        def wsgiApp(environ, start_response):
            start_response('200 OK', [('Content-type','text/plain'),
                                      ('Content-length', '12')])
            return [b"Hello World!"]

        console.terse("{0}\n".format("Building Valet ...\n"))
        wireLogAlpha = nonblocking.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = serving.Valet(port = 6101,
                              bufsize=131072,
                              wlog=wireLogAlpha,
                              store=store,
                              app=wsgiApp)
        self.assertIs(alpha.servant.reopen(), True)
        self.assertEqual(alpha.servant.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.servant.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Patron ...\n"))
        wireLogBeta = nonblocking.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        path = "http://{0}:{1}/".format('localhost', alpha.servant.eha[1])

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     store=store,
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
                         ('headers', odict([('Accept', 'application/json'),
                                            ('Content-Length', 0)])),
                        ])

        beta.requests.append(request)

        while (beta.requests or beta.connector.txes or not beta.responses or
               not alpha.idle()):
            alpha.serviceAll()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)

        self.assertEqual(len(alpha.servant.ixes), 1)
        self.assertEqual(len(alpha.reqs), 1)
        self.assertEqual(len(alpha.reps), 1)
        requestant = alpha.reqs.values()[0]
        self.assertEqual(requestant.method, request['method'])
        self.assertEqual(requestant.url, request['path'])
        self.assertEqual(requestant.headers, {'accept': 'application/json',
                                                'accept-encoding': 'identity',
                                                'content-length': '0',
                                                'host': 'localhost:6101'})


        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response['body'],bytearray(b'Hello World!'))
        self.assertEqual(response['status'], 200)

        responder = alpha.reps.values()[0]
        self.assertTrue(responder.status.startswith, str(response['status']))
        self.assertEqual(responder.headers, response['headers'])

        alpha.servant.closeAll()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()

    def testValetServiceBottle(self):
        """
        Test Valet WSGI service request response
        """
        console.terse("{0}\n".format(self.testValetServiceBottle.__doc__))

        try:
            import bottle
        except ImportError as ex:
            console.terse("Bottle not available.\n")
            return

        store = storing.Store(stamp=0.0)

        app = bottle.default_app() # create bottle app

        @app.get('/echo')
        @app.get('/echo/<action>')
        @app.post('/echo')
        @app.post('/echo/<action>')
        def echoGet(action=None):
            """
            Echo back request data
            """
            query = dict(bottle.request.query.items())
            body = bottle.request.json
            raw = bottle.request.body.read()
            form = odict(bottle.request.forms)

            data = odict(verb=bottle.request.method,
                        url=bottle.request.url,
                        action=action,
                        query=query,
                        form=form,
                        content=body)
            return data


        console.terse("{0}\n".format("Building Valet ...\n"))
        wireLogAlpha = nonblocking.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = serving.Valet(port = 6101,
                              bufsize=131072,
                              wlog=wireLogAlpha,
                              store=store,
                              app=app)
        self.assertIs(alpha.servant.reopen(), True)
        self.assertEqual(alpha.servant.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.servant.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Patron ...\n"))
        wireLogBeta = nonblocking.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        path = "http://{0}:{1}/".format('localhost', alpha.servant.eha[1])

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     store=store,
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
                         ('headers', odict([('Accept', 'application/json'),
                                            ('Content-Length', 0)])),
                        ])

        beta.requests.append(request)
        timer = StoreTimer(store, duration=1.0)
        while (beta.requests or beta.connector.txes or not beta.responses or
               not alpha.idle()):
            alpha.serviceAll()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)
            store.advanceStamp(0.1)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)

        self.assertEqual(len(alpha.servant.ixes), 1)
        self.assertEqual(len(alpha.reqs), 1)
        self.assertEqual(len(alpha.reps), 1)
        requestant = alpha.reqs.values()[0]
        self.assertEqual(requestant.method, request['method'])
        self.assertEqual(requestant.url, request['path'])
        self.assertEqual(requestant.headers, {'accept': 'application/json',
                                                'accept-encoding': 'identity',
                                                'content-length': '0',
                                                'host': 'localhost:6101'})

        self.assertEqual(len(beta.responses), 1)
        response = beta.responses.popleft()
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['reason'], 'OK')
        self.assertEqual(response['body'],bytearray(b''))
        self.assertEqual(response['data'],{'action': None,
                                            'content': None,
                                            'form': {},
                                            'query': {'name': 'fame'},
                                            'url': 'http://localhost:6101/echo?name=fame',
                                            'verb': 'GET'},)

        responder = alpha.reps.values()[0]
        self.assertTrue(responder.status.startswith, str(response['status']))
        self.assertEqual(responder.headers, response['headers'])

        alpha.servant.closeAll()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()

    def testValetServiceBottleStream(self):
        """
        Test Valet WSGI service request response stream sse
        """
        console.terse("{0}\n".format(self.testValetServiceBottleStream.__doc__))

        try:
            import bottle
        except ImportError as ex:
            console.terse("Bottle not available.\n")
            return

        store = storing.Store(stamp=0.0)

        app = bottle.default_app() # create bottle app

        @app.get('/stream')
        def streamGet():
            """
            Create test server sent event stream that sends count events
            """
            timer = StoreTimer(store, duration=2.0)
            bottle.response.set_header('Content-Type',  'text/event-stream') #text
            bottle.response.set_header('Cache-Control',  'no-cache')
            # HTTP 1.1 servers detect text/event-stream and use Transfer-Encoding: chunked
            # Set client-side auto-reconnect timeout, ms.
            yield 'retry: 1000\n\n'
            i = 0
            yield 'id: {0}\n'.format(i)
            i += 1
            yield 'data: START\n\n'
            n = 1
            while not timer.expired:
                yield 'id: {0}\n'.format(i)
                i += 1
                yield 'data: {0}\n\n'.format(n)
                n += 1
            yield "data: END\n\n"

        console.terse("{0}\n".format("Building Valet ...\n"))
        wireLogAlpha = nonblocking.WireLog(buffify=True, same=True)
        result = wireLogAlpha.reopen()

        alpha = serving.Valet(port = 6101,
                              bufsize=131072,
                              wlog=wireLogAlpha,
                              store=store,
                              app=app)
        self.assertIs(alpha.servant.reopen(), True)
        self.assertEqual(alpha.servant.ha, ('0.0.0.0', 6101))
        self.assertEqual(alpha.servant.eha, ('127.0.0.1', 6101))

        console.terse("{0}\n".format("Building Patron ...\n"))
        wireLogBeta = nonblocking.WireLog(buffify=True,  same=True)
        result = wireLogBeta.reopen()

        path = "http://{0}:{1}/".format('localhost', alpha.servant.eha[1])

        beta = clienting.Patron(bufsize=131072,
                                     wlog=wireLogBeta,
                                     store=store,
                                     path=path,
                                     reconnectable=True,
                                     )

        self.assertIs(beta.connector.reopen(), True)
        self.assertIs(beta.connector.accepted, False)
        self.assertIs(beta.connector.connected, False)
        self.assertIs(beta.connector.cutoff, False)

        request = odict([('method', u'GET'),
                         ('path', u'/stream'),
                         ('qargs', odict()),
                         ('fragment', u''),
                         ('headers', odict([('Accept', 'application/json'),
                                            ('Content-Length', 0)])),
                         ('body', None),
                        ])

        beta.requests.append(request)
        timer = StoreTimer(store, duration=1.0)
        while (not timer.expired):
            alpha.serviceAll()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)
            store.advanceStamp(0.1)

        self.assertIs(beta.connector.accepted, True)
        self.assertIs(beta.connector.connected, True)
        self.assertIs(beta.connector.cutoff, False)

        self.assertEqual(len(alpha.servant.ixes), 1)
        self.assertEqual(len(alpha.reqs), 1)
        self.assertEqual(len(alpha.reps), 1)
        requestant = alpha.reqs.values()[0]
        self.assertEqual(requestant.method, request['method'])
        self.assertEqual(requestant.url, request['path'])
        self.assertEqual(requestant.headers, {'accept': 'application/json',
                                                'accept-encoding': 'identity',
                                                'content-length': '0',
                                                'host': 'localhost:6101'})


        #timed out while stream still open so no responses in .responses
        self.assertIs(beta.waited, True)
        self.assertIs(beta.respondent.ended, False)
        self.assertEqual(len(beta.responses), 0)
        self.assertIn('content-type', beta.respondent.headers)
        self.assertEqual(beta.respondent.headers['content-type'], 'text/event-stream')
        self.assertIn('transfer-encoding', beta.respondent.headers)
        self.assertEqual(beta.respondent.headers['transfer-encoding'], 'chunked')

        self.assertTrue(len(beta.events) >= 3)
        self.assertEqual(beta.respondent.retry, 1000)
        self.assertTrue(int(beta.respondent.leid) >= 2)
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '0', 'name': '', 'data': 'START'})
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '1', 'name': '', 'data': '1'})
        event = beta.events.popleft()
        self.assertEqual(event, {'id': '2', 'name': '', 'data': '2'})
        beta.events.clear()

        #keep going until ended
        timer.restart(duration=1.5)
        while (not timer.expired):
            alpha.serviceAll()
            time.sleep(0.05)
            beta.serviceAll()
            time.sleep(0.05)
            store.advanceStamp(0.1)

        self.assertTrue(len(beta.events) >= 3)
        self.assertEqual(beta.respondent.leid,  '9')
        self.assertEqual(beta.events[-2], {'id': '9', 'name': '', 'data': '9'})
        self.assertEqual(beta.events[-1], {'id': '9', 'name': '', 'data': 'END'})
        beta.events.clear()

        alpha.servant.closeAll()
        beta.connector.close()

        wireLogAlpha.close()
        wireLogBeta.close()


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
             'testPorterServiceEcho',
             'testValetServiceBasic',
             'testValetServiceBottle',
             'testValetServiceBottleStream',
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
