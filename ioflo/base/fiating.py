"""fiating.py goal action module

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
from . import tasking
from . import framing

from ..aid.consoling import getConsole
console = getConsole()

class Fiat(acting.Actor):
    """Fiat Class for explicit control of slave framers
       slave framer is not in framer.auxes list and is not actively run by scheduler

    """
    Registry = odict()

    def _resolve(self, tasker, **kwa):
        """Resolves value (tasker) link that is passed in as parm
           resolved link is passed back to ._act to store in parms
           since framer may not be current framer at build time
        """
        parms = super(Fiat, self)._resolve( **kwa)

        parms['tasker'] = tasker = tasking.resolveTasker(tasker,
                                                 who=self.name,
                                                 desc='fiat tasker',
                                                 contexts=[SLAVE],
                                                 human=self._act.human,
                                                 count=self._act.count)
        return parms

class FiatReady(Fiat):
    """FiatReady Fiat

    """
    def __init__(self, **kw):
        """Initialization method for instance."""
        super(FiatReady,self).__init__(**kw)

    def action(self, tasker, **kw):
        """ready control for explicit slave tasker"""

        console.profuse("Ready {0}\n".format(tasker.name))
        status = tasker.runner.send(READY)
        return (status == READIED)

class FiatStart(Fiat):
    """FiatStart Fiat

    """
    def __init__(self, **kw):
        """Initialization method for instance."""
        super(FiatStart,self).__init__(**kw)

    def action(self, tasker, **kw):
        """start control for explicit slave tasker"""

        console.profuse("Start {0}\n".format(tasker.name))
        status = tasker.runner.send(START)
        return (status == STARTED)

class FiatStop(Fiat):
    """FiatStop Fiat

    """
    def __init__(self, **kw):
        """Initialization method for instance."""
        super(FiatStop,self).__init__(**kw)

    def action(self, tasker, **kw):
        """stop control for explicit slave framer"""

        console.profuse("Stope {0}\n".format(tasker.name))
        status = tasker.runner.send(STOP)
        return (status == STOPPED)

class FiatRun(Fiat):
    """FiatRun Fiat

    """
    def __init__(self, **kw):
        """Initialization method for instance."""
        super(FiatRun,self).__init__(**kw)

    def action(self, tasker, **kw):
        """run control for explicit slave tasker"""

        console.profuse("Run {0}\n".format(tasker.name))
        status = tasker.runner.send(RUN)
        return (status == RUNNING)

class FiatAbort(Fiat):
    """FiatAbort Fiat

    """
    def __init__(self, **kw):
        """Initialization method for instance."""
        super(FiatAbort,self).__init__(**kw)

    def action(self, tasker, **kw):
        """abort control for explicit slave tasker"""

        console.profuse("Abort {0}\n".format(tasker.name))
        status = tasker.runner.send(ABORT)
        return (status == ABORTED)
