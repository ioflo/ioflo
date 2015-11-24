"""
checking.py utility functions for crc or chechsum type checking
"""
from __future__ import absolute_import, division, print_function

import sys
import os
import struct

# Import ioflo libs
from .sixing import *
from .consoling import getConsole

console = getConsole()


def crc16(inpkt):
    """ Returns 16 bit crc or inpkt packed binary string
        compatible with ANSI 709.1 and 852
        inpkt is bytes in python3 or str in python2
        needs struct module
    """
    inpkt = bytearray(inpkt)
    poly = 0x1021  # Generator Polynomial
    crc = 0xffff
    for element in inpkt :
        i = 0
        #byte = ord(element)
        byte = element
        while i < 8 :
            crcbit = 0x0
            if (crc & 0x8000):
                crcbit = 0x01
            databit = 0x0
            if (byte & 0x80):
                databit = 0x01
            crc = crc << 1
            crc = crc & 0xffff
            if (crcbit != databit):
                crc = crc ^ poly
            byte = byte << 1
            byte = byte & 0x00ff
            i += 1
    crc = crc ^ 0xffff
    return struct.pack("!H",crc )

def crc64(inpkt) :
    """ Returns 64 bit crc of inpkt binary packed string inpkt
        inpkt is bytes in python3 or str in python2
        returns tuple of two 32 bit numbers for top and bottom of 64 bit crc
    """
    inpkt = bytearray(inpkt)
    polytop = 0x42f0e1eb
    polybot = 0xa9ea3693
    crctop  = 0xffffffff
    crcbot  = 0xffffffff
    for element in inpkt :
        i = 0
        #byte = ord(element)
        byte = element
        while i < 8 :
            topbit = 0x0
            if (crctop & 0x80000000):
                topbit = 0x01
            databit = 0x0
            if (byte & 0x80):
                databit = 0x01
            crctop = crctop << 1
            crctop = crctop & 0xffffffff
            botbit = 0x0
            if (crcbot & 0x80000000):
                botbit = 0x01
            crctop = crctop | botbit
            crcbot = crcbot << 1
            crcbot = crcbot & 0xffffffff
            if (topbit != databit):
                crctop = crctop ^ polytop
                crcbot = crcbot ^ polybot
            byte = byte << 1
            byte = byte & 0x00ff
            i += 1
    crctop = crctop ^ 0xffffffff
    crcbot = crcbot ^ 0xffffffff
    return (crctop, crcbot)

