import pytest
import numpy as np

from ioflo.aid.blending import *


# def testOWA():
#     with pytest.raises(ValueError, message="Weights, membership, and importance lists must be of equal length."):
#         owa([1, 1, 0, 0], [.2, .1, .3])
#
#     with pytest.raises(ValueError, message="Weights, membership, and importance lists must be of equal length."):
#         owa([1, 1, 0, 0], [.2, .1, .3], [.7, .8, .2, .4])
#
#     assert round(owa([1, 1, 0, 0], [.2, .1, .3, .4]), 4) == 0.07
#     assert round(owa([0, 0, 0, 0], [.2, .1, .3, .4]), 4) == 0.00
#     assert round(owa([0, 0, 1, 1], [.2, .1, .3, .4]), 4) == 0.03
#
#     assert round(owa([1, 1, 0, 0], [.2, .1, .3, .4], [.1, .2, .1, .6]), 4) == 0.27


def testBlendCauchian():
    D = [x for x in np.arange(-3, 3.5, .5)]

    results = []
    for d in D:
        results.append((round(d, 3), round(blendCauchian(d), 3)))

    print(results)

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
