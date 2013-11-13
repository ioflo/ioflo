"""fiating.py goal action module

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
    #global fiatStart, fiatStop, fiatRun
    fiatReady = ReadyFiat(name = 'fiatReady', store = store)
    fiatStart = StartFiat(name = 'fiatStart', store = store)
    fiatStop = StopFiat(name = 'fiatStop', store = store)
    fiatRun = RunFiat(name = 'fiatRun', store = store)
    fiatAbort = AbortFiat(name = 'fiatAbort', store = store)


class Fiat(acting.Actor):
    """Fiat Class for explicit control of slave framers
       slave framer is not in framer.auxes list and is not actively run by scheduler

    """
    Counter = 0  
    Names = {}

    def __init__(self, **kw):
        """Initialization method for instance.

        """
        if 'preface' not in kw:
            kw['preface'] = 'Fiat'

        super(Fiat,self).__init__(**kw)

    def resolveLinks(self, tasker, **kw):
        """Resolves value (tasker) link that is passed in as parm
           resolved link is passed back to act to store in parms
           since framer may not be current framer at build time
        """
        parms = {}
        if not isinstance(tasker, tasking.Tasker): #name
            if tasker not in tasking.Tasker.Names: 
                raise excepting.ResolveError("ResolveError: Bad fiat tasker link name", tasker, '')
            tasker = tasking.Tasker.Names[tasker]

        if tasker.schedule != SLAVE : # only allowed on slave taskers
            msg = "ResolveError: Bad tell tasker, not slave"
            raise excepting.ResolveError(msg, tasker.name, tasker.schedule)


        parms['tasker'] = tasker #replace name with valid link

        return parms

class ReadyFiat(Fiat):
    """ReadyFiat Fiat

    """
    def __init__(self, **kw):
        """Initialization method for instance."""
        super(ReadyFiat,self).__init__(**kw)  

    def action(self, tasker, **kw):
        """ready control for explicit slave tasker"""

        console.profuse("Ready {0}\n".format(tasker.name))
        status = tasker.runner.send(READY)
        return (status == READIED)

class StartFiat(Fiat):
    """StartFiat Fiat

    """
    def __init__(self, **kw):
        """Initialization method for instance."""
        super(StartFiat,self).__init__(**kw)  

    def action(self, tasker, **kw):
        """start control for explicit slave tasker"""

        console.profuse("Start {0}\n".format(tasker.name))
        status = tasker.runner.send(START)
        return (status == STARTED)

class StopFiat(Fiat):
    """StopFiat Fiat

    """
    def __init__(self, **kw):
        """Initialization method for instance."""
        super(StopFiat,self).__init__(**kw)  

    def action(self, tasker, **kw):
        """stop control for explicit slave framer"""

        console.profuse("Stope {0}\n".format(tasker.name))
        status = tasker.runner.send(STOP)
        return (status == STOPPED)

class RunFiat(Fiat):
    """RunFiat Fiat

    """
    def __init__(self, **kw):
        """Initialization method for instance."""
        super(RunFiat,self).__init__(**kw)  

    def action(self, tasker, **kw):
        """run control for explicit slave tasker"""

        console.profuse("Run {0}\n".format(tasker.name))
        status = tasker.runner.send(RUN)
        return (status == RUNNING)

class AbortFiat(Fiat):
    """RunFiat Fiat

    """
    def __init__(self, **kw):
        """Initialization method for instance."""
        super(AbortFiat,self).__init__(**kw)  

    def action(self, tasker, **kw):
        """abort control for explicit slave tasker"""

        console.profuse("Abort {0}\n".format(tasker.name))      
        status = tasker.runner.send(ABORT)
        return (status == ABORTED)


def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    test()
