"""salting.py saltstack integration behaviors

"""
print "module %s" % __name__

from collections import deque

from ...base.odicting import odict
from ...base.globaling import *

from ...base import aiding
from ...base import storing 
from ...base import deeding

from ...base.consoling import getConsole
console = getConsole()

#debugging support
#debug = True
debug = False


def CreateInstances(store):
    """Create action instances. Recreate with each new house after clear registry
    """

    saltEventerJob = Eventer(name = 'saltEventerJob', store = store, 
                                       group = 'salt.eventer.job', output = 'salt.eventer.job.event',
                                       input_ = 'salt.eventer.job.sub', period='meta.period', 
                                       parms = dict(throttle = 0.0))

    saltBosserCluster = Bosser(name = 'saltBosserCluster', store = store,
                                         group = 'salt.bosser.pool', output = 'state.pool.overload', 
                                         input_ = 'goal.pool.overload', pool = 'pool', event = 'event', 
                                         parms = dict(high = 1.0, low = 0.5,))
    
    

class Eventer(deeding.LapseDeed):
    """Eventer LapseDeed Deed Class
       Salt Eventer

    """

    def __init__(self, group, output, input_, parms = None, **kw):
        """Initialize instance

           group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    throttle = divisor

              group.

           output is path name of share latest event

           input_ = path name of input subscription queue
           period = path name of throttle period (framer or skedder)
           parms is optional dictionary of initial values for group.parm fields

           instance attributes

           .output = reference to output share
           .group = copy of group name
           .parm = reference to input parameter share
           .period = reference to throttle period

           inherited instance attributes
           .stamp = time stamp
           .lapse = time lapse between updates of controller
           .name
           .store

        """
        #call super class method
        super(Eventer, self).__init__(**kw)  

        self.lapse = 0.0 #time lapse in seconds calculated on update

        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        parms = parms or dict(throttle = 0.0,)
        self.parm.create(**parms)

        self.output = self.store.create(output).update(value = 0.0) #force update not just create

        self.input_ = self.store.create(input_).create(value = 0.0) #create if not exist


    def restart(self):
        """Restart Throttle"""
        pass


    def action(self, **kw):
        """update will use inputs from store
           assumes all inputs come from deeds that use value as their output attribute name
        """
        super(Eventer,self).action(**kw) #computes lapse here

        self.elapsed.value = self.lapse  #update share

        if self.lapse <= 0.0: #test throttle
            pass

        input_ = self.input_.value #get from store
        
        self.output.value = out

        return None

    def expose(self):
        """prints out controller state"""
        pass

class Bosser(deeding.LapseDeed):
    """Bosser LapseDeed Deed Class
       Salt Bosser

    """

    def __init__(self, group, output, input_, parms = None, **kw):
        """Initialize instance

           group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    throttle = divisor

              group.

           output is path name of share latest event

           input_ = path name of input subscription queue
           period = path name of throttle period (framer or skedder)
           parms is optional dictionary of initial values for group.parm fields

           instance attributes

           .output = reference to output share
           .group = copy of group name
           .parm = reference to input parameter share
           .period = reference to throttle period

           inherited instance attributes
           .stamp = time stamp
           .lapse = time lapse between updates of controller
           .name
           .store

        """
        #call super class method
        super(Bosser, self).__init__(**kw)  

        self.lapse = 0.0 #time lapse in seconds calculated on update

        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        parms = parms or dict(throttle = 0.0,)
        self.parm.create(**parms)

        self.output = self.store.create(output).update(value = 0.0) #force update not just create

        self.input_ = self.store.create(input_).create(value = 0.0) #create if not exist


    def restart(self):
        """Restart """
        pass


    def action(self, **kw):
        """update will use inputs from store
           assumes all inputs come from deeds that use value as their output attribute name
        """
        super(Bosser,self).action(**kw) #computes lapse here

        self.elapsed.value = self.lapse  #update share

        if self.lapse <= 0.0: #test throttle
            pass

        input_ = self.input_.value #get from store
        
        self.output.value = out

        return None

    def expose(self):
        """ prints out state"""
        pass



def Test():
    """Module Common self test

    """
    global debug

    oldDebug = debug
    debug = True #turn on debug during tes


    debug = oldDebug #restore debug value


if __name__ == "__main__":
    Test()
