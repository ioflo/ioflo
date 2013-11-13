"""traiting.py goal action module


"""
#print "module %s" % __name__

import time
import struct
from collections import deque
import inspect


from .globaling import *

from . import aiding
from . import excepting
from . import registering
from . import storing
from . import acting

from .consoling import getConsole
console = getConsole()


def CreateInstances(store):
    """Create action instances
       must be function so can recreate after clear registry
       globals good for module self tests
    """
    #global traitDepth
    #instance should be only one should use singleton or borg
    traitDepth = DepthTrait(name = 'traitDepth', store = store)



class Trait(acting.Actor):
    """Trait Class for configuration feature

    """
    Counter = 0  
    Names = {}

    def __init__(self, **kw):
        """Initialization method for instance.

        """
        if 'preface' not in kw:
            kw['preface'] = 'Trait'

        super(Trait,self).__init__(**kw)  



class DepthTrait(Trait):
    """DepthTrait Trait

    """
    def __init__(self, **kw):
        """Initialization method for instance."""

        super(DepthTrait,self).__init__(**kw)        

    def action(self, value = 0.0, **kw):
        """Use depth """

        console.profuse( "Use depth of {0:0.3f}\n".format(value))

        return None



def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    test()

