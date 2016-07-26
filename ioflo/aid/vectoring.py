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

def dot(u, v):
    """
    Returns dot product of vectors u and v
    """
    if len(u) != len(v):
        raise ValueError("Vectors lengths differ {} != {}".format(len(u),
                                                                  len(v)))
    return (sum(e*g for e, g in zip(u, v)))

def norm(v, check=False):
    """
    Returns normalized (euclidean norm) copy of vector v as list
    If v is zero vector then returns v as is

    For non zero v If check is True then and if mag != 1.0 repeat normalization once
    """
    if not any(v):
        return v  # v is zero vector
    m = mag(v)
    nv = tuple(e / m for e in v )
    if check:
        if mag(nv) != 1.0:
            nv = norm(nv, check=check)
    return (nv)

def perp2(u, v):
    """
    Returns the scalar 2D perpendicular product of vectors u and v.
    The convention is u perp v.
    The product is:
        positive if v is to the left of u, that is,
          the shortest rotation from u to v is ccw
        negative if v is to the right of u, that is,
          the shortest rotation from u to v is cw
        zero if v is colinear with u
    Essentially perp2 is the scalar 2D cross product
    """
    return (u[0] * v[1] - u[1] * v[0])

def ccw(u, v):
    """
    Returns True if v is to the left of u, that is,
          the shortest rotation from u to v is ccw
    False otherwise
    """
    return ((u[0] * v[1] - u[1] * v[0]) > 0)

left = ccw  # alias

def cw(u, v):
    """
    Returns True if v is to the right of u, that is,
          the shortest rotation from u to v is cw
    False otherwise
    """
    return ((u[0] * v[1] - u[1] * v[0]) < 0)

right = cw  #alias


def cross3(u, v):
    """
    Returns 3 tuple that is  the 3 dimentional vector cross product of
    3 vector u crossed onto 3 vector v
    """
    return ((u[1] * v[2] - v[1] * u[2],
             u[2] * v[0] - v[2] * u[0],
             u[0] * v[1] - v[0] * u[1]))
