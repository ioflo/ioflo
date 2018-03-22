"""aiding.py constants and basic functions

"""
from __future__ import absolute_import, division, print_function

import math

# Import ioflo libs
from .sixing import *
from ..base import excepting

from .consoling import getConsole
console = getConsole()


def blend0(d=0.0, u=1.0, s=1.0):
    """
       blending function trapezoid
       d = delta x = xabs - xdr
       u = uncertainty radius of xabs estimate error
       s = tuning scale factor

       returns blend
    """
    d = float(abs(d))
    u = float(abs(u))
    s = float(abs(s))
    v = d - u #offset by radius

    if v >= s:  #first so if s == 0 catches here so no divide by zero below
        b = 0.0
    elif v <= 0.0:
        b = 1.0
    else: # 0 < v < s
        b = 1.0 - (v / s)

    return b

Blend0 = blend0


def blend1(d=0.0, u=1.0, s=1.0):
    """
       blending function pisig
       d = delta x = xabs - xdr
       u = uncertainty radius of xabs estimate error
       s = tuning scale factor

       returns blend
    """
    v = float(abs(u * s)) #scale uncertainty radius make sure positive
    a = float(abs(d)) #symmetric about origin

    if a >= v or v == 0.0 : #outside uncertainty radius accept delta
        b = 1.0
    elif a < v/2.0: # inside 1/2 uncertainty radius closer to 0
        b = 2.0 * (a * a)/(v * v)
    else: #greater than 1/2 uncertainty radius closer to 1
        b = 1.0 - (2.0 * (a - v) * (a - v))/ (v * v)

    return b

Blend1 = blend1


def blend2(d=0.0, u=1.0, s=5.0):
    """
       blending function gaussian
       d = delta x = xabs - xdr
       u = uncertainty radius of xabs estimate error
       s = tuning scale factor

       returns blend
    """
    d = float(d)
    u = float(u)
    s = float(abs(s)) # make sure positive

    b = 1.0 - math.exp( - s * (d * d)/(u * u))

    return b

Blend2 = blend2


def blend3(d=0.0, u=1.0, s=0.05):
    """
       blending function polynomial
       d = delta x = xabs - xdr
       u = uncertainty radius of xabs estimate error
       s = tuning scale factor

       returns blend
    """
    d = float(d)
    u = float(u)
    s = min(1.0,float(abs(s))) # make sure positive <= 1.0

    b = 1.0 - s ** ((d * d)/(u * u))

    return b

Blend3 = blend3


def blendConcaveInc(d=0.0, u=1.0, s=1.0, h=1.0):
    d = float(d)
    u = float(u)
    s = float(s)
    
    m = (2 * s - u - d) 
    if m == 0:
        return h
    
    if d >= s:
        return h
    else:
        b = h * (s - u) / (2 * s - u - d)    
    
    return b

BlendConcaveInc = blendConcaveInc


def blendConcaveDec(d=0.0, u=2.0, s=1.0, h=1.0):
    d = float(d) 
    u = float(u)
    s = float(s)
    
    m = (u - 2 * s + d) 
    if m == 0:
        return h
    
    if d <= s:
        return h
    else:
        b = (h * (u - s)) / (u - 2 * s + d)    
    
    return b

BlendConcaveDec = blendConcaveDec


def blendCauchian(d=0.0, a=1.0, b=0.0, c=2.0, h=1.0):
    """
       blending function polynomial
       d = x value
       a = area under curve/uncertainty radius
       b = horizontal shift
       c = curvature of function/tuning scale factor
       h = height of the set

       returns blend
    """
    d = float(d)
    a = float(a)
    b = float(b)
    c = float(c)
    h = float(h)

    if a == 0:
        raise ValueError("Param a must be a non zero value.")

    return h / (1 + math.pow(abs((d-b)/a), 2*c))

BlendCauchian = blendCauchian


def blendCosine(d=0.0, a=0.166666667, b=0.0, h=1.0):
    """
       blending function polynomial
       d = x value
       a = area under curve/uncertainty radius
       b = horizontal shift
       h = height of the set

       returns blend
    """
    d = float(d)
    a = float(a)
    b = float(b)
    h = float(h)

    if b - 1.0/a <= d <= b + 1.0/a:
        return 0.5 * h * (1 + math.cos(a * math.pi * (d - b)))
    else:
        return 0.0

BlendCosine = blendCosine


def blendSinc(d, u=1.0):
    """
       blending function sinc
       d = delta x = x - horizontal shift
       u = uncertainty radius of xabs estimate error

       returns blend
    """
    u = float(u)

    if u == 0 or d == 0:
        raise ValueError("Params cannot be zero.")

    return math.sin(d/u) / (d/u)

BlendSinc = blendSinc


def blendSpike(d=0.0, u=0.0, s=1.0):
    """
        blending function spike
        d - Delta x = xabs - xdr
        u - Horizontal offset
        s - Tuning scale factor

        returns blend
    """

    d = float(d)
    u = float(u)
    s = float(s)

    b = math.e**(-(abs(s * (d - u))))

    return b

BlendSpike = blendSpike


def blendSigmoidInc(d=0.0, u=0.0, s=1.0):
    """
        blending function increasing sigmoid
        d - Delta x = xabs - xdr
        u - Horizontal offset
        s - Tuning scale factor

        returns blend
    """
    d = float(d)
    u = float(u)
    s = float(s)

    b = 1.0/(1+math.e**(s*(u-d)))

    return b

BlendSigmoidInc = blendSigmoidInc


def blendSigmoidDec(d=0.0, u=0.0, s=1.0):
    """
        blending function decreasing sigmoid
        d - Delta x = xabs - xdr
        u - Horizontal offset
        s - Tuning scale factor

        returns blend
    """
    d = float(d)
    u = float(u)
    s = float(s)

    b = 1.0 - (1.0 / (1 + math.e ** (s * (u - d))))

    return b

BlendSigmoidDec = blendSigmoidDec
