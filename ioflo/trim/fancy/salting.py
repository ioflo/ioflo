""" salting.py saltstack integration behaviors


Shares

.meta
    .period
        value

.salt 
   .pool 
      .m1 
         mid  status  overload  loadavg  numcpus alive
      .m2 
         mid  status  overload  loadavg  numcpus alive
      .m3 
         mid  status  overload  loadavg  numcpus alive
      .m4 
         mid  status  overload  loadavg  numcpus alive
      .m5 
         mid  status  overload  loadavg  numcpus alive
      .m6 
         mid  status  overload  loadavg  numcpus alive
    
   .autoscale 
      .limit 
         up  down 
   .eventer 
      .job 
         .parm 
            tag  throttle 
         .req 
            value 
         .pub 
            value 
         .event 
            value 
   .overload 
      value
      
   .status
        overload onCount offCount healthy deadCount
   
   
   .bosser 
      .overload 
         .event 
            value 
         .parm 
            value 

init salt.pool.m1 to mid "alpha" status on
init salt.pool.m2 to mid "ms-0" status on 
init salt.pool.m3 to mid "ms-1" status on 
init salt.pool.m4 to mid "ms-2" status off 
init salt.pool.m5 to mid "ms-3" status off 
init salt.pool.m6 to mid "ms-4" status off 


"""
#print "module %s" % __name__

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
    
       init protocol:  inode  and (ipath, ival, iown)
    """
    EventerSalt(name = 'eventerSalt', store=store).ioinit.update(
        period= '.meta.period',
        req=('req', deque()), 
        event=('event', odict(), True),
        pub=('pub', odict(), True), 
        parm=('parm', odict(throttle=0.0, tag='salt'), True),)      
    
    EventerSalt(name = 'saltEventerJob', store=store).ioinit.update(
        period=('.meta.period',),
        req=('req', deque()), 
        event=('event', odict(), True),
        pub=('pub', odict(), True), 
        parm=('parm', odict(throttle=0.0, tag='salt/job'), True), 
        inode='.salt.eventer.job', )
                                
    OverloadPoolerSalt(name = 'saltPoolerOverload', store=store).ioinit.update(
        status=('.salt.status', odict([('overload', 0.0), ('onCount', 0), ('offCount', 0)]), True),
        pool= '.salt.pool.', 
        parm= 'parm', 
        inode='.salt.pooler.overload',)
    
    PingPoolBosserSalt(name = 'saltBosserPoolPing', store=store).ioinit.update(
        event=('event', deque()),
        pool='.salt.pool.', 
        status=('.salt.status', odict([('healthy', 0.0), ('deadCount', 0)])), 
        req=('.salt.eventer.job.req', deque(), True),
        parm=('parm', odict(timeout=5.0), True), 
        inode='.salt.bosser.pool.ping',)    
    
    NumcpuPoolBosserSalt(name = 'saltBosserPoolNumcpu', store=store).ioinit.update(
        event=('event', deque()),
        pool=('.salt.pool.', ), 
        req=('.salt.eventer.job.req', deque(), True),
        parm=('parm', odict(), True), 
        inode='.salt.bosser.pool.numcpu',)
    
    LoadavgPoolBosserSalt(name = 'saltBosserPoolLoadavg', store=store).ioinit.update(
        event=('event', deque()),
        pool=('.salt.pool.', ),
        req=('.salt.eventer.job.req', deque(), True),
        parm=('parm', odict(), True), 
        inode='.salt.bosser.pool.loadavg',)        
    
class SaltDeed(deeding.Deed):
    """ Base class for Deeds that interface with Salt
        Adds salt client interface attribute .client
        
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of controller
            
        local attributes
            .client is salt client interface
    
    """
    def __init__(self, **kw):
        """ Initialize instance """
        #call super class method
        super(SaltDeed, self).__init__(**kw)
        
        self.client = salt.client.api.APIClient()    

class EventerSalt(SaltDeed, deeding.SinceDeed):
    """ Salt Eventer
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .client is salt client interface
            
            
        arguments to update .ioinit attribute
            event is share initer of event deque
            pub is share initer of publications to subscribers odict
            req is share initer of subscriptions request deque
            period is share path name of min period of (skedder (meta) or framer)
            parm = inode.parm field values
                throttle
            inode is node path name in store

        local attributes created by initio
            .inode is inode node
            .oflos is ref to out flos odict
            .iflos is ref to in flos odict
            
            .event is ref to event share, value is deque of events incoming
            .req is ref to subscription request share, value is deque of subscription requests
                each request is duple of tag, share
            .pub is ref to pub share, with tag fields, value list of publication to subscriber shares
                each pub share value is deque of events put there by Eventer
            .period is ref to period share
            .parm is ref to node.parm share
                throttle is divisor or period max portion of period to consume each run
    """
             

    def action(self, **kw):
        """ Process subscriptions and publications of events
            subscription request are duples (tag prefix, share)
            value is 
        """
        super(EventerSalt, self).action(**kw) #updates .stamp here
        
        #if not self.pub.value: #no pub to subscriptions so request one
            #publication = self.store.create("salt.pub.test").update(value=deque())
            #self.req.value.append(("salt/job/", publication))
        
        #loop to process sub requests
        while self.req.value: # some requests
            tag, share = self.req.value.popleft()
            console.verbose("     Eventer '{0}' subreq tag '{1}' share '{2}'\n".format(self.name, tag, share.name))
            if tag in self.pub.value and self.pub.value[tag] != share:
                self.pub.value[tag].append(share)
            else: #first time
                self.pub.value[tag] = [share]
        
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
            self.event.stampNow() # since modified value in place
            console.verbose("     Eventer '{0}' event tag '{1}'\n".format(self.name, utag))
            # loop to pub event to publications for subscribers
            for tag, shares in self.pub.value.items():
                if edata['tag'].startswith(tag):
                    for share in shares:
                        share.value.append(edata)
                        share.stampNow() # modified in place

        return None


class OverloadPoolerSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Pooler Overload
        Computer the overload percentage of each active member of pool and
        the average overload for the pool
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            
        arguments to update of .ioinit attribute
            status is share initer of current pool status 
            pool is node initer of shares in node are the pool minions
            parm = inode.parm field values
            inode is node path name in store
            
            
        local attributes created by initio
            .inode is inode node
            .status is ref to status share, field overload is computed overload
            .pool is ref to pool node. Each value is share with minion details
                mid, status, overload, loadavg, numcpu
            .parm is ref to node.parm share

    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(OverloadPoolerSalt, self).__init__(**kw)
        
    def postinitio(self):
        """ initialize poolees from pool"""
        for key, share in self.pool.items():
            share.data.overload = None
        self.status.data.overload = 0.0
        self.status.data.onCount = 0
        self.status.data.offCount = 0

    def action(self, **kw):
        """ update overloads for pool"""
        super(OverloadPoolerSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        for share in self.pool.values():
            if share.data.status: #pool member is on
                if share.get('loadavg') is not None and share.get('numcpu') is not None:
                    try:
                        share.update(overload=(share.data.loadavg / share.data.numcpu))
                        console.terse("     {0} overload is {1:0.4f}\n".format(
                             share.data.mid, share.data.overload))
                    except ZeroDivisionError:
                        pass
                    except TypeError:
                        pass
            else: # turned off clear stale overload, numcpu, loadavg
                share.update(overload=None)
                
        count = 0
        overloadSum = 0.0
        for share in self.pool.values():
            overload = share.get('overload')
            if overload is not None:
                overloadSum += overload
                count += 1
        
        if count:
            self.status.update(overload=overloadSum / count,
                               onCount=count, offCount= len(self.pool) -  count)
            console.terse("     Pool overload is {0:0.4f} with onCount {1}\n".format(
                self.status.data.overload,  count))
            console.terse("     Salt Status stamp {0:0.4f} Store stamp {1:0.4f}\n".format(
                            self.status.stamp, self.store.stamp))            
                
        return None

class PingPoolBosserSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Bosser Pool Ping
        Deed to determine if any of the 'on' minions in pool are down
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            .poolees is odict mapping minion ids to pool shares
            
        arguments to update of .ioinit attribute
            status is share initer of pool status uses health field
            event is share initer of events deque() subbed from eventer
            req is share initer of subscription requests deque() for eventer
            pool is node initer of shares in node are the pool minions
            parm = inode.parm field values
            inode is node path name in store
            
            
        local attributes created by initio
            .inode is inode node
            .status is ref to pool status share, healthy deadCount
            .event is ref to event share, value is deque of events subbed from eventer
            .req is ref to subscription request share, value is deque of subscription requests
                each request is duple of tag, share
            .pool is ref to pool node. Each value is share with minion details
                mid, status, overload, loadavg, numcpu
            .parm is ref to node.parm share
                timeout is time in seconds whereupon ping has failed
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(PingPoolBosserSalt, self).__init__(**kw)
        
        self.poolees = odict() #mapping between pool shares and mid
        self.cycleStart = None #timestamp start of ping cycle
        self.alives = odict() #mapping of mids to boolean alive in given cycle

    def postinitio(self):
        """ initialize poolees from pool"""
        for key, share in self.pool.items():
            self.poolees[share.data.mid] = share #map minion id to share
            self.alives[share.data.mid] = False
            share.data.alive = None
        self.status.data.healthy=False
        self.status.data.deadCount=0
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(PingPoolBosserSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        while self.event.value: #deque of events is not empty
            edata = self.event.value.popleft()
            console.verbose("     Bosser {0} got event {1}\n".format(self.name, edata['tag']))
            data = edata['data']
            if data.get('success'): #only ret events
                self.poolees[data['id']].update(alive=data['return'])
                self.alives[data['id']] = True
                
        for share in self.pool.values(): # clear stale active
            if not share.data.status: #pool member is off
                share.update(alive=None)           
            
        if self.cycleStart is not None:
            # see if all are alive or any still dead
            alive = True # True when any on are dead
            deadCount = 0
            for share in self.pool.values():
                if share.data.status: #pool member is on
                    if not self.alives[share.data.mid]: #still dead
                        alive = False
                        deadCount += 1
            
            if alive: # immediately update if all alive
                self.status.update(healthy=alive, deadCount=deadCount)
                console.terse("     Pool healthy is {0}\n".format(
                    self.status.data.healthy))
                
            else: # dead so far but only update as unhealthy (dead) at end of cycle
                if (self.stamp - self.cycleStart) > self.parm.data.timeout:
                    # cycle completed 
                    self.status.update(deadCount=deadCount)
                    for share in self.pool.values():
                        if share.data.status: #pool member is on
                            if not self.alives[share.data.mid]: #still dead
                                share.update(alive=False) #this one dead
                    self.status.update(healthy=False)
                    console.terse("     Pool healthy is {0} with {1} dead minions\n".format(
                        self.status.data.healthy, self.status.data.deadCount))
                    self.cycleStart = None
                           
        if self.cycleStart is None: #start new cycle
            self.cycleStart =  self.stamp
            
            for key in self.alives: #mark all as dead.
                self.alives[key] = False 
            
            target = ','.join([mid for mid, share in self.poolees.items() if share.data.status])
            
            cmd = dict(mode='async', fun='test.ping',
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
                    self.req.stampNow()
                
        return None
    
    
class NumcpuPoolBosserSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Bosser Pool Numcpu
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            .poolees is odict mapping minion ids to pool shares
            
        arguments to update of .ioinit attribute
            event is share initer of events deque() subbed from eventer
            req is share initer of subscription requests deque() for eventer
            pool is node initer of shares in node are the pool minions
            parm = inode.parm field values
            inode is node path name in store
            
            
        local attributes created by initio
            .inode is inode node
            .event is ref to event share, value is deque of events subbed from eventer
            .req is ref to subscription request share, value is deque of subscription requests
                each request is duple of tag, share
            .pool is ref to pool node. Each value is share with minion details
                mid, status, overload, loadavg, numcpu
            .parm is ref to node.parm share

    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(NumcpuPoolBosserSalt, self).__init__(**kw)
        
        self.poolees = odict() #mapping between pool shares and mid

    def postinitio(self):
        """ initialize poolees from pool"""
        for key, share in self.pool.items():
            self.poolees[share.data.mid] = share #map minion id to share
            share.data.numcpu = None
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(NumcpuPoolBosserSalt, self).action(**kw) #updates .stamp and .lapse here

        while self.event.value: #deque of events is not empty
            edata = self.event.value.popleft()
            console.verbose("     Bosser {0} got event {1}\n".format(self.name, edata['tag']))
            data = edata['data']
            if data.get('success'): #only ret events
                self.poolees[data['id']].update(numcpu=data['return'])
                
        for share in self.pool.values(): # clear stale numcpu
            if not share.data.status: #pool member is off
                share.update(numcpu=None)
            
        target = ','.join([mid for mid, share in self.poolees.items() if share.data.status])
        
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
                self.req.stampNow()
                     
        return None

class LoadavgPoolBosserSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Bosser Pool Loadavg
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            .poolees is odict mapping minion ids to pool shares
            
        arguments to update of .ioinit attribute
            event is share initer of events deque() subbed from eventer
            req is share initer of subscription requests deque() for eventer
            pool is node initer of shares in node are the pool minions
            parm = inode.parm field values
            inode is node path name in store
            
            
        local attributes created by initio
            .inode is inode node
            .event is ref to event share, value is deque of events subbed from eventer
            .req is ref to subscription request share, value is deque of subscription requests
                each request is duple of tag, share
            .pool is ref to pool node. Each value is share with minion details
                mid, status, overload, loadavg, numcpu
            .parm is ref to node.parm share
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(LoadavgPoolBosserSalt, self).__init__(**kw)
        
        self.poolees = odict() #mapping between pool shares and mid

    def postinitio(self):
        """ initialize poolees from pool"""
        for key, share in self.pool.items():
            self.poolees[share.data.mid] = share #map minion id to share
            share.data.loadavg = None
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(LoadavgPoolBosserSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        while self.event.value: #deque of events is not empty
            edata = self.event.value.popleft()
            console.verbose("     Bosser {0} got event {1}\n".format(self.name, edata['tag']))
            data = edata['data']
            if data.get('success'): #only ret events
                self.poolees[data['id']].update(loadavg=data['return']['1-min'])
        
        for share in self.pool.values(): # clear stale loadavg
            if not share.data.status: #pool member is off
                share.data.loadavg = None        
            
        target = ','.join([mid for mid, share in self.poolees.items() if share.data.status])
        
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
                self.req.stampNow()
                
        return None
    

def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    Test()
