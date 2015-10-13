"""
Python 2 to 3 supporting definitions

"""
from __future__ import absolute_import, division, print_function

import sys

# Python2to3 support
if sys.version > '3':
    long = int
    basestring = (str, bytes)
    unicode = str
    xrange = range

    def ns2b(x):
        """
        Converts from native str type to native bytes type
        """
        return x.encode('ISO-8859-1')

    def ns2u(x):
        """
        Converts from native str type to native unicode type
        """
        return x

    def reraise(kind, value, trace=None):
        if value is None:
            value = kind()
        if value.__traceback__ is not trace:
            raise value.with_traceback(trace)
        raise value



else:
    #long = long
    #basestring = basestring
    #unicode = unicode

    def ns2b(x):
        """
        Converts from native str type to native bytes type
        """
        return x

    def ns2u(x):
        """
        Converts from native str type to native unicode type
        """
        return unicode(x)

    exec("""def reraise(kind, value, trace=None): raise kind, value, trace""", globals())
