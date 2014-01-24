"""wanting.py goal action module


"""
#print "module %s" % __name__

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
    """Wnat Class for requesting control via skedder using .desire attribute
       of explicit peer tasker generators

       inherited attributes
          .name = unique name for actor instance
          .store = shared data store
          
    """
    Registry = odict()
    
    def resolve(self, taskers, **kwa):
        """Resolves value taskers list of links that is passed in as parm
           resolved links are passed back to act to store in parms
           since tasker may not be current framer at build time
        """
        parms = super(Want, self).resolve( **kwa)  
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
    
    def cloneParms(self, parms, clones, **kw):
        """ Returns parms fixed up for framing cloning. This includes:
            Reverting any Frame links to name strings,
            Reverting non cloned Framer links into name strings
            Replacing any cloned framer links with the cloned name strings from clones
            Replacing any parms that are acts with clones.
            
            clones is dict whose items keys are original framer names
            and values are duples of (original,clone) framer references
        """
        parms = super(StatusNeed,self).cloneParms(parms, clones, **kw)
        taskers = parms.get('taskers')
        links = []      
        for tasker in taskers:
            if isinstance(tasker, tasking.Tasker):
                if tasker.name in clones: # replace name with clone.name
                    links.append(clones[tasker.name][1].name)
                else:
                    links.append(tasker.name) # revert to name
            elif tasker in clones: # replace name with clone.name
                links.append(clones[tasker][1].name)
            else:
                links.append(tasker)
        
        parms['taskers'] = links
        
        return parms    

class StartWant(Want):
    """StartWant Want 
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

class StopWant(Want):
    """StopWant Want 
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

class RunWant(Want):
    """RunWant Want 
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

def Test():
    """Module Common self test

    """
    pass

if __name__ == "__main__":
    test()

