"""wanting.py goal action module


"""
#print("module {0}".format(__name__))

import time
import struct
from collections import deque
import inspect



from .globaling import *
from .odicting import odict
from . import aiding
from . import excepting
from . import registering
from . import storing
from . import acting
from . import tasking
from . import framing

from .consoling import getConsole
console = getConsole()


class Want(acting.Actor):
    """
    Class for requesting control via skedder using .desire attribute
       of explicit peer tasker generators

    """
    Registry = odict()

    def _resolve(self, taskers, **kwa):
        """Resolves value taskers list of links that is passed in as parm
           resolved links are passed back to act to store in parms
           since tasker may not be current framer at build time
        """
        parms = super(Want, self)._resolve( **kwa)
        links = set()
        for tasker in taskers:
            if tasker == 'all':
                for tasker in self.store.house.taskables:
                    links.add(tasker)
            elif tasker == 'me':
                tasker = self._act.frame.framer
                links.add(tasker)

            else:
                tasker = tasking.resolveTasker(tasker,
                                               who=self.name,
                                               desc='tasker',
                                               contexts=[ACTIVE, INACTIVE],
                                               human=self._act.human,
                                               count=self._act.count)
                links.add(tasker)

        parms['taskers'] = links #replace with valid list

        return parms

class WantStop(Want):
    """WantStop Want
       bid stop tasker [tasker ...]
       bid stop all
       bid stop [me]
    """
    def action(self, taskers, **kw):
        """stop taskers """

        for tasker in taskers:
            tasker.desire = STOP
            console.profuse( "Bid stop {0}\n".format(tasker.name))

        return None

class WantStart(Want):
    """WantStart Want
       bid start tasker [taskers ...]
       bid start all
       bid start [me] #won't cahnge anything since must be already started
    """
    def action(self, taskers, **kw):
        """start taskers  """
        for tasker in taskers:
            tasker.desire = START
            console.profuse( "Bid start {0}\n".format(tasker.name))

        return None

class WantRun(Want):
    """WantRun Want
       bid run tasker [taskers ...]
       bid run all
       bid run [me] #won't cahnge anything since must be already running
    """
    def action(self, taskers, **kw):
        """run taskers """
        for tasker in taskers:
            tasker.desire = RUN
            console.profuse( "Bid run {0}\n".format(tasker.name))

        return None

class WantAbort(Want):
    """WantAbort Want
       bid abort tasker [taskers ...]
       bid abort all
       bid abort [me]
    """
    def action(self, taskers, **kw):
        """abort taskers """
        for tasker in taskers:
            tasker.desire = ABORT
            console.profuse( "Bid abort {0}\n".format(tasker.name))

        return None

class WantReady(Want):
    """WantReady Want
       bid ready tasker [taskers ...]
       bid ready all
       bid ready [me]  # won't change anything since must be already ready
    """
    def action(self, taskers, **kw):
        """readt taskers """
        for tasker in taskers:
            tasker.desire = READY
            console.profuse( "Bid ready {0}\n".format(tasker.name))

        return None
