"""goaling.py goal action module

"""
#print "module %s" % __name__

import time
import struct

from collections import deque
from itertools import izip

import inspect



from .globaling import *
from .odicting import odict
from . import aiding
from . import excepting
from . import registering
from . import storing 
from . import acting

from .consoling import getConsole
console = getConsole()

#Class definitions
#instance should be only one should use singleton or borg
def CreateInstances(store):
    """Create action instances
       must be function so can recreate after clear registry
       globals good for module self tests
    """
    #global goalDirect, goalIndirect

    goalDirect = DirectGoal(name = 'goalDirect', store = store)
    goalIndirect = IndirectGoal(name = 'goalIndirect', store = store)


class Goal(acting.Actor):
    """Goal Class for setting configuration or command value in data share

    """
    Counter = 0  
    Names = {}

    def __init__(self,  **kw):
        """Initialization method for instance.
           inherited attributes:
              .name = unique name for action instance
              .store = shared data store

           parameters:
              goal = share of goal

        """
        if 'preface' not in kw:
            kw['preface'] = 'Goal'

        super(Goal,self).__init__(**kw)  

    def expose(self):
        """

        """
        print "Goal %s" % (self.name)


#Direct goal
class DirectGoal(Goal):
    """DirectGoal Goal

    """
    def __init__(self, **kw):
        """Initialization method for instance.

           inherited attributes:
              .name = unique name for action instance
              .store = shared data store

           parameters:
              goal = share of goal
              data = dict of data fields to assign to goal share


        """
        super(DirectGoal, self).__init__(**kw)  #.goal inited here


    def action(self, goal, data, **kw): 
        """Set goal to data dictionary"""

        console.profuse("Set {0} to {1}\n".format(goal.name, data))
        goal.update(data)
        return None

#Direct goal
class IndirectGoal(Goal):
    """IndirectGoal Goal

    """
    def __init__(self, **kw):
        """Initialization method for instance.

           inherited attributes:
              .name = unique name for action instance
              .store = shared data store

           parameters:
              goal = share of goal
              source = share of source to get data from
              fields = fields to use to update goal


        """
        super(IndirectGoal, self).__init__(**kw)  #.goal inited here


    def action(self, goal, goalFields, source, sourceFields, **kw): 
        """Set goalFields in goal from sourceFields in source"""

        console.profuse("Set {0} in {1} from {2} in {3}\n".format(
            goal.name, goalFields, source.name, sourceFields))

        data = odict()
        for gf, sf in izip(goalFields, sourceFields):
            data[gf] = source[sf]

        goal.update(data)

        return None



def Test():
    """Module Common self test

    """
    pass

if __name__ == "__main__":
    test()

