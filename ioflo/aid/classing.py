"""
meta class and base class utility classes and functions

"""
from __future__ import absolute_import, division, print_function

from collections import Iterable, Sequence
from abc import ABCMeta

# import ioflo modules
from .sixing import *

from .consoling import getConsole
console = getConsole()


def metaclassify(metaclass):
    """
    Class decorator for creating a class with a metaclass.
    This enables the same syntax to work in both python2 and python3
    python3 does not support
        class name(object):
            __metaclass__ mymetaclass
    python2 does not support
        class name(metaclass=mymetaclass):

    Borrowed from six.py add_metaclass decorator

    Usage:
    @metaclassify(Meta)
    class MyClass(object):
        pass
    That code produces a class equivalent to:

    on Python 3
    class MyClass(object, metaclass=Meta):
        pass

    on Python 2
    class MyClass(object):
        __metaclass__ = MyMeta
    """
    def wrapper(cls):
        originals = cls.__dict__.copy()
        originals.pop('__dict__', None)
        originals.pop('__weakref__', None)
        for slots_var in originals.get('__slots__', ()):
            originals.pop(slots_var)
        return metaclass(cls.__name__, cls.__bases__, originals)
    return wrapper

@metaclassify(ABCMeta)
class NonStringIterable:
    """ Allows isinstance check for iterable that is not a string
    """
    #__metaclass__ = ABCMeta

    @classmethod
    def __subclasshook__(cls, C):
        if cls is NonStringIterable:
            if (not issubclass(C, basestring) and issubclass(C, Iterable)):
                return True
        return NotImplemented

@metaclassify(ABCMeta)
class NonStringSequence:
    """ Allows isinstance check for sequence that is not a string
    """
    #__metaclass__ = ABCMeta

    @classmethod
    def __subclasshook__(cls, C):
        if cls is NonStringSequence:
            if (not issubclass(C, basestring) and issubclass(C, Sequence)):
                return True
        return NotImplemented

def nonStringIterable(obj):
    """
    Returns True if obj is non-string iterable, False otherwise

    Future proof way that is compatible with both Python3 and Python2 to check
    for non string iterables.
    Assumes in Python3 that, basestring = (str, bytes)

    Faster way that is less future proof
    return (hasattr(x, '__iter__') and not isinstance(x, basestring))
    """
    return (not isinstance(obj, basestring) and isinstance(obj, Iterable))

def nonStringSequence(obj):
    """
    Returns True if obj is non-string sequence, False otherwise

    Future proof way that is compatible with both Python3 and Python2 to check
    for non string sequences.
    Assumes in Python3 that, basestring = (str, bytes)
    """
    return (not isinstance(obj, basestring) and isinstance(obj, Sequence) )

