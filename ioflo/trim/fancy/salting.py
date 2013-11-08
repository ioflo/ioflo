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
        .mid
            alpha  ms_1 ...
        .status
            alpha ms_1 ...
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


init salt.pool.mid to alpha "alpha" ms_0 "ms-0" ms_1 "ms-1" ms_2 "ms_2" \
      ms_3 "ms-3" ms_4 "ms-4" 
init salt.pool.status to alpha on ms_0 on ms_1 on ms_2 off ms_3 off ms_4 off 
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


def CreateInstances(store):
    """Create action instances. Recreate with each new house after clear registry
    
       init protocol: (ipath, ival, iown, ipri)
    """

    Eventer(name = 'saltEventerJob', store=store).ioinit.update(
        event=('event', odict(), True, True), 
        req=('req', deque(), False, True), 
        sub=('sub', odict(), True), 
        period=('.meta.period', None),
        parm=('parm', dict(throttle=0.0, tag='salt/job'), True), 
        proem='.salt.eventer.job', )  
                                

    Bosser(name = 'saltBosserOverload', store=store).ioinit.update(
        overload=('.salt.overload', 0.0, True, True),
        event=('event', deque(), False, True),
        req=('.salt.eventer.job.req', deque(), True), 
        poolMid=('.salt.pool.mid', ), 
        poolStatus=('.salt.pool.status', ),
        parm=('parm', dict(), True), 
        proem='salt.bosser.overload',)
    
    

class Eventer(deeding.LapseDeed):
    """Eventer LapseDeed Deed Class
       Salt Eventer

    """

    def __init__(self, **kw):
        """ Initialize instance
        
        arguments
            event is share initer of event deque
            sub is share initer of subscribers odict
            req is share initer of subscriptions request deque
            period is share path name of min period of (skedder (meta) or framer)
            parm = proem.parm field values
                throttle
            proem is node path name in store
            
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of controller
            
        local attributes
            .client is salt client interface
            
        local attributes created by initio
            .node is proem node
            .oflos is ref to out flos odict
            .iflos is ref to in flos odict
            
            .event is ref to event share, value is deque of events incoming
            .req is ref to subscription request share, value is deque of subscription requests
                each request is duple of tag, share
            .sub is ref to sub share, with tag fields, value list of subscriber shares
                each subscriber share value is deque of events put there by Eventer
            .period is ref to period share
            .parm is ref to node.parm share
                throttle is divisor or period max portion of period to consume each run
        

        """
        #call super class method
        super(Eventer, self).__init__(**kw)
        
        self.client = salt.client.api.APIClient()
             
        

    def action(self, **kw):
        """ Process subscriptions and publications of events
            subscription request are duples (tag prefix, share)
            value is 
        """
        super(Eventer,self).action(**kw) #computes lapse here

        if self.lapse <= 0.0:
            pass
        
        #if not self.sub.value: #no subscriptions so request one
            #subscriber = self.store.create("salt.sub.test").update(value=deque())
            #self.req.value.append(("salt/job/", subscriber))
        
        #loop to process sub requests
        while self.req.value: # some requests
            tag, share = self.req.value.popleft()
            console.verbose("     Eventer '{0}' subreq tag '{1}' share '{2}'\n".format(self.name, tag, share.name))
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
            console.verbose("     Eventer '{0}' event tag '{1}'\n".format(self.name, utag))
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

    def __init__(self, **kw):
        """Initialize instance

        arguments
            overload is share initer of current overload value for pool
            event is share initer of events deque() subbed from eventer
            req is share initer of subscription requests deque() for eventer
            poolMid is share initer of pool minon ids
            poolStatus is share initer of pool minon status on or off
            parm = proem.parm field values
            proem is node path name in store
            
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of controller
            
        local attributes
            .client is interface to salt
            .loadavgs is dict of loadavg for each minion in pool
            .cpus is dict of cpus for each minion in pool
            .overloads is dict of overloads for each minion in pool
            
        local attributes created by initio
            .node is proem node
            .oflos is ref to out flos odict
            .iflos is ref to in flos odict
            
            .overload is ref to overload share, value is computed overload
            .event is ref to event share, value is deque of events subbed from eventer
            .req is ref to subscription request share, value is deque of subscription requests
                each request is duple of tag, share
            .poolMid is ref to poolMid share, of all minion ids in pool, each value is mid
            .poolStatus if ref to pooStatus share is on off status of minion in pool
            .parm is ref to node.parm share
                
           
        """
        #call super class method
        super(Bosser, self).__init__(**kw)
        
        self.client = salt.client.api.APIClient()
        self.loadavgs = {}
        self.cpus = {}
        self.overloads = {}


    def action(self, **kw):
        """ check for events
            update overload
            poll on minions for new overload
            request events for associated jobid
           
        """
        super(Bosser,self).action(**kw) #computes lapse here

        if self.lapse <= 0.0:
            pass
        
        while self.event.value: #deque of events is not empty
            edata = self.event.value.popleft()
            console.verbose("     Bosser {0} got event {1}\n".format(self.name, edata['tag']))
            data = edata['data']
            if data.get('success'): #only ret events
                if data['fun'] == 'status.loadavg':
                    self.loadavgs[data['id']] = data['return']['1-min']
                if data['fun'] == 'grains.get':
                    self.cpus[data['id']] = data['return']
        

        for key, mid in self.poolMid.items():
            if self.poolStatus.get(key): #pool member is on
                if self.loadavgs.get(mid):
                    try:
                        self.overloads[mid] = self.loadavgs[mid] / self.cpus[mid]
                    except ZeroDivisionError:
                        pass
            else: # turned off so delete stale overload
                if mid in self.overloads:
                    del self.overloads[mid]
                    
        
        count = len(self.overloads)
        if count and count == sum([1 for key in self.poolStatus if self.poolStatus[key]]):
            overload = sum(self.overloads.values()) / count
            self.overload.value = overload
            console.terse("     Overload updated to {0:0.4f}\n".format(overload))
                
        target = ','.join([mid for key, mid in self.poolMid.items() if self.poolStatus[key]])
        
        cmd = dict(mode='async', fun='grains.get', arg=['num_cpus'], 
                           tgt=target, expr_form='list',
                           username='saltwui', password='dissolve', eauth='pam')
                
        result = None
        try:
            result = self.client.run(cmd)
            console.verbose("     Salt command result = {0}\n".format(result))
        except EauthAuthenticationError as ex:
            console.verbose("Eauth failure for salt command {0} with {1}\n".format(cmd, ex))
                      
        if result:
            jid = result.get('jid')
            if jid:
                self.req.value.append(('salt/job/{0}'.format(jid), self.event))        
                     
        
        cmd = dict(mode='async', fun='status.loadavg',
                   tgt=target, expr_form='list',
                   username='saltwui', password='dissolve', eauth='pam')
        
        result = None
        try:
            result = self.client.run(cmd)
            console.verbose("     Salt command result = {0}\n".format(result))
        except EauthAuthenticationError as ex:
            console.terse("Eauth failure for salt command {0} with {1}\n".format(cmd, ex))
                      
        if result:
            jid = result.get('jid')
            if jid:
                self.req.value.append(('salt/job/{0}'.format(jid), self.event))
                
        return None

    def expose(self):
        """ prints out state"""
        pass



def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    Test()
