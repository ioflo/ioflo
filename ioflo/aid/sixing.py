"""
Python 2 to 3 supporting definitions

"""
#print("module {0}".format(__name__))

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

