"""needing.py need action module

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


#Class definitions should be singletons or borgs
#instance should be only one should use singleton or borg

def CreateInstances(store):
    """Create action gloal lists and instances
       must be function so can recreate after clear registry
       globals good for module self tests
    """
    #global specialNeeds, simpleNeeds


    #specialNeeds = ['done', 'always', 'status']
    #simpleNeeds = ['elapsed', 'repeat']

    #special needs
    needDone = DoneNeed(name = 'needDone', store = store)
    needAlways = AlwaysNeed(name = 'needAlways', store = store)
    needStatus = StatusNeed(name = 'needStatus', store = store)

    #dynamic need types
    needBoolean = BooleanNeed(name = 'needBoolean', store = store)
    needDirect = DirectNeed(name = 'needDirect', store = store)
    needIndirect = IndirectNeed(name = 'needIndirect', store = store)


class Need(acting.Actor):
    """Need Class for conditions  such as entry or trans

    """
    Counter = 0  
    Names = {}

    def __init__(self, **kw):
        """Initialization method for instance.

           inherited attributes:
              .name = unique name for action instance
              .store = shared data store

        """
        if 'preface' not in kw:
            kw['preface'] = 'Need'

        super(Need,self).__init__(**kw)  


    def expose(self):
        """

        """
        print "Need %s " % (self.name)

    @staticmethod
    def Check(state, comparison, goal, tolerance):
        """Check state compared to goal with tolerance
           tolerance ignored unless comparison == or !=

        """
        if comparison == '==':
            try: #in case goal is string
                result = ( (goal - abs(tolerance)) <= state <= (goal + abs(tolerance)))
            except TypeError:
                result = (goal == state)
        elif comparison == '<':
            result = ( state < goal)
        elif comparison == '<=':
            result = ( state <= goal)
        elif comparison == '>=':
            result = ( state >= goal)
        elif comparison == '>':
            result = ( state > goal)
        elif comparison == '!=':
            try: #in case goal is string
                result = ( state <= (goal - abs(tolerance)) or state >= (goal + abs(tolerance)) )
            except TypeError:
                result = (goal != state)
        else:
            result = False

        return result

#special needs
class AlwaysNeed(Need):
    """AlwaysNeed Need

       inherited attributes:

             .name = unique name for action instance
             .store = shared data store

       parameters:

    """
    def __init__(self, **kw):
        """Initialization method for instance.

        """
        super(AlwaysNeed, self).__init__(**kw) 


    def action(self, **kw):
        """Always return true"""

        result = True
        console.profuse("Need Always = {0}\n".format(result)) 

        return result


class DoneNeed(Need):
    """DoneNeed Need

       inherited attributes:

             .name = unique name for action instance
             .store = shared data store

       parameters:
          tasker
    """
    def __init__(self, **kw):
        """Initialization method for instance.

        """
        super(DoneNeed, self).__init__(**kw) 


    def action(self, tasker, **kw):
        """Check if  tasker done 

        """
        result = tasker.done
        console.profuse("Need Framer {0} done = {1}\n".format(tasker.name, result)) 

        return result

    def resolveLinks(self, tasker, **kw):
        """Resolves value (tasker) link that is passed in as tasker parm
           resolved link is passed back to container act to update in act's parms
        """
        parms = {}

        if not isinstance(tasker, tasking.Tasker): # name of tasker so resolve
            if tasker not in tasking.Tasker.Names: 
                raise excepting.ResolveError("ResolveError: Bad need done aux link", tasker, self.name)
            tasker = tasking.Tasker.Names[tasker] #replace tasker name with tasker

        #if not tasker.schedule in [AUX, SLAVE]: 
            #raise excepting.ResolveError("ResolveError: Bad need done tasker not auxiliary or slave", tasker, self.name)

        parms['tasker'] = tasker #replace name with valid link

        return parms #return items are updated in original act parms

class StatusNeed(Need):
    """StatusNeed Need

       inherited attributes:

             .name = unique name for action instance
             .store = shared data store

       parameters:
          tasker
          status
    """
    def __init__(self, **kw):
        """Initialization method for instance.

        """
        super(StatusNeed, self).__init__(**kw) 


    def action(self, tasker, status, **kw):
        """Check if  tasker done """

        result = (tasker.status == status)
        console.profuse("Need Tasker {0} status is {1} = {2}\n".format(
            tasker.name, StatusNames[status], result)) 

        return result

    def resolveLinks(self, tasker, status, **kw):
        """Resolves value (tasker) link that is passed in as parm
           resolved link is passed back to container act to update in act's parms
        """
        parms = dict(status=status)

        if not isinstance(tasker, tasking.Tasker): #so name of tasker
            if tasker not in tasking.Tasker.Names: 
                raise excepting.ResolveError("ResolveError: Bad need done tasker link", tasker, self.name)
            tasker = tasking.Tasker.Names[tasker] #replace tasker name with tasker

        parms['tasker'] = tasker #replace name with valid link

        return parms #return items are updated in original act parms

class BooleanNeed(Need):
    """BooleanNeed Need

       if state
    """
    def __init__(self, **kw):
        """Initialization method for instance.

           inherited attributes:

              .name = unique name for action instance
              .store = shared data store

           parameters:
              state = share of state
              stateField = field key



        """
        super(BooleanNeed,self).__init__(**kw)  

    def action(self, state, stateField, **kw):
        """Check if state[stateField] evaluates to True"""

        if state[stateField]:
            result = True
        else:
            result = False
        console.profuse("Need Boolean, if {0}[{1}]: = {2}\n".format(
            state.name, stateField, result)) 


        return result

class DirectNeed(Need):
    """DirectNeed Need

       if state comparison goal [+- tolerance]
    """
    def __init__(self, **kw):
        """Initialization method for instance.

           inherited attributes:

              .name = unique name for action instance
              .store = shared data store

           parameters:
              state = share of state
              stateField = field key
              comparison
              goal
              tolerance

        """
        super(DirectNeed,self).__init__(**kw)  

    def action(self, state, stateField, comparison, goal, tolerance, **kw):
        """Check if state[field] comparison to goal +- tolerance is True"""

        result = self.Check(state[stateField], comparison, goal, tolerance)
        console.profuse("Need Direct, if {0}[{1}] {2} {3} +- %s: = {4}\n".format(
            state.name, stateField, comparison, goal, tolerance, result))     

        return result

class IndirectNeed(Need):
    """IndirectNeed Need

       if state comparison goal [+- tolerance]
    """
    def __init__(self, **kw):
        """Initialization method for instance.

           inherited attributes:

              .name = unique name for action instance
              .store = shared data store

           parameters:
              state = share of state
              stateField = field key
              comparison
              goal
              goalField
              tolerance

        """
        super(IndirectNeed,self).__init__(**kw)  

    def action(self, state, stateField, comparison, goal, goalField, tolerance, **kw):
        """Check if state[field] comparison to goal[goalField] +- tolerance is True"""

        result = self.Check(state[stateField], comparison, goal[goalField], tolerance)
        console.profuse("Need Indirect, if {0}[{1}] {2} {3}[{4}] +- %s: = {5}\n".format(
            state.name, stateField, comparison, goal, goalField, tolerance, result))     

        return result

def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    test()
