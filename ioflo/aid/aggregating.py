import math


def fuzzyAnd(m):
    """
    fuzzy anding
    m = list of membership values to be anded

    returns smallest value in the list
    """
    return min(m)

FuzzyAnd = fuzzyAnd


def fuzzyOr(m):
    """
    fuzzy oring
    m = list of membership values to be ored

    returns largest value in the list
    """
    return max(m)

FuzzyOr = fuzzyOr


def fuzzyNot(x):
    """
    fuzzy not
    x = single membership value to be noted

    returns the inverse membership value
    """
    return 1 - x


def compensatoryAnd(m, g=0.5):
    """
       anding function
       m = list of membership values for x derived from n membership functions
       g = gamma value 0=product 1=algebraic sum

       returns compensatory AND value of x
    """
    g = float(g)

    product1 = 1
    product2 = 1
    for mem in m:
        product1 *= mem
        product2 *= (1 - mem)

    return math.pow(product1, 1 - g) * math.pow((1 - product2), g)

CompensatoryAnd = compensatoryAnd


def owa(w, wm):
    """
       Ordered Weighted Averaging Operator
       w = list of weights
       wm = list of importance weighted membership values

       returns ordered weighted average
    """

    if len(w) != len(wm):
        raise ValueError("Weights and membership value lists must be of equal length.")

    wm.sort(reverse=True)

    s = 0
    for i in range(len(w)):
        s += w[i] * wm[i]

    return s

Owa = owa
