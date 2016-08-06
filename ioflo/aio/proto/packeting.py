"""
Packet Base Class Package

"""
from __future__ import absolute_import, division, print_function

import struct
from binascii import hexlify
from collections import deque, namedtuple
import enum

from ...aid.sixing import *
from ...aid.odicting import odict
from ...aid.byting import bytify, unbytify, packify, packifyInto, unpackify
from ...aid import getConsole
from .protoing import MixIn

console = getConsole()



class Part(MixIn):
    """
    Base class for packet part classes with .packed .size and len
    """
    Size = 0

    def __init__(self, size=None, packed=None, **kwa):
        """
        Initialization method for instance.

        Parameters:
            size is initial size of .packed if packed not provided
            packed is initial .packed

        Attributes:
            .packed is bytearray of packed binary data

        Properties:
            .size is length of .packed

        """
        super(Part, self).__init__(**kwa)

        if packed is None:
            size = size if size is not None else self.Size
            self.packed = bytearray([0 for i in range(0, size)])
        else:
            self.packed = bytearray(packed)

    def __len__(self):
        """
        Returns the length of .packed
        """
        return len(self.packed)

    @property
    def size(self):
        """
        Property size
        """
        return self.__len__()

    def show(self):
        """
        Returns descriptive string for display purposes
        """
        name = self.__class__.__name__
        result = ("    {0}: packed=0x{1}\n".format(name,
                                        hexlify(self.packed).decode('ascii')))
        return result


class PackerPart(Part):
    """
    Base class for packet packer part classes with .packer and .fmt
    .fmt is the struct string format for the fixed size portion of part
    """
    Format = '!'  # default empty packer struct format string for packed

    def __init__(self, fmt=None, raw=None, **kwa):
        """
        Initialization method for instance.

        Inherited Parameters:
            size is initial size of .packed

        Parameters:
            fmt is struct format string to pack into .packed
            raw is input bytearray of data to parse(unpack)

        Inherited Attributes:
            .packed is bytearray of packed binary data using .packer

        Attributes:
            .fmt is struct format string
            .packer is compiled struct packer
            
        Class Attributes:
            .Format is struct packer format string for packed

        Inherited Properties:
            .size is length of .packed

        """
        self.fmt = fmt if fmt is not None else self.Format
        self.packer = struct.Struct(self.fmt) #precompile struct for packing unpacking
        kwa['size'] = self.packer.size  # override size to match .packer.size
        super(PackerPart, self).__init__(**kwa)

        if raw is not None:
            self.parse(raw=raw)

    def verifySize(self, raw=bytearray(b'')):
        """
        Return True if len(raw) is at least long enough for packed size
        """
        return (len(raw) >= (self.packer.size))

    def parse(self, raw):
        """Parse raw bytearray and assign to fields
           Return offset into raw of unparsed portion
           Base method to be overridden in subclass
        """
        if (raw is None) or (not self.verifySize(raw)):
            raise ValueError("Parse Packer: Not enough raw data for packer. "
                             "Need {0} bytes, got {1} bytes.".format(self.size,
                                                                     len(raw)))

        result = self.packer.unpack_from(raw)  # result should be empty tuple
        self.packed[:] = raw[0:self.packer.size]

        return self.size #return offset to start of unparsed portion of data

    def pack(self, **kwa):
        """
        Return .packed with data if any
        Base method to be overridden in sub class
        """

        self.packer.pack_into(self.packed, 0)  # empty

        if self.size != self.packer.size :
            raise ValueError("Build Packer: size packed={0} not match "
                             "format={1}".format(self.size, self.packer.size))
        return self.packed


class PackifierPart(Part):
    """
    Base class for packet packifier part classes with packify .fmt
    .fmt is the packify string format for the fixed size portion of part
    packify allows bit field packing
    """
    Format = ''  # default packer struct format string for packed

    def __init__(self, fmt=None, raw=None, **kwa):
        """
        Initialization method for instance.

        Inherited Parameters:
            size is initial size of .packed

        Parameters:
            fmt is packify format string to pack into .packed
            raw is input bytearray of data to parse(unpack)

        Inherited Attributes:
            .packed is bytearray of packed binary data

        Attributes:
            .fmt is packify format string
            .fmtSize is size given by format string

        Inherited Properties:
            .size is length of .packed
            
        Properties
            .fmtSize is size given by .fmt

        """
        self.fmt = fmt if fmt is not None else self.Format
        kwa['size'] = self.fmtSize  # override size to match packify size of whole bytes
        super(PackifierPart, self).__init__(**kwa)

        if raw is not None:
            self.parse(raw=raw)
            
    @property
    def fmtSize(self):
        """
        Property fmtSize
        """
        tbfl = sum((int(x) for x in self.fmt.split()))
        size = (tbfl // 8) + 1 if tbfl % 8 else tbfl // 8        
        return size
    
    def verifySize(self, raw=bytearray(b'')):
        """
        Return True if len(raw) is at least long enough for packed size
        """
        return (len(raw) >= (self.fmtSize))

    def parse(self, raw):
        """Parse raw bytearray and assign to fields
           Return offset into raw of unparsed portion
           Base method to be overridden in subclass
        """
        if (not raw) or (not self.verifySize(raw)):
            raise ValueError("Parse Packifier: Not enough raw data for packifier. "
                             "Need {0} bytes, got {1} bytes.".format(self.size,
                                                                     len(raw)))

        result = unpackify(self.fmt, raw, boolean=True, size=self.fmtSize)  # empty result
        self.packed[:] = raw[0:self.size]

        return self.size #return offset to start of unparsed portion of data

    def pack(self, **kwa):
        """
        Return .packed with data if any
        Base method to be overridden in sub class
        """
        size = packifyInto(self.packed, fmt=self.fmt, fields=())

        if self.size != size :
            raise ValueError("Build Packifier: size packed={0} not match "
                             "format={1}".format(self.size, size))
        return self.packed

    def show(self):
        """
        Returns descriptive string for display purposes
        """
        name = self.__class__.__name__
        result = ("    {0}: packed=0x{1}\n".format(name,
                                        hexlify(self.packed).decode('ascii')))
        return result


class PacketPart(Part):
    """
    PacketPart base class for parts of packets.
    Allows PacketPart to reference other parts of its Packet
    """

    def __init__(self, packet=None, **kwa):
        """
        Initialization method for instance.
        Base class method to be overridden in subclass
        Need to add parts to packet in subclass

        Inherited Parameters:
            size is initial size of .packed

        Parameters:
            packet is Packet instance that holds this part

        Inherited Attributes:
            .packed is bytearray of packed binary data

        Attributes:
            .packet is Packet instance that holds this part

        Properties:
            .size is length of .packed

        """
        self.packet = packet  # do this first  in case mixin needs attribute
        super(PacketPart, self).__init__(**kwa)
        

    def show(self):
        """
        Returns descriptive string for display purposes
        """
        name = self.__class__.__name__
        result = ("    {0}: packed=0x{1}\n".format(name,
                                        hexlify(self.packed).decode('ascii')))
        return result


class Packet(Part):
    """
    Packet base class
    Allows packet to reference its stack
    """

    def __init__(self, stack=None, **kwa):
        """
        Initialization method for instance.
        Base class method to be overridden in subclass
        Need to add parts to packet in subclass

        Inherited Parameters:
            size is initial size of .packed

        Parameters:
            stack is I/O stack that handles this packet

        Inherited Attributes:
            .packed is bytearray of packed binary data

        Attributes:
            .stack is I/O stack that handles this packet

        Inherited Properties:
            .size is length of .packed


        """
        super(Packet, self).__init__(**kwa)
        self.stack = stack


    def parse(self, raw):
        """
        Parse raw data into .packed
        """
        return self.size

    def pack(self):
        """
        Pack into .packed
        """
        return self.packed

