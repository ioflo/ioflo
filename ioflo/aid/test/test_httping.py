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

        hc.close()

    def testNonBlocking(self):
        """
        Test NonBlocking Http client
        """
        console.terse("{0}\n".format(self.testBasic.__doc__))

        console.terse("{0}\n".format("Connecting ...\n"))
        hc = HTTPConnection('127.0.0.1', port=8080, timeout=1.0)

        hc.connect()


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
    names = ['testBasic', ]
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

    runOne('testBasic')

