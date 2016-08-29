"""
vectoring.py basic vector functions

"""
from __future__ import absolute_import, division, print_function

import sys
import math
from collections import namedtuple

# Import ioflo libs
from .sixing import *

from ..base.globaling import Pxy, Pxyz, Pne, Pned,  Pfs,  Pfsb  # namedtuple points

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

def neg(v):
    """
    Returns the negative of v
    """
    return tuple(-e for e in v)

def mult(k, v):
    """
    Returns the vector result of multipling scalar k with vector v
    """
    return tuple(k*e for e in v)

def add(u, v):
    """
    Returns the vector addition of vectors u + v
    """
    if len(u) != len(v):
        raise ValueError("Vectors lengths differ {} != {}".format(len(u),
                                                                  len(v)))
    return tuple(e + g for e, g in zip(u, v))

def sub(u, v):
    """
    Returns the vector subtraction of vectors u - v
    """
    if len(u) != len(v):
        raise ValueError("Vectors lengths differ {} != {}".format(len(u),
                                                                  len(v)))
    return tuple(e - g for e, g in zip(u, v))

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
    Returns normalized (euclidean norm) copy of vector v as tuple
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

def proj(u, v):
    """
    Returns the vector projection of u onto v, u proj v
    """
    w = norm(v)
    return (mult(dot(u, w), w))

def trip(u, v):
    """
    Returns the scalar triple product of vectors u and v and z axis.
    The convention is z dot (u cross v). Dotting with the z axis simplifies
    it to the z component of the u cross v
    The product is:
        positive if v is to the left of u, that is,
          the shortest right hand rotation from u to v is ccw
        negative if v is to the right of u, that is,
          the shortest right hand rotation from u to v is cw
        zero if v is colinear with u
    Essentially trip is the z component of the cross product of u x v
    """
    return (u[0] * v[1] - u[1] * v[0])

def ccw(u, v):
    """
    Returns True if v is to the left of u, that is,
          the shortest rotation from u to v is ccw, turn left
    False otherwise
    """
    return ((u[0] * v[1] - u[1] * v[0]) > 0)

left = ccw  # alias

def cw(u, v):
    """
    Returns True if v is to the right of u, that is,
          the shortest rotation from u to v is cw, turn right
    False otherwise
    """
    return ((u[0] * v[1] - u[1] * v[0]) < 0)

right = cw  #alias

def tween(p, u, v):
    """
    Returns true if point p is on the line from u to v, ie is between u and v
    """
    # treat u as the origin and create vectors a=up b=uv
    a = sub(p, u)
    b = sub(v, u)

    if a == b:  # endpoint same
        return True

    daa = dot(a, a)
    if daa == 0:  # p equals u so on line segment
        return True

    dbb = dot(b, b)
    if dbb == 0: # empty line segment
        if a == b:  # point on line only if same point
            return True
        else:  # point not on line
            return False

    dab = dot(a, b)
    if dab < 0:  # not on segment before
        return False

    if dab > dbb:  # not on segment after
        return False

    # collinear if ka=b
    # colinear is scalars all the same so any scale should work
    k = 0
    for e, g in zip(a, b):
        if e == 0:
            if g != 0:
                return False
            else:
                continue
        k = g / e
        break

    if k == 0:
        return False

    if mult(k, a) != b:
        return False

    return True

def tween2(p, u, v):
    """
    Returns true if 2d point p is on the line from 2d points u to v,
    ie is between u and v
    """
    # treat u as the origin and create vectors a=up b=uv
    a = sub(p, u)
    b = sub(v, u)

    dbb = dot(b, b)
    if dbb == 0: # empty line segment
        if a == b:  # point on line only if same point
            return True
        else:  # point not on line
            return False

    dab = dot(a, b)
    if dab < 0:
        return False  # before not between
    if dab > mag2(b):
        return False  # past not between
    if trip(a, b) != 0:  # not colinear
        return False
    return True

def cross3(u, v):
    """
    Returns 3 tuple that is  the 3 dimentional vector cross product of
    3 vector u crossed onto 3 vector v
    """
    return ((u[1] * v[2] - v[1] * u[2],
             u[2] * v[0] - v[2] * u[0],
             u[0] * v[1] - v[0] * u[1]))


def wind(p, vs):
    """
    Returns integer winding number of 2D point-in-polygon test for point p in
    the closed polygon whose sides are formed by connecting the vertex points
    in sequence vs where each element of vs is a point.
    Points are 2D sequences (tuples, namedtuples, lists etc)

    If the winding number is zero then p is not inside the polygon.
    If the winding number is positive then p is inside and the polygon is
      wound counter clockwise around p
    If the winding number is negative then p is inside and the polygon is
      wound clockwise around p



    Modified version of algorithm from Dan Sunday
    http://geomalgorithms.com/a03-_inclusion.html
    The Sunday algorithm does not handle the case consistently where p is on a vertex
    This modified algorithm accounts for p on edge (vertex or side) as outside
    Because P on the edge could be either inside or outside arbitrarily but there
    is not good way to determine winding direction in that case it is considered outside
    Algorithm checks for p as a vertex or side and returns w=0

    To determine which side of the infinite line directed from
    A=(x1,y1) to B=(x2,y2), a point P=(x,y) falls on
    compute the value:
    d=(x−x1)(y2−y1)−(y−y1)(x2−x1)

    u[0] * v[1] - u[1] * v[0]

    If d<0  then the point lies on one side of the line,
    If d>0 then it lies on the other side.
    If d=0 then the point lies exactly on the line.
    d is a version of the scalar triple product for the xy plane
    d is the z component of AB x AP

    """
    if p in vs:  # if on a vertex can't tell winding direction so outside
        return 0

    px, py = p[:2]
    w = 0  # winding number
    l = len(vs) # number of vertices
    for i in range(l):
        j = (i + 1) % l  # wrap around next vertex
        if tween2(p, vs[i], vs[j]):  # on side so outside
            return 0
        x, y = vs[i][:2]  # current vertex elements
        u, v = vs[j][:2]  # next vertex elements

        if y <= py:  # segment starts below ray level with x
            if v > py:  # segment ends above ray level with x = upward crossing
                # vertex vs[i] is origin, create vectors to p and vs[j]
                # compute if point is to the left of line segment by turn of vector
                if right(sub(p, vs[i]), sub(vs[j], vs[i])):  # turn right = is left
                    w += 1
        else:  # segment starts above ray level with x
            if v <= py: # segment ends below ray level with x = downward crossing
                # vertex vs[i] is origin, create vectors to p  and vs[j]
                # compute if point is to the right of line segment by turn of vector
                if left(sub(p, vs[i]), sub(vs[j], vs[i])):  # turn left = is right
                    w -= 1
    return (w)


def inside(p, vs):
    """
    Returns True if 2D point p satisfies point-in-polygon test for the
    the closed polygon whose sides are formed by connecting the vertex points
    in sequence vs where each element of vs is a point.
    Points are 2D sequences (tuples, namedtuples, lists etc)

    If p is on a vertex or edge of polygon it is considered outside
    """
    return False if wind(p, vs) == 0 else True
