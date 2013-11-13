"""wanting.py goal action module


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
    """
    wantStart = StartWant(name = 'wantStart', store = store)
    wantStop = StopWant(name = 'wantStop', store = store)
    wantRun = RunWant(name = 'wantRun', store = store)

class Want(acting.Actor):
    """Wnat Class for requesting control via skedder using .desire attribute
       of explicit peer tasker generators

       inherited attributes
          .name = unique name for actor instance
          .store = shared data store
          
    """
    Counter = 0  
    Names = {}

    def __init__(self, **kw):
        """Initialization method for instance. """
        if 'preface' not in kw:
            kw['preface'] = 'Fiat'

        super(Want,self).__init__(**kw)  

    def resolveLinks(self, taskers, **kw):
        """Resolves value (tasker) link that is passed in as parm
           resolved link is passed back to act to store in parms
           since tasker may not be current framer at build time
        """
        parms = {}
        links = []
        for tasker in taskers:
            if not isinstance(tasker, tasking.Tasker): # string name of tasker
                if tasker == 'all':
                    for tasker in self.store.house.taskables:
                        if tasker not in links:
                            links.append(tasker)
                elif tasker in tasking.Tasker.Names: 
                    tasker = tasking.Tasker.Names[tasker]
                    if tasker not in links:
                        links.append(tasker)
                else:
                    raise excepting.ResolveError("ResolveError: Bad want tasker link name", tasker, '')
            else:
                links.append(tasker)

        for tasker in links:
            if tasker.schedule == AUX or tasker.schedule == SLAVE : #want forbidden on aux or slave 
                msg = "ResolveError: Bad want tasker, aux or slave forbidden"
                raise excepting.ResolveError(msg, tasker.name, tasker.schedule)

        parms['taskers'] = links #replace with valid list

        return parms


class StartWant(Want):
    """StartWant Want 
       bid start tasker [taskers ...]
       bid start all
       bid stort me #won't do anything
    """
    def __init__(self, **kw):
        """Initialization method for instance.  """
        super(StartWant,self).__init__(**kw)       

    def action(self, taskers, **kw):
        """start taskers  """
        for tasker in taskers:
            tasker.desire = START
            console.profuse( "Bid start {0}\n".format(tasker.name))

        return None

class StopWant(Want):
    """StopWant Want 
       bid stop tasker [tasker ...]
       bid stop all
       bid stop me 
    """
    def __init__(self, **kw):
        """Initialization method for instance. """
        super(StopWant,self).__init__(**kw)       

    def action(self, taskers, **kw):
        """stop taskers """

        for tasker in taskers:
            tasker.desire = STOP
            console.profuse( "Bid stop {0}\n".format(tasker.name))

        return None

class RunWant(Want):
    """RunWant Want 
       bid run tasker [taskers ...]
       bid run all
       bid run me #won't do anything
    """
    def __init__(self, **kw):
        """Initialization method for instance. """
        super(RunWant,self).__init__(**kw)       

    def action(self, taskers, **kw):
        """run taskers """
        for tasker in taskers:
            tasker.desire = RUN
            console.profuse( "Bid run {0}\n".format(tasker.name))

        return None

def Test():
    """Module Common self test

    """
    pass

if __name__ == "__main__":
    test()

