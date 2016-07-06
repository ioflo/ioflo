"""
vectoring.py basic vector functions

"""
from __future__ import absolute_import, division, print_function

import sys
import math


# Import ioflo libs
from .sixing import *


from .consoling import getConsole

console = getConsole()


def mag(v):
    """
    Returns the euclidean length or magnitude of vector v
    """
    return (pow(sum(e*e for e in v), 0.5))  # pow works for complex, math.sqrt does not

def mag2(v):
    """
    Returns the magnitude squared of vector v
    """
    return (sum(e*e for e in v))

def norm(v):
    """
    Returns normalized (euclidean norm) copy of vector v as list
    If v is zero vector then returns v as is
    """
    if not any(v):
        return v  # v is zero vector
    m = mag(v)
    return([e / m for e in v ])

def dot(u, v):
    """
    Returns dot product of vectors u and v
    """
    if len(u) != len(v):
        raise ValueError("Vectors lengths differ {} != {}".format(len(u),
                                                                  len(v)))
    return (sum(e*g for e, g in zip(u, v)))
