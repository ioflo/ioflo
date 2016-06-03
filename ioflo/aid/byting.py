"""
byting.py utility functions supporting byte, bit, hex conversion and packing

"""
from __future__ import absolute_import, division, print_function

import sys
import os
import struct
import string

# Import ioflo libs
from .sixing import *
from .odicting import odict

from .consoling import getConsole
console = getConsole()


def binize(n=0, size=8):
    """
    Returns the expanded binary unicode string equivalent of integer n,
    left zero padded using size number of bits

    example binize(11, 4) returns u'1011'
    """
    return "".join([str((n >> y) & 1) for y in range(size-1, -1, -1)])

def unbinize(u=u''):
    """
    Returns integer n equivalent of binary unicode string u

    example: unbinize(u'1011') returns 11
    """
    n = 0
    for bit in u:
        n <<= 1
        n |= 1 if int(bit) else 0
    return n

def hexize(b=b''):
    """
    Returns the expanded hex unicode string equivalent of the bytes string b
    Converts bytes string  b into the unicode hex format equivalent
    Where each byte in bytes b is expanded into the 2 charater hex
    equivalent
    """
    h = u''
    for i in range(len(b)):
        h += "{0:02x}".format(ord(b[i:i+1]))
    return h

def unhexize(h=u''):
    """
    Returns the packed bytes string version of the unicode hex string h
    Converts unicode string h in hex format into  bytes string by compressing
    every two hex characters into 1 byte that is the binary equivalent
    If h does not have an even number of characters then a 0 is first prepended to h

    """
    #remove any non hex characters, any char that is not in '0123456789ABCDEF'
    hh = h  # make copy so iteration not change
    for c in hh:
        if c not in string.hexdigits:
            h = h.replace(c,'') #delete characters

    if len(h) % 2: #odd number of characters
        h = u'0' + h #prepend a zero to make even number

    b = b''
    for i in xrange(0, len(h), 2):
        s = h[i:i+2]
        b = b + struct.pack('!B', int(s, 16))

    return b

def hexify(b=bytearray([])):
    """
    Returns the unicode string hex equivalent of the bytearray b
    Converts byte in b into into the two character unicode string hex equivalent
    """
    b = bytearray(b)  # just in case bytes
    h = u''
    for byte in b:
        h += "{0:02x}".format(byte)
    return h

def unhexify(h=u''):
    """
    Returns the packed binary bytearray equivalent of the unicode hex string h
    version of the string as bytes
    Where every two hex characters in h are compressed into one byte binary equivalent
    If h does not have an even number of characters then a '0' is first prependedto h
    """
    #remove any non hex characters, any char that is not in '0123456789ABCDEF'
    hh = h #make copy so iteration not change
    for c in hh:
        if c not in string.hexdigits:
            h = h.replace(c,'') #delete characters
    if len(h) % 2: #odd number of characters
        h = u'0' + h #prepend a zero to make even number
    b = bytearray([])
    for i in xrange(0, len(h), 2):
        s = h[i:i+2]
        b.append(int(s, 16))
    return b

def bytify(n=0, size=1, reverse=False, strict=False):
    """
    Returns bytearray of at least size bytes equivalent of integer n that is
    left zero padded to size bytes. For n positive, if the bytearray
    equivalent of n is longer than size  and strict is False the bytearray
    is extended to the length needed to fully represent n. Otherwise if strict
    is True or n is negative it is truncated to the least significant size bytes.

    Big endian is the default.
    If reverse is true then it reverses the order of the bytes in the resultant
    bytearray for little endian with right zero padding.
    """
    if n < 0 or strict:
        n =  n & (2 ** (size * 8) - 1)
    b = bytearray()
    count = 0
    while n:
        b.insert(0, n & 0xFF)
        count += 1
        n >>=  8
    if (count < size):
        b = bytearray([0]*(size-count)) + b
    if reverse:
        b.reverse()
    return b

def unbytify(b=bytearray([]), reverse=False):
    """
    Returns unsigned integer equivalent of bytearray b
    b may be any iterable of ints including bytes or list of ints.
    Big endian is the default.
    If reverse is true then it reverses the order of the bytes in the byte array
    before conversion for little endian.
    """
    b = bytearray(b)
    if not reverse:  # process MSB first on the right
        b.reverse()
    n = 0
    while b:
        n <<= 8
        n += b.pop()
    return n

def packify(fmt=u'8', fields=[0x00], size=None, reverse=False):
    """
    Packs fields sequence of bit fields into bytearray of size bytes using fmt string.
    Each white space separated field of fmt is the length of the associated bit field
    If not provided size is the least integer number of bytes that hold the fmt.
    If reverse is true reverse the order of the bytes in the byte array before
    returning. This is useful for converting between bigendian and littleendian.

    Assumes unsigned fields values.
    Assumes network big endian so first fields element is high order bits.
    Each field in format string is number of bits for the associated bit field
    Fields with length of 1 are treated as has having boolean truthy field values
       that is,   nonzero is True and packs as a 1
    for 2+ length bit fields the field element is truncated
    to the number of low order bits in the bit field
    if sum of number of bits in fmt less than size bytes then the last byte in
       the bytearray is right zero padded
    if sum of number of bits in fmt greater than size bytes returns exception
    to pad just use 0 value in source field.
    example
    packify("1 3 2 2", (True, 4, 0, 3)). returns bytearry([0xc3])
    """
    tbfl = sum((int(x) for x in fmt.split()))
    if size is None:
        size = (tbfl // 8) + 1 if tbfl % 8 else tbfl // 8

    if not (0 <= tbfl <= (size * 8)):
        raise ValueError("Total bit field lengths in fmt not in [0, {0}]".format(size * 8))

    n = 0
    bfp = 8 * size  # starting bit field position
    bu = 0  # bits used

    for i, bfmt in enumerate(fmt.split()):
        bits = 0x00
        bfl = int(bfmt)
        bu += bfl

        if bfl == 1:
            if fields[i]:
                bits = 0x01
            else:
                bits = 0x00
        else:
            bits = fields[i] & (2**bfl - 1)  # bit-and mask out high order bits

        bits <<= (bfp - bfl) #shift left to bit position less bit field size

        n |= bits  # bit-or in bits
        bfp -= bfl #adjust bit field position for next element

    return bytify(n=n, size=size, reverse=reverse, strict=True)

def packifyInto(b, fmt=u'8', fields=[0x00], size=None, offset=0, reverse=False):
    """
    Packs fields sequence of bit fields using fmt string into bytearray b
    starting at offset and packing into size bytes
    Each white space separated field of fmt is the length of the associated bit field
    If not provided size is the least integer number of bytes that hold the fmt.
    Extends the length of b to accomodate size after offset if not enough.
    Returns actual size of portion packed into.
    The default assumes big endian.
    If reverse is True then reverses the byte order before extending. Useful for
    little endian.

    Assumes unsigned fields values.
    Assumes network big endian so first fields element is high order bits.
    Each field in format string is number of bits for the associated bit field
    Fields with length of 1 are treated as has having boolean truthy field values
       that is,   nonzero is True and packs as a 1
    for 2+ length bit fields the field element is truncated
    to the number of low order bits in the bit field
    if sum of number of bits in fmt less than size bytes then the last byte in
       the bytearray is right zero padded
    if sum of number of bits in fmt greater than size bytes returns exception
    to pad just use 0 value in source field.
    example
    packify("1 3 2 2", (True, 4, 0, 3)). returns bytearry([0xc3])
    """
    tbfl = sum((int(x) for x in fmt.split()))
    if size is None:
        size = (tbfl // 8) + 1 if tbfl % 8 else tbfl // 8

    if not (0 <= tbfl <= (size * 8)):
        raise ValueError("Total bit field lengths in fmt not in [0, {0}]".format(size * 8))

    if len(b) < (offset + size):
        b.extend([0x00]*(offset + size - len(b)))

    n = 0
    bfp = 8 * size  # starting bit field position
    bu = 0  # bits used

    for i, bfmt in enumerate(fmt.split()):
        bits = 0x00
        bfl = int(bfmt)
        bu += bfl

        if bfl == 1:
            if fields[i]:
                bits = 0x01
            else:
                bits = 0x00
        else:
            bits = fields[i] & (2**bfl - 1)  # bit-and mask out high order bits

        bits <<= (bfp - bfl) #shift left to bit position less bit field size

        n |= bits  # bit-or in bits
        bfp -= bfl #adjust bit field position for next element

    bp = bytify(n=n, size=size, reverse=reverse, strict=True)

    b[offset:offset + len(bp)] = bp

    #count = 0
    #while n or (count < size):
        #b[offset + size - 1 - count] = n & 0xFF
        #count += 1
        #n >>=  8

    return size

def unpackify(fmt=u'1 1 1 1 1 1 1 1',
              b=bytearray([0x00]),
              boolean=False,
              size=None,
              reverse=False):
    """
    Returns tuple of unsigned int bit field values that are unpacked from the
    bytearray b according to fmt string. b maybe an integer iterator
    If not provided size is the least integer number of bytes that hold the fmt.
    The default assumes big endian.
    If reverse is True then reverse the byte order of b before unpackifing. This
    is useful for little endian.

    Each white space separated field of fmt is the length of the associated bit field.
    returns unsigned fields values.

    Assumes network big endian so first fmt is high order bits.
    Format string is number of bits per bit field
    If boolean parameter is True then return boolean values for
       bit fields of length 1

    if sum of number of bits in fmt less than 8 * size) then remaining
    bits are returned as additional field in result.

    if sum of number of bits in fmt greater 8 * len(b) returns exception

    example:
    unpackify(u"1 3 2 2", bytearray([0xc3]), False) returns (1, 4, 0, 3)
    unpackify(u"1 3 2 2", 0xc3, True) returns (True, 4, 0, 3)
    """
    b = bytearray(b)
    if reverse:
        b.reverse()

    tbfl = sum((int(x) for x in fmt.split()))
    if size is None:
        size = (tbfl // 8) + 1 if tbfl % 8 else tbfl // 8

    if not (0 <= tbfl <= (size * 8)):
        raise ValueError("Total bit field lengths in fmt not in [0, {0}]".format(size * 8))

    b = b[:size]
    fields = []  # list of bit fields
    bfp = 8 * size  # bit field position
    bu = 0  # bits used
    n = unbytify(b)  # unsigned int equivalent of b

    for i, bfmt in enumerate(fmt.split()):
        bfl = int(bfmt)
        bu += bfl

        mask = (2**bfl - 1) << (bfp - bfl)  # make mask
        bits = n & mask  # mask off other bits
        bits >>= (bfp - bfl)  # right shift to low order bits
        if bfl == 1 and boolean: #convert to boolean
            if bits:
                bits = True
            else:
                bits = False
        fields.append(bits) #assign to fields list
        bfp -= bfl #adjust bit field position for next element

    if bfp != 0:  # remaining bits
        bfl = bfp
        mask = (2**bfl - 1) # make mask
        bits = n & mask  # mask off other bits
        if bfl == 1 and boolean: #convert to boolean
            if bits:
                bits = True
            else:
                bits = False
        fields.append(bits) #assign to fields list
    return tuple(fields) #convert to tuple

def signExtend(x, n=8):
    """
    Returns signed integer that is the sign extention of n bit unsigned integer x
    in twos complement form where x has n significant bits

    This is useful when unpacking bit fields where the bit fields use two's complement
    to represent signed numbers. Assumes the the upper bits (above n) of x are zeros
    Works for both positive and negative x
    """
    m = 1 << (n-1)  # mask
    r = (x ^ m) - m
    return (r)

def packByte(fmt = b'8', fields = [0x00]):
    """Packs fields sequence into one byte using fmt string.

       Each fields element is a bit field and each
       char in fmt is the corresponding bit field length.
       Assumes unsigned fields values.
       Assumes network big endian so first fields element is high order bits.
       Format string is number of bits per bit field
       Fields with length of 1 are treated as has having boolean truthy field values
          that is,   nonzero is True and packs as a 1
       for 2-8 length bit fields the field element is truncated
       to the number of low order bits in the bit field
       if sum of number of bits in fmt less than 8 last bits are padded
       if sum of number of bits in fmt greater than 8 returns exception
       to pad just use 0 value in source field.
       example
       packByte("1322",(True,4,0,3)). returns 0xc3
    """
    fmt = bytes(fmt)
    byte = 0x00
    bfp = 8 #bit field position
    bu = 0 #bits used

    for i in range(len(fmt)):
        bits = 0x00
        bfl = int(fmt[i:i+1])  # slice returns bytes not byte so int works

        if not (0 < bfl <= 8):
            raise ValueError("Bit field length in fmt must be > 0 and <= 8")

        bu += bfl
        if bu > 8:
            raise ValueError("Sum of bit field lengths in fmt must be <= 8")

        if bfl == 1:
            if fields[i]:
                bits = 0x01
            else:
                bits = 0x00
        else:
            bits = fields[i] & (2**bfl - 1) #bit and to mask out high order bits

        bits <<= (bfp - bfl) #shift left to bit position less bit field size

        byte |= bits #or in bits
        bfp -= bfl #adjust bit field position for next element

    console.profuse("Packed byte = {0:#x}\n".format(byte))

    return byte

def unpackByte(fmt = b'11111111', byte = 0x00, boolean = True):
    """unpacks source byte into tuple of bit fields given by fmt string.

       Each char of fmt is a bit field length.
       returns unsigned fields values.
       Assumes network big endian so first fmt is high order bits.
       Format string is number of bits per bit field
       If boolean parameter is True then return boolean values for
          bit fields of length 1

       if sum of number of bits in fmt less than 8 then remaining
       bits returned as additional element in result.

       if sum of number of bits in fmt greater than 8 returns exception
       only low order byte of byte is used.

       example
       unpackByte("1322",0xc3, False ) returns (1,4,0,3)
       unpackByte("1322",0xc3, True ) returns (True,4,0,3)
    """
    fmt = bytes(fmt)
    fields = [] #list of bit fields
    bfp = 8 #bit field position
    bu = 0 #bits used
    byte &= 0xff #get low order byte

    for i in range(len(fmt)):
        bfl = int(fmt[i:i+1])  # slice returns bytes not byte so int works

        if not (0 < bfl <= 8):
            raise ValueError("Bit field length in fmt must be > 0 and <= 8")

        bu += bfl
        if bu > 8:
            raise ValueError("Sum of bit field lengths in fmt must be <= 8")

        mask = (2**bfl - 1) << (bfp - bfl) #make mask
        bits = byte & mask #mask off other bits
        bits >>= (bfp - bfl) #right shift to low order bits
        if bfl == 1 and boolean: #convert to boolean
            if bits:
                bits = True
            else:
                bits = False

        fields.append(bits) #assign to fields list

        bfp -= bfl #adjust bit field position for next element

    return tuple(fields) #convert to tuple

def denary2BinaryStr(n, l=8):
    """
    Convert denary integer n to binary string bs, left pad to length l
    """
    bs = ''
    if n < 0:  raise ValueError("must be a positive integer")
    if n == 0: return '0'
    while n > 0:
        bs = str(n % 2) + bs
        n = n >> 1
    return bs.rjust(l,'0')

def dec2BinStr(n, count=24):
    """ returns the binary formated string of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

def printHex(s, chunk = 0, chunks = 0, silent = False, separator = '.'):
    """prints elements of bytes string s in hex notation.

       chunk is number of bytes per chunk
       0 means no chunking
       chunks is the number of chunks per line
       0 means no new lines

       silent = True means return formatted string but do not print
    """
    if (chunk < 0):
        raise ValueError("invalid size of chunk")

    if (chunks < 0):
        raise ValueError("invalid chunks per line")

    slen = len(s)

    if chunk == 0:
        chunk = slen

    if chunks == 0:
        line = slen
    else:
        line = chunk * chunks

    cc = 0
    ps = ''
    for i in range(len(s)):
        ps += ("%02x" % ord(s[i:i+1]))
        #add space or dot if not end of line or end of string
        if ((i + 1) % line) and ((i+1) % slen):
            if not ((i + 1) % chunk): #end of chunk
                ps += ' ' #space between chunks
            else:
                ps += separator #between bytes in chunk
        elif (i + 1) != slen: # newline if not last line
            ps += '\n' #newline

    if not silent:
        console.terse("{0}\n".format(ps))

    return ps

def printDecimal(s):
    """prints elements of string s in decimal notation.

    """
    ps = ''
    for i in range(len(s)):
        ps = ps + ("%03d." % ord(s[i:i+1]))
    ps = ps[0:-1] #strip trailing .
    print(ps)


