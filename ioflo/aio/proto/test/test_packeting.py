# -*- coding: utf-8 -*-
"""
Unittests
"""
from __future__ import absolute_import, division, print_function

import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os

from binascii import hexlify

# Import ioflo libs
from ioflo.aid.sixing import *
from ioflo.aid.byting import hexify, bytify, unbytify, packify, unpackify
from ioflo.aid import getConsole

console = getConsole()

from ioflo.aio.proto import packeting

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
        console.reinit(verbosity=console.Wordage.profuse)

    def tearDown(self):
        """

        """
        console.reinit(verbosity=console.Wordage.concise)

    def testPart(self):
        """
        Test Part class
        """
        console.terse("{0}\n".format(self.testPart.__doc__))

        part = packeting.Part()
        self.assertEqual(part.size, 0)
        self.assertEqual(part.size, len(part))
        self.assertEqual(part.packed, bytearray([]))

        part = packeting.Part(size=2)
        self.assertEqual(part.size, 2)
        self.assertEqual(part.size, len(part))
        self.assertEqual(part.packed, bytearray([0, 0]))

        packed = bytearray([0, 1, 2, 3])
        part = packeting.Part(size=2, packed=packed)
        self.assertEqual(part.size, 4)
        self.assertEqual(part.size, len(packed))
        self.assertEqual(part.size, len(part))
        self.assertEqual(part.packed, packed)

    def testPackerPart(self):
        """
        Test PackerPart class
        """
        console.terse("{0}\n".format(self.testPackerPart.__doc__))

        part = packeting.PackerPart()
        self.assertEqual(part.fmt, '!')
        self.assertTrue(part.packer)
        self.assertEqual(part.size, 0)
        self.assertEqual(part.size, len(part))
        self.assertEqual(part.size, part.packer.size)
        self.assertEqual(part.packed, bytearray([]))
        show = part.show()
        self.assertEqual(show, '    PackerPart: packed=0x\n')

        packed = part.pack()
        self.assertEqual(packed, part.packed)
        self.assertEqual(part.packed, bytearray([]))
        show = part.show()
        self.assertEqual(show, '    PackerPart: packed=0x\n')

        raw = bytearray()
        offset = part.parse(raw=raw)
        self.assertEqual(offset, part.size)
        self.assertEqual(offset, 0)
        self.assertEqual(part.packed, bytearray([]))
        show = part.show()
        self.assertEqual(show, '    PackerPart: packed=0x\n')

        raw = bytearray([7, 2, 1, 0])
        offset = part.parse(raw=raw)
        self.assertEqual(offset, part.size)
        self.assertEqual(offset, 0)
        self.assertEqual(part.packed, bytearray([]))
        show = part.show()
        self.assertEqual(show, '    PackerPart: packed=0x\n')

        part = packeting.PackerPart(fmt="!BBB")
        self.assertEqual(part.fmt, '!BBB')
        self.assertTrue(part.packer)
        self.assertEqual(part.size, 3)
        self.assertEqual(part.size, len(part))
        self.assertEqual(part.size, part.packer.size)
        self.assertEqual(part.packed, bytearray([0, 0, 0]))
        show = part.show()
        self.assertEqual(show, '    PackerPart: packed=0x000000\n')

    def testPackifierPart(self):
        """
        Test PackifierPart class
        """
        console.terse("{0}\n".format(self.testPackifierPart.__doc__))

        part = packeting.PackifierPart()
        self.assertEqual(part.fmt, '')
        self.assertEqual(part.size, 0)
        self.assertEqual(part.size, len(part))
        self.assertEqual(part.packed, bytearray([]))
        show = part.show()
        self.assertEqual(show, '    PackifierPart: packed=0x\n')

        packed = part.pack()
        self.assertEqual(packed, part.packed)
        self.assertEqual(part.packed, bytearray([]))
        show = part.show()
        self.assertEqual(show, '    PackifierPart: packed=0x\n')

        raw = bytearray([7, 2, 1, 0])
        offset = part.parse(raw=raw)
        self.assertEqual(offset, part.size)
        self.assertEqual(offset, 0)
        self.assertEqual(part.packed, bytearray([]))
        show = part.show()
        self.assertEqual(show, '    PackifierPart: packed=0x\n')

        part = packeting.PackifierPart(fmt="8 8 8")
        self.assertEqual(part.fmt, "8 8 8")
        self.assertEqual(part.fmtSize, 3)
        self.assertEqual(part.size, 3)
        self.assertEqual(part.size, len(part))
        self.assertEqual(part.fmtSize, part.size)
        self.assertEqual(part.packed, bytearray([0, 0, 0]))
        show = part.show()
        self.assertEqual(show, '    PackifierPart: packed=0x000000\n')

    def testPacketPart(self):
        """
        Test PacketPart class
        """
        console.terse("{0}\n".format(self.testPacketPart.__doc__))

        part = packeting.PacketPart()
        self.assertEqual(part.packet, None)
        self.assertEqual(part.size, 0)
        self.assertEqual(part.size, len(part))
        self.assertEqual(part.packed, bytearray([]))
        show = part.show()
        self.assertEqual(show, '    PacketPart: packed=0x\n')

        part = packeting.PacketPart(packet="Not a packet")
        self.assertEqual(part.packet, "Not a packet")


    def testPacket(self):
        """
        Test Packet class
        """
        console.terse("{0}\n".format(self.testPacket.__doc__))

        part = packeting.Packet()
        self.assertEqual(part.stack, None)
        self.assertEqual(part.size, 0)
        self.assertEqual(part.size, len(part))
        self.assertEqual(part.packed, bytearray([]))

        part = packeting.Packet(stack="Not a stack")
        self.assertEqual(part.stack, "Not a stack")


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
             'testPart',
             'testPackerPart',
             'testPackifierPart',
             'testPacketPart',
             'testPacket',
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

    #runAll() #run all unittests

    runSome()#only run some

    #runOne('testPart')



