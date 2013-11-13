"""completing.py  done action module

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
from . import tasking
from . import framing

from .consoling import getConsole
console = getConsole()


def CreateInstances(store):
    """Create action instances
       must be function so can recreate after clear registry
       globals good for module self tests
    """
    #global completeDone #used for testing

    completeDone = DoneComplete(name = 'completeDone', store = store)


class Complete(acting.Actor):
    """Complete Class for indicating tasker done state

    """
    Counter = 0  
    Names = {}

    def __init__(self, **kw):
        """Initialization method for instance.

        """
        if 'preface' not in kw:
            kw['preface'] = 'Complete'

        super(Complete,self).__init__(**kw)  

    def resolveLinks(self, framer, **kw):
        """Resolves value (framer) link that is passed in as parm
           resolved link is passed back to act to store in parms
           since framer may not be current framer at build time
        """
        parms = {}
        if not isinstance(framer, framing.Framer): #so name of framer
            if framer not in framing.Framer.Names: 
                raise excepting.ResolveError("ResolveError: Bad done framer link name", framer, '')
            framer = framing.Framer.Names[framer]

        if not isinstance(framer, framing.Framer): #maker sure framer not other tasker
            raise excepting.ResolveError("ResolveError: Bad done framer name not for framer", framer, '')

        #if not framer.schedule in [AUX, SLAVE]: #maker sure framer is auxliary or slave
            #raise excepting.ResolveError("ResolveError: Bad done framer, framer not auxiliary or slave", framer, '')

        parms['framer'] = framer #replace name with valid link

        return parms


class DoneComplete(Complete):
    """DoneComplete Complete

    """
    def __init__(self, **kw):
        """Initialization method for instance.

        """
        super(DoneComplete,self).__init__(**kw)       


    def action(self, framer = None, **kw):
        """set done state to True for aux or slave framer

        """
        framer.done = True
        console.profuse("    Done {0}\n".format(self.name))

        return None


def Test():
    """Module Common self test

    """
    pass

if __name__ == "__main__":
    test()

