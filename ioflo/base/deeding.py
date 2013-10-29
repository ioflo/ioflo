"""deeding.py deed module


"""
print "module %s" % __name__

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

from .consoling import getConsole
console = getConsole()

#debugging support
#debug = True
debug = False

#Constant Definitions

def CreateInstances(store):
    """Create action instances
       must be function so can recreate after clear registry
    """
    pass


#Class definitions
#instance should be only one, maybe should use singleton or borg

class Deed(acting.Actor):
    """Deed Actor Patron Registry Class for behaviors like arbiters and controls

       deeds are recur actions
       but building deed from hafscript checks 
       if deed instance has restart attribute then
          adds entry action to call restart method of deed
       TimeLapse deeds have restart method attribute

       inherited attributes
          .name = unique name for actor instance
          .store = shared data store

    """
    #create Deed specific registry name space
    Counter = 0  
    Names = {}

    def __init__(self,  **kw):
        """Initialization method for instance. """
        if 'preface' not in kw:
            kw['preface'] = 'Deed'

        super(Deed,self).__init__(**kw)  


class SinceDeed(Deed):
    """SinceDeed Deed Actor Patron Registry Class
       Generic Super Class acts if input updated Since last time ran
       knows time of current iteration and last time processed input

       Should be subclassed

       inherited attributes
          .name = unique name for actor instance
          .store = shared data store

       local attributes
          .stamp = current time of deed evaluation in seconds

    """
    def __init__(self, **kw):
        """Initialize Instance """
        if 'preface' not in kw:
            kw['preface'] = 'SimulatorDeed'

        #call super class method
        super(SinceDeed,self).__init__( **kw)  

        self.stamp = None

    def action(self, **kw):
        """Should call this on superclass  as first step of subclass action method  """
        console.profuse("Actioning SinceDeed  {0}\n".format(self.name))
        self.stamp = self.store.stamp

    def expose(self):
        """     """
        print "Deed %s stamp = %s" % (self.name, self.stamp)

class LapseDeed(Deed):
    """LapseDeed Deed Actor Patron Registry Class
       Generic Super Class for  controllers, simulators, and deed that needs to
       keep track of lapsed time between iterations.
       Should be subclassed

       inherited attributes
          .name = unique name for actor instance
          .store = shared data store

       local attributes
          .stamp =  current time deed evaluation in seconds
          .lapse = elapsed time betweeen evaluations of a behavior

       has restart method when resuming after noncontiguous time interruption
       builder creates implicit entry action of restarter for deed
    """
    def __init__(self, **kw):
        """Initialize Instance """
        if 'preface' not in kw:
            kw['preface'] = 'SimulatorDeed'

        #call super class method
        super(LapseDeed,self).__init__( **kw)  

        self.stamp = None
        self.lapse = 0.0 #elapsed time in seconds between updates calculated on update


    def restart(self):
        """Restart Deed  """
        console.profuse("Restarting LapseDeed  {0}\n".format(self.name))

    def updateLapse(self):
        """Calculates a new time lapse based on stamp or if stamp is None then use store stamp
           updates .stamp
        """
        stampLast, self.stamp = self.stamp, self.store.stamp

        #lapse must not be negative
        try:
            self.lapse = max( 0.0, self.stamp - stampLast) #compute lapse

        except TypeError: #either/both self.store.stamp or self.stamp is not a number
            #So if store is number then makes stamp number so next time lapse is non zero
            #If store.stamp is not a number then lapse will always be zero
            self.stamp = self.store.stamp #so make stamp same as store 
            self.lapse = 0.0

    def action(self, **kw):
        """    """
        console.profuse("Actioning LapseDeed  {0}\n".format(self.name))
        self.updateLapse()


    def expose(self):
        """     """
        print "Deed %s stamp = %s lapse = %s" % (self.name, self.stamp, self.lapse)


def Test():
    """Module Common self test

    """
    global debug

    oldDebug = debug
    debug = True #turn on debug during tes


    debug = oldDebug #restore debug value


if __name__ == "__main__":
    test()

