"""completing.py  done action module

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

class Complete(acting.Actor):
    """Complete Class for indicating tasker done state

    """
    Registry = odict()

    def resolve(self, framer, **kwa):
        """Resolves value (framer) link that is passed in as parm
           resolved link is passed back to act to store in parms
           since tasker may not be current tasker at build time
        """
        parms = super(Complete, self).resolve( **kwa)
        if framer == 'me':
            framer = self.act.frame.framer.name
        parms['framer'] = framer = framing.resolveFramer(framer,
                                                         who=self.name,
                                                         desc='framer',
                                                         contexts=[AUX, SLAVE],
                                                         human=self.act.human,
                                                         count=self.act.count)

        return parms

class CompleteDone(Complete):
    """CompleteDone Complete

    """
    def action(self, framer = None, **kw):
        """set done state to True for aux or slave framer

        """
        framer.done = True
        console.profuse("    Done {0}\n".format(framer.name))

        return None
