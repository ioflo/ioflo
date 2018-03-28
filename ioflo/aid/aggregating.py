import math
import statistics


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


def gowa(w, wm, l=1.0):
    """
       Generalized Ordered Weighted Averaging Operator
       More info can be found here:
        https://pdfs.semanticscholar.org/2810/c971af0d01d085c799fb2295dc5668d055c8.pdf

       l = -1 = Ordered Weighted Harmonic Averaging Operator
       l = -.000000000001 = Ordered Weighted Geometric Averaging Operator
       l = 1 = Ordered Weighted Arithmetic Averaging Operator
       l = 2 = Ordered Weighted Quadratic Averaging Operator

       w = list of weights
       wm = list of importance weighted membership values
       l = lambda real number specifying type of owa to use

       returns ordered weighted average
    """
    if len(w) != len(wm):
        raise ValueError("Weights and membership value lists must be of equal length.")

    if l == 0:
        raise ZeroDivisionError("Param l cannot be 0.  Use -.000000000001 for owg.")

    wm.sort(reverse=True)

    s = 0
    for i in range(len(w)):
        s += w[i] * math.pow(wm[i], l)

    return math.pow(s, 1/l)

Gowa = gowa


def owa(w, wm):
    """
       Ordered Weighted Arithmetic Averaging Operator
       w = [1,0,0,0] = AND
       w = [0,0,0,1] = OR
       w = [1/n,1/n,1/n,1/n] = Arithmetic Average where n=len(w)

       w = list of weights
       wm = list of importance weighted membership values

       returns ordered arithmetic weighted average
    """

    if len(w) != len(wm):
        raise ValueError("Weights and membership value lists must be of equal length.")

    wm.sort(reverse=True)

    s = 0
    for i in range(len(w)):
        s += w[i] * wm[i]

    return s

Owa = owa


def owg(w, wm):
    """
       Ordered Weighted Geometric Averaging Operator
       More info can be found here:
        ftp://decsai.ugr.es/pub/arai/tech_rep/decision/libroOWG.pdf
       w = [1,0,0,0] = AND
       w = [0,0,0,1] = OR
       w = [1/n,1/n,1/n,1/n] = Geometric Average where n=len(w)

       w = list of weights
       wm = list of importance weighted membership values

       returns ordered geometric weighted average
    """
    if len(w) != len(wm):
        raise ValueError("Weights and membership value lists must be of equal length.")

    wm.sort(reverse=True)

    s = 1
    for i in range(len(w)):
        s *= math.pow(wm[i], w[i])

    return s

Owg = owa


def owh(w, wm):
    """
       Ordered Weighted Harmonic Averaging Operator
       w = [1,0,0,0] = AND
       w = [0,0,0,1] = OR
       w = [1/n,1/n,1/n,1/n] = Harmonic Average where n=len(w)

       w = list of weights
       wm = list of importance weighted membership values

       returns ordered harmonic weighted average
    """
    return gowa(w, wm, -1)

Owh = owh


def owq(w, wm):
    """
       Ordered Weighted Quadratic Averaging Operator
       w = [1,0,0,0] = AND
       w = [0,0,0,1] = OR
       w = [1/n,1/n,1/n,1/n] = Quadratic Average where n=len(w)

       w = list of weights
       wm = list of importance weighted membership values

       returns ordered quadratic weighted average
    """
    return gowa(w, wm, 2)

Owq = owq


def median(wm):
    """
       Median Operator

       wm = list of importance weighted membership values

       returns the middle value in the set
    """
    return statistics.median(wm)

Median = median
