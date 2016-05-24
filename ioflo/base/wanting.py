"""wanting.py goal action module


"""
#print("module {0}".format(__name__))

import time
import struct
from collections import deque
import inspect


from ..aid.sixing import *
from .globaling import STOP, START, RUN, ABORT, READY, ControlNames
from .globaling import INACTIVE, ACTIVE, AUX, SLAVE, MOOT, ScheduleNames, ScheduleValues

from ..aid import odict, oset
from ..aid import aiding
from . import excepting
from . import registering
from . import storing
from . import acting
from . import tasking
from . import framing

from ..aid.consoling import getConsole
console = getConsole()


class Want(acting.Actor):
    """
    Class for requesting control via skedder using .desire attribute
       of explicit peer tasker generators

    """
    Registry = odict()

    def _resolve(self, taskers, period, source, sourceField, **kwa):
        """Resolves value taskers list of links that is passed in as parm
           resolved links are passed back to act to store in parms
           since tasker may not be current framer at build time
        """
        parms = super(Want, self)._resolve( **kwa)
        links = oset()
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


        if  period is None and source is not None:
            parms['source'] = source = self._resolvePath(ipath=source, warn=True) # now a share
            if not sourceField: #default rules for field
                sourceField = 'value'

            if sourceField not in source:
                console.profuse("     Warning: Non-existent field '{0}' in source"
                                " {1} ... creating anyway".format(sourceField, source.name))
                source[sourceField] = 0.0  # create

            parms['sourceField'] = sourceField
        else:
            parms['source'] = None
            parms['sourceField'] = None

        parms['taskers'] = links #replace with valid oset/list ordered
        parms['period'] = period

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
    def action(self, taskers, period, source, sourceField, **kw):
        """start taskers  """
        if source is not None:
            period = source[sourceField]
        for tasker in taskers:
            if period is not None:
                tasker.period = max(0.0, period)
            tasker.desire = START
            console.profuse( "Bid start {0} at {1}\n".format(tasker.name, tasker.period))

        return None

class WantRun(Want):
    """WantRun Want
       bid run tasker [taskers ...]
       bid run all
       bid run [me] #won't cahnge anything since must be already running
    """
    def action(self, taskers, period, source, sourceField, **kw):
        """run taskers """
        if source is not None:
            period = source[sourceField]
        for tasker in taskers:
            if period is not None:
                tasker.period = max(0.0, period)
            tasker.desire = RUN
            console.profuse( "Bid run {0} at (1)\n".format(tasker.name, tasker.period))

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
    def action(self, taskers, period, source, sourceField, **kw):
        """readty taskers """
        if source is not None:
            period = source[sourceField]
        for tasker in taskers:
            if period is not None:
                tasker.period = max(0.0, period)
            tasker.desire = READY
            console.profuse( "Bid ready {0} at {1}\n".format(tasker.name, tasker.period))

        return None
