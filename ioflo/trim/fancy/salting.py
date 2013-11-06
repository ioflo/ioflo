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

import salt.client.api

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
    
       init protocol: (path, ival, mine, prim)
    """

    saltEventerJob = Eventer(name = 'saltEventerJob', store=store, 
                                event=('event', odict(), True, True), 
                                req=('req', deque(), False, True), 
                                sub=('sub', odict(), True), 
                                period=('.meta.period', None),
                                parm=('parm', dict(throttle=0.0, tag='salt/job'), True), 
                                proem='.salt.eventer.job', )
                                

    #saltBosserOverload = Bosser(name = 'saltBosserOverload', store=store,
                                #group='salt.bosser.overload',
                                #oflo='state.overload', 
                                #iflo='goal.overload',
                                #poolIds='salt.pool.ids',
                                #poolStatus='salt.pool.status',
                                #event='event', 
                                #parms=dict(high=1.0, low=0.5,))
    
    

class Eventer(deeding.LapseDeed):
    """Eventer LapseDeed Deed Class
       Salt Eventer

    """

    def __init__(self, event=None, req=None, sub=None, period=None, parm=None, proem="", **kw):
        """ Initialize instance
        
        arguments
            event is share initer of event deque
            sub is share initer of subscribers odict
            req is share initer of subscriptions request deque
            period is share path name of min period of (skedder (meta) or framer)
            proem is node path name in store
            parm = proem.parm field values
                throttle
            
        inherited attributes
            .name is actor name string
            .store is data store ref
            .stamp is time stamp
            .lapse is time lapse between updates of controller
            
        local attributes created by init
            .node is proem node
            .oflos is ref to out flos odict
            .iflos is ref to in flos odict
            
            .event is ref to event share, value is deque of events incoming
            .req is ref to subscription request share, value is deque of subscription requests
                each field key is tag, value is list of shares, startswith to match
            .sub is ref to sub share, with tag fields, value list of subscriber shares
                each subscriber share value is deque of events put there by Eventer
            .period is ref to period share
            .parm is ref to node.parm share
                throttle is divisor or period max portion of period to consume each run
        

        """
        #call super class method
        super(Eventer, self).__init__(**kw)  
        
        self.init(proem=proem, event=event, sub=sub, req=req, period=period, parm=parm)
        
        
    def reinit(self, **kw):
        """ Override default Deed method"""
        
        self.client = salt.client.api.APIClient()
        
    #def restart(self):
        #"""Restart Throttle"""
        #pass


    def action(self, **kw):
        """ Process subscriptions and publications of events
            subscription request are duples (tag prefix, share)
            value is 
        """
        super(Eventer,self).action(**kw) #computes lapse here

        #self.elapsed.value = self.lapse  #update share

        if self.lapse <= 0.0: #test throttle
            pass
        
        if not self.sub.value: #no subscriptions so request one
            subscriber = self.store.create("salt.sub.test").update(value=deque())
            self.req.value.append(("salt/job/", subscriber))
        
        #loop to process sub requests
        while self.req.value: # some requests
            tag, share = self.req.value.popleft()
            console.verbose("Eventer '{0}' subreq tag '{1}' share '{2}'\n".format(self.name, tag, share.name))
            if tag in self.sub.value and self.sub.value[tag] != share:
                self.sub.value[tag].append(share)
            else: #first time
                self.sub.value[tag] = [share]
        
        #eventually have realtime check to throttle ratio limit time 
        # in event loop processing events
        period = self.period.value
        throttle = self.parm.data.throttle
        try:
            limit =  period / throttle
        except ZeroDivisionError:
            limit = 0 # no limit
        
        #loop to get and process events from salt client api
        etag = self.parm.data.tag
        while True: #event loop
            edata =  self.client.get_event(wait=0.01, tag=etag, full=True)
            if not edata:
                break
            utag = '/'.join([edata['tag'], edata['data']['_stamp']])
            edata['data']['utag'] = utag
            self.event.value[utag] = edata #pub to odict of all events
            console.verbose("Eventer '{0}' event tag '{1}'\n".format(self.name, utag))
            # loop to pub event to subscribers
            for tag, shares in self.sub.value.items():
                if edata['tag'].startswith(tag):
                    for share in shares:
                        share.value.append(edata)

        return None

    def expose(self):
        """prints out controller state"""
        pass

class Bosser(deeding.LapseDeed):
    """Bosser LapseDeed Deed Class
       Salt Bosser

    """

    def __init__(self, event=None, req=None, sub=None, period=None, parm=None, proem="", **kw):
        """Initialize instance

        arguments
            event is share initer of event deque
            sub is share initer of subscribers odict
            req is share initer of subscriptions request deque
            period is share path name of min period of (skedder (meta) or framer)
            proem is node path name in store
            parm = proem.parm field values
                throttle
            
        inherited attributes
            .name is actor name string
            .store is data store ref
            .stamp is time stamp
            .lapse is time lapse between updates of controller
            
        local attributes created by init
            .node is proem node
            .oflos is ref to out flos odict
            .iflos is ref to in flos odict
            
            .event is ref to event share, value is deque of events incoming
            .req is ref to subscription request share, value is deque of subscription requests
                each field key is tag, value is list of shares, startswith to match
            .sub is ref to sub share, with tag fields, value list of subscriber shares
                each subscriber share value is deque of events put there by Eventer
            .period is ref to period share
            .parm is ref to node.parm share
                throttle is divisor or period max portion of period to consume each run
           
        """
        #call super class method
        super(Bosser, self).__init__(**kw)  

        self.init(proem=proem, event=event, sub=sub, req=req, period=period, parm=parm)
        
    def reinit(self, **kw):
        """ Override default Deed method"""
        self.client = salt.client.api.APIClient()    
    
    #def restart(self):
        #"""Restart """
        #pass


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
