"""traiting.py goal action module


"""
#print("module {0}".format(__name__))

import time
import struct
from collections import deque
import inspect

from ..aid.sixing import *
from .globaling import *
from ..aid.odicting import odict

from ..aid import aiding
from . import excepting
from . import registering
from . import storing
from . import acting

from ..aid.consoling import getConsole
console = getConsole()

class Trait(acting.Actor):
    """Trait Class for configuration feature

    """
    Registry = odict()

class TraitDepth(Trait):
    """TraitDepth Trait

    """

    def action(self, value = 0.0, **kw):
        """Use depth """

        console.profuse( "Use depth of {0:0.3f}\n".format(value))

        return None
