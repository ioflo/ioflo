""" salting.py saltstack integration behaviors


Shares

.meta
    .period
        value

.goal
    .overload
            value

.state
    .overload
            value


.salt
    .pool 
        alpha  ms-1 ...
            on off
    .overload
        value
    .autoscale
        .up  
        .down
        .failure
        .abort
        
    .eventer
        .job
        
        .sub
        
        .event
        
    .bosser
        .overload
            .event
            .parm
                high low



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

    saltEventerJob = Eventer(name = 'saltEventerJob', store=store, 
                                group='salt.eventer.job',
                                oflo='salt.eventer.job.event',
                                iflo='salt.eventer.job.sub',
                                period='meta.period', 
                                parms=dict(throttle=0.0, ))

    saltBosserOverload = Bosser(name = 'saltBosserOverload', store=store,
                                group='salt.bosser.overload',
                                oflo='state.overload', 
                                iflo='goal.overload',
                                pool='salt.pool',
                                event='event', 
                                parms=dict(high=1.0, low=0.5,))
    
    

class Eventer(deeding.LapseDeed):
    """Eventer LapseDeed Deed Class
       Salt Eventer

    """

    def __init__(self, group, oflo, iflo, period, parms=None, **kw):
        """ Initialize instance
        
        arguments
            group is group path name in store
            oflo is share path name of latest event deque
            iflo is share path name of subscriptions deque
            period is share path name of min period of (skedder (meta) or framer)
            parms = optional dictionary of initial values for group.parm fields
            
        inherited attributes
            .name is actor name string
            .store is data store ref
            .stamp is time stamp
            .lapse is time lapse between updates of controller
            
        local attributes
            .group is group name string
            .oflo is ref to outflo share
            .iflo is ref to inflo share
            .period is ref to period share
            .parm is ref to group.parm share
            
 
        """
        #call super class method
        super(Eventer, self).__init__(**kw)  

        self.lapse = 0.0 #time lapse in seconds calculated on update
        self.group = group
        self.parm = self.store.create(group + '.parm') #create if not exist
        self.parm.create(**(parms or dict(throttle = 0.0))) #create and update if not exist

        self.oflo = self.store.create(oflo).update(value = deque()) #create and force update
        self.iflo = self.store.create(iflo).create(value = deque()) #create if not exist 
        self.period = self.store.create(period)

    def restart(self):
        """Restart Throttle"""
        pass


    def action(self, **kw):
        """ Process subscriptions and publications of events
        """
        super(Eventer,self).action(**kw) #computes lapse here

        self.elapsed.value = self.lapse  #update share

        if self.lapse <= 0.0: #test throttle
            pass
        
        #loop to process subs
        iflo = self.iflo.value.popLeft() #get from store
        period = self.period.value
        throttle = self.parm.data.throttle
        #eventually have realtime loop to determine max time to process events
        # loop to get events here and pub to subs
        #self.oflo.value.append(iflo)

        return None

    def expose(self):
        """prints out controller state"""
        pass

class Bosser(deeding.LapseDeed):
    """Bosser LapseDeed Deed Class
       Salt Bosser

    """

    def __init__(self, group, oflo, iflo, pool, event, parms=None, **kw):
        """Initialize instance

        arguments
            group is group path name in store
            oflo is share path name of latest event deque
            iflo is share path name of subscriptions deque
            period is share path name of min period of (skedder (meta) or framer)
            parms = optional dictionary of initial values for group.parm fields
            
        inherited attributes
            .name is actor name string
            .store is data store ref
            .stamp is time stamp
            .lapse is time lapse between updates of controller
                
        local attributes
            .group = group name string
            .oflo = reference to oflo share
            .iflo = reference to iflo share
            .parm = reference to input parameter share
           
        """
        #call super class method
        super(Bosser, self).__init__(**kw)  

        self.lapse = 0.0 #time lapse in seconds calculated on update

        self.group = group
        self.parm = self.store.create(group + '.parm')#create if not exist
        self.parm.create(**(parms or dict(high=1.0, low=0.75)))
        self.oflo = self.store.create(oflo).update(value = 0.0) #force update not just create
        self.iflo = self.store.create(iflo).create(value = 0.0) #create if not exist
        
        self.pool = self.store.create(pool)
        self.event = self.store.create(event).create(value=deque())

    def restart(self):
        """Restart """
        pass


    def action(self, **kw):
        """update will use inputs from store
           assumes all inputs come from deeds that use value as their oflo attribute name
        """
        super(Bosser,self).action(**kw) #computes lapse here

        self.elapsed.value = self.lapse  #update share

        if self.lapse <= 0.0: #test throttle
            pass

        iflo = self.iflo.value #get from store
        
        self.oflo.value = out

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
