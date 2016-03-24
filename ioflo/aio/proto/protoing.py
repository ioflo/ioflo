"""
Device Base Package

"""
from __future__ import absolute_import, division, print_function


from ...aid import getConsole

console = getConsole()

class MixIn(object):
    """
    Base class to enable consistent MRO for mixin multiple inheritance
    """
    def __init__(self, *pa, **kwa):
        pass
