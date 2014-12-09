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

    def resolve(self, taskers, **kwa):
        """Resolves value taskers list of links that is passed in as parm
           resolved links are passed back to act to store in parms
           since tasker may not be current framer at build time
        """
        parms = super(Want, self).resolve( **kwa)
        links = set()
        for tasker in taskers:
            if tasker == 'all':
                for tasker in self.store.house.taskables:
                    links.add(tasker)
            elif tasker == 'me':
                tasker = self.act.frame.framer
                links.add(tasker)

            else:
                tasker = tasking.resolveTasker(tasker,
                                               who=self.name,
                                               desc='tasker',
                                               contexts=[ACTIVE, INACTIVE],
                                               human=self.act.human,
                                               count=self.act.count)
                links.add(tasker)

        parms['taskers'] = links #replace with valid list

        return parms

class WantStart(Want):
    """WantStart Want
       bid start tasker [taskers ...]
       bid start all
       bid stort me #won't do anything
    """
    def action(self, taskers, **kw):
        """start taskers  """
        for tasker in taskers:
            tasker.desire = START
            console.profuse( "Bid start {0}\n".format(tasker.name))

        return None

class WantStop(Want):
    """WantStop Want
       bid stop tasker [tasker ...]
       bid stop all
       bid stop me
    """
    def action(self, taskers, **kw):
        """stop taskers """

        for tasker in taskers:
            tasker.desire = STOP
            console.profuse( "Bid stop {0}\n".format(tasker.name))

        return None

class WantRun(Want):
    """WantRun Want
       bid run tasker [taskers ...]
       bid run all
       bid run me #won't do anything
    """
    def action(self, taskers, **kw):
        """run taskers """
        for tasker in taskers:
            tasker.desire = RUN
            console.profuse( "Bid run {0}\n".format(tasker.name))

        return None
