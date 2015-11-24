"""interfacing.py  remote host interfacing module


"""
#print("module {0}".format(__name__))

#imports
import pickle
import pdb
import string
import math
import types
import os
import time
import copy
from collections import deque #double ended que, pronounced deck

from ..aid.sixing import *

from ..aid.consoling import getConsole
console = getConsole()

class NMEAParser(object):
    """NMEA Serial String Parser Object

       NMEA-0183

       Under the NMEA-0183 standard, all characters used are printable
       ASCII text (plus carriage return and line feed).  NMEA-0183 data
       is sent at 4800 baud.

       The data is transmitted in the form of "sentences".  Each
       sentence starts with a "$", a two letter "talker ID", a three
       letter "sentence ID", followed by a number of data fields
       separated by commas, and terminated by an optional checksum, and
       a carriage return/line feed.  A sentence may contain up to 82
       characters including the "$" and CR/LF.

       If data for a field is not available, the field is simply
       omitted, but the commas that would delimit it are still sent,
       with no space between them.

       Since some fields are variable width, or may be omitted as
       above, the receiver should locate desired data fields by
       counting commas, rather than by character position within the
       sentence.

       The optional checksum field consists of a "*" and two hex digits
       representing the exclusive OR of all characters between, but not
       including, the "$" and "*".  A checksum is required on some
       sentences.

       The standard allows individual manufacturers to define
       proprietary sentence formats.  These sentences start with "$P",
       then a 3 letter manufacturer ID, followed by whatever data the
       manufacturer wishes, following the general format of the
       standard sentences.

       Some common talker IDs are:
              GP      Global Positioning System receiver
              LC      Loran-C receiver
              OM      Omega Navigation receiver
              II      Integrated Instrumentation
                              (eg. AutoHelm Seatalk system)

    """

    def __init__(self):
        """Initialize instance   """
        pass

    def validate(self,sentence):
        """   Validates NMEA string and strips off leading $ and trailing optional
              checksum and linefeed if any

              If fails any test returns "" empty string
              Otherwise returns stripped string

              Tests:
                 length of string <= 82
                 first char is $
                 no more than one checksum indicator * exists
                 if checksum indicator
                    it is in correct position and valid

        """
        if len(sentence) > 82: #exceeds maximum length
            return ""

        if sentence[0] != '$':
            return "" #first char must be '$'

        sentence = sentence.rstrip() #clean off trailing whitspace including newline cr
        sentence = sentence[1:] #strip off leading '$'

        #use rpartition here should be simpler
        #does it have optional checksum?
        spot = sentence.rfind('*') #get offset from end to checksum indicator '*'
        lspot = sentence.find('*') #get offset from start to checksum indicator
        if spot != lspot: #more than one indicator '*' so invalid
            return ""

        if spot != -1:  #checksum exits, if not found, rfind returns -1
            if spot != len(sentence) - 3:# not at valid position for 2 byte checksum
                return ""
            else: #valid location so compute checksum
                sentence, given = sentence.rsplit('*') #strip off given check sum
                given= int(given,16) #convert to integer
                check = 0

                for c in sentence:
                    check += ord(c)
                    check %= 256

            if check != given:  #bad sum
                return ""

        return sentence

    def parse(self, sentence):
        """parse nemea sentence """

        chunks = sentence.split(',') #chunks are comma delimited

    def validateFile(self, fname):
        fp = open(fname,'r')
        valid = True
        fp.close()
