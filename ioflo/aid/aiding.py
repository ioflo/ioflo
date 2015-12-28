"""
aiding.py miscellaneous utility functions

"""
from __future__ import absolute_import, division, print_function

import sys
import os
import re

# Import ioflo libs
from .sixing import *
from .consoling import getConsole

console = getConsole()

# For backwards compatibility. In the future import from .byting
from .byting import (binize, unbinize, hexize, unhexize, hexify, unhexify,
                     bytify, unbytify, packify, unpackify, packByte, unpackByte,
                     denary2BinaryStr, dec2BinStr, printHex, printDecimal)

# For backwards compatibility. In the future import from .eventing
from .eventing import tagify, eventify

# For backwards compatibility. In the future import from .checking
from .checking import crc16, crc64

# For backwards compatibility. In the future import from .filing
from .filing import ocfn, load, dump, loadPickle, dumpPickle, loadJson, dumpJson


def repack(n, seq, default=None):
    """ Repacks seq into a generator of len n and returns the generator.
        The purpose is to enable unpacking into n variables.
        The first n-1 elements of seq are returned as the first n-1 elements of the
        generator and any remaining elements are returned in a tuple as the
        last element of the generator
        default (None) is substituted for missing elements when len(seq) < n

        Example:

        x = (1, 2, 3, 4)
        tuple(repack(3, x))
        (1, 2, (3, 4))

        x = (1, 2, 3)
        tuple(repack(3, x))
        (1, 2, (3,))

        x = (1, 2)
        tuple(repack(3, x))
        (1, 2, ())

        x = (1, )
        tuple(repack(3, x))
        (1, None, ())

        x = ()
        tuple(repack(3, x))
        (None, None, ())

    """
    it = iter(seq)
    for _i in range(n - 1):
        yield next(it, default)
    yield tuple(it)

def just(n, seq, default=None):
    """ Returns a generator of just the first n elements of seq and substitutes
        default (None) for any missing elements. This guarantees that a generator of exactly
        n elements is returned. This is to enable unpacking into n varaibles

        Example:

        x = (1, 2, 3, 4)
        tuple(just(3, x))
        (1, 2, 3)
        x = (1, 2, 3)
        tuple(just(3, x))
        (1, 2, 3)
        x = (1, 2)
        tuple(just(3, x))
        (1, 2, None)
        x = (1, )
        tuple(just(3, x))
        (1, None, None)
        x = ()
        tuple(just(3, x))
        (None, None, None)

    """
    it = iter(seq)
    for _i in range(n):
        yield next(it, default)

def reverseCamel(name, lower=True):
    """ Returns camel case reverse of name.
        case change boundaries are the sections which are reversed.
        If lower is True then the initial letter in the reversed name is lower case

        Assumes name is of the correct format to be Python Identifier.
    """
    index = 0
    parts = [[]]
    letters = list(name) # list of the letters in the name
    for c in letters:
        if c.isupper(): #new part
            parts.append([])
            index += 1
        parts[index].append(c.lower())
    parts.reverse()
    parts = ["".join(part) for part in  parts]
    if lower: #camel case with initial lower
        name = "".join(parts[0:1] + [part.capitalize() for part in parts[1:]])
    else: #camel case with initial upper
        name = "".join([part.capitalize() for part in parts])
    return name

def nameToPath(name):
    """ Converts camel case name into full node path where uppercase letters denote
        intermediate nodes in path. Node path ends in dot '.'

        Assumes Name is of the correct format to be Identifier.
    """
    pathParts = []
    nameParts = list(name)
    for c in nameParts:
        if c.isupper():
            pathParts.append('.')
            pathParts.append(c.lower())
        else:
            pathParts.append(c)
    pathParts.append('.')
    path = ''.join(pathParts)
    return path

def isPath(s):
    """Returns True if string s is valid Store path name
       Returns False otherwise

       Faster to use precompiled versions in base

       raw string
       this also matches an empty string so need
       r'^([a-zA-Z_][a-zA-Z_0-9]*)?([.][a-zA-Z_][a-zA-Z_0-9]*)*$'

       at least either one of these
       r'^([a-zA-Z_][a-zA-Z_0-9]*)+([.][a-zA-Z_][a-zA-Z_0-9]*)*$'
       r'^([.][a-zA-Z_][a-zA-Z_0-9]*)+$'

       so get
       r'^([a-zA-Z_][a-zA-Z_0-9]*)+([.][a-zA-Z_][a-zA-Z_0-9]*)*$|^([.][a-zA-Z_][a-zA-Z_0-9]*)+$'

       shorthand replace [a-zA-Z_0-9] with  \w which is shorthand for [a-zA-Z_0-9]
       r'^([a-zA-Z_]\w*)+([.][a-zA-Z_]\w*)*$|^([.][a-zA-Z_]\w*)+$'

       ^ anchor to start
       $ anchor to end
       | must either match preceding or succeeding expression
       * repeat previous match zero or more times greedily
       ? repeat previous match zero or one times
       ( ) group
       [ ] char from set of ranges
       [a-zA-Z_] alpha or underscore one and only one
       [a-zA-Z_0-9]* alpha numeric or underscore (zero or more)
       ([a-zA-Z_][a-zA-Z_0-9]*) group made up of one alpha_ and zero or more alphanumeric_
       ([a-zA-Z_][a-zA-Z_0-9]*)? zero or one of the previous group

       ([.][a-zA-Z_][a-zA-Z_0-9]*) group made of one period one alpha_ and zero or more alphanumeric_
       ([.][a-zA-Z_][a-zA-Z_0-9]*)* zero or more of the previous group

       so what it matches.
       if first character is alpha_ then all remaining alphanumeric_ characters will
       match up to but not including first period if any

       from then on it will match groups that start with period one alpha_ and zero
       or more alphanumeric_ until the end

       valid forms
       a
       a1
       .a
       .a1

       a.b
       a1.b2
       .a1.b2
       .a.b

       but not
       .
       a.
       a..b
       ..a
       1.2

    """
    if re.match(r'^([a-zA-Z_]\w*)+([.][a-zA-Z_]\w*)*$|^([.][a-zA-Z_]\w*)+$',s):
        return True
    else:
        return False

def isIdentifier(s):
    """Returns True if string s is valid python identifier (variable, attribute etc)
       Returns False otherwise

       how to determine if string is valid python identifier

       r'^[a-zA-Z_]\w*$'
       r'^[a-zA-Z_][a-zA-Z_0-9]*$'  #equivalent \w is shorthand for [a-zA-Z_0-9]

       r' = raw string
       ^ = anchor to start
       [a-zA-Z_] = first char is letter or underscore
       [a-zA-Z_0-9] = next char is letter, underscore, or digit
       * = repeat previous character match greedily
       $ = anchor to end

       How
       import re
       reo = re.compile(r'^[a-zA-Z_]\w*$') #compile is faster
       if reo.match('_hello') is not None: #matched returns match object or None

       #re.match caches compiled pattern string compile so faster after first
       if re.match(r'^[a-zA-Z_]\w*$', '_hello')

       reo = re.compile(r'^[a-zA-Z_][a-zA-Z_0-9]*$')
       reo.match(

    """
    if re.match(r'^[a-zA-Z_]\w*$',s):
        return True
    else:
        return False

def isIdentPub(s):
    """Returns True if string s is valid python public identifier,
       that is, an identifier that does not start with an underscore
       Returns False otherwise
    """
    if re.match(r'^[a-zA-Z]\w*$',s):
        return True
    else:
        return False

