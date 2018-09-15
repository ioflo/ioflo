import pytest

from ioflo.aid.blending import *


def testBlendCauchian():
    D = [i / 2 - 3 for i in range(0, 13)]

    results = []
    for d in D:
        results.append((round(d, 3), round(blendCauchian(d), 3)))

    # Test a=1, b=0, c=2, h=1
    assert results == [(-3.0, 0.012),
                       (-2.5, 0.025),
                       (-2.0, 0.059),
                       (-1.5, 0.165),
                       (-1.0, 0.5),
                       (-0.5, 0.941),
                       (0.0, 1.0),
                       (0.5, 0.941),
                       (1.0, 0.5),
                       (1.5, 0.165),
                       (2.0, 0.059),
                       (2.5, 0.025),
                       (3.0, 0.012)]

    assert round(blendCauchian(0.0, h=2.0), 3) == 2.0
    assert round(blendCauchian(2.0, b=2.0), 3) == 1.0
    for x in np.arange(-3, 3.1, .1):
        assert round(blendCauchian(x, c=0.0), 3) == 0.5

    with pytest.raises(ValueError, message="Param a must be a non zero value."):
        blendCauchian(0.0, a=0.0)


def testBlendCosine():
    D = [i / 2 - 2.5 for i in range(0, 11)]

    results = []
    for d in D:
        results.append((round(d, 3), round(blendCosine(d, a=0.5), 3)))

    # Test a=0.5, b=0, h=1
    assert results == [(-2.5, 0.0),
                       (-2.0, 0.0),
                       (-1.5, 0.146),
                       (-1.0, 0.5),
                       (-0.5, 0.854),
                       (0.0, 1.0),
                       (0.5, 0.854),
                       (1.0, 0.5),
                       (1.5, 0.146),
                       (2.0, 0.0),
                       (2.5, 0.0)]

    assert round(blendCosine(0.0, h=2.0), 3) == 2.0
    assert round(blendCosine(2.0, b=2.0), 3) == 1.0


def testBlendSinc():
    D = [i / 2 -3.5 for i in range(0, 15)]

    results = []
    for d in D:
        results.append((round(d, 3), round(blendSinc(d), 3)))

    # Test u=1.0
    assert results == [(-3.5, 0.0),
                       (-3.0, 0.047),
                       (-2.5, 0.239),
                       (-2.0, 0.455),
                       (-1.5, 0.665),
                       (-1.0, 0.841),
                       (-0.5, 0.959),
                       (0.0, 1.0),
                       (0.5, 0.959),
                       (1.0, 0.841),
                       (1.5, 0.665),
                       (2.0, 0.455),
                       (2.5, 0.239),
                       (3.0, 0.047),
                       (3.5, 0.0)]
