import pytest

from ioflo.aid.aggregating import *


def testFuzzyAnd():
    assert fuzzyAnd([1, 2]) == 1
    assert fuzzyAnd([-7, 5]) == -7


def testFuzzyOr():
    assert fuzzyOr([1, 2]) == 2
    assert fuzzyOr([-10, 5]) == 5


def testFuzzyNot():
    assert round(fuzzyNot(0.98), 3) == 0.02
    assert round(fuzzyNot(0.5), 3) == 0.5
    assert round(fuzzyNot(0.02), 3) == 0.98


def testCompensatoryAnd():
    # test algebraic product
    assert compensatoryAnd([0.1, 0.02], 0) == 0.002
    assert compensatoryAnd([0.1, 0.02, 0.3], 0) == 0.0006

    # test algebraic sum
    assert compensatoryAnd([0.1, 0.02], 1) == 0.118
    assert round(compensatoryAnd([0.1, 0.02, 0.3], 1), 5) == 0.3826


def testOwa():
    with pytest.raises(ValueError, message="Weights and membership value lists must be of equal length."):
        owa([1, 1, 0, 0], [.2, .1, .3])

    assert round(owa([1, 1, 0, 0], [.2, .1, .3, .4]), 4) == 0.7
    assert round(owa([0, 0, 0, 0], [.2, .1, .3, .4]), 4) == 0.00
    assert round(owa([0, 0, 1, 1], [.2, .1, .3, .4]), 4) == 0.3

    # test and
    assert round(owa([0, 0, 0, 1], [.2, .1, .3, .4]), 4) == 0.1

    # test or
    assert round(owa([1, 0, 0, 0], [.2, .1, .3, .4]), 4) == 0.4

    # test average
    assert round(owa([1/4, 1/4, 1/4, 1/4], [.2, .1, .3, .4]), 4) == 0.25
