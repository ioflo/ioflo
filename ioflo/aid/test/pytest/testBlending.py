import pytest
import numpy as np

from ioflo.aid.blending import *


def testBlendCauchian():
    D = [x for x in np.arange(-3, 3.5, .5)]

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
    D = [x for x in np.arange(-2.5, 3, .5)]

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
    D = [x for x in np.arange(-3.1, 3.6, .5)]

    results = []
    for d in D:
        results.append((round(d, 3), round(blendSinc(d), 3)))

    print(results)

    # Test u=1.0
    assert results == [(-3.1, 0.013),
                       (-2.6, 0.198),
                       (-2.1, 0.411),
                       (-1.6, 0.625),
                       (-1.1, 0.81),
                       (-0.6, 0.941),
                       (-0.1, 0.998),
                       (0.4, 0.974),
                       (0.9, 0.87),
                       (1.4, 0.704),
                       (1.9, 0.498),
                       (2.4, 0.281),
                       (2.9, 0.082),
                       (3.4, -0.075)]
