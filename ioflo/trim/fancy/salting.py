""" salting.py saltstack integration behaviors


Shares

.meta
    .period
        value

.salt
    .autoscale
        .limit 
           high  low 
        
        .status
            .overload
            .count
            .healthy
            .deadCount

        .pool 
            .m1 
               .mid
               .status
               .overload
               .loadavg
               .numcpus
               .alive
            .m2 
               .mid
               .status
               .overload
               .loadavg
               .numcpus
               .alive
            .m3 
               .mid
               .status
               .overload
               .loadavg
               .numcpus
               .alive
            .m4 
               .mid
               .status
               .overload
               .loadavg
               .numcpus
               .alive
            .m5 
               .mid
               .status
               .overload
               .loadavg
               .numcpus
               .alive
            .m6 
               .mid
               .status
               .overload
               .loadavg
               .numcpus
               .alive
            
    .pooler 
        .overload 
            .parm 
           
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
   .bosser 
        .pool 
           .numcpu 
                .parm 
                   value 
                .event 
                   value 
           .loadavg 
                .parm 
                   value 
                .event 
                   value 
           .ping 
                .parm 
                   timeout 
                .event 
                   value 

init salt.autoscale.pool.m1.mid to value "alpha" 
init salt.autoscale.pool.m1.status to value on 

init salt.autoscale.pool.m2.mid to value "ms-0" 
init salt.autoscale.pool.m3.mid to value "ms-1" 
init salt.autoscale.pool.m4.mid to value "ms-2" 
init salt.autoscale.pool.m5.mid to value "ms-3" 
init salt.autoscale.pool.m6.mid to value "ms-4" 


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
        parm=('parm', odict(throttle=0.0, tag='salt/job'), True),)
                                
    OverloadPoolerSalt(name = 'saltPoolerOverload', store=store).ioinit.update(
        pool = '.salt.autoscale.pool.',
        overload = ('.salt.autoscale.status.overload', 0.0, True),
        count = ('.salt.autoscale.status.count', 0, True),)
    
    PingPoolBosserSalt(name = 'saltBosserPoolPing', store=store).ioinit.update(
        pool='.salt.autoscale.pool.',
        healthy = ('.salt.autoscale.status.healthy', None, True),
        deadCount = ('.salt.autoscale.status.deadCount', 0, True),
        event=('event', deque()),
        req=('.salt.eventer.job.req', deque(), True),
        parm=('parm', odict(timeout=5.0), True),)    
    
    NumcpuPoolBosserSalt(name = 'saltBosserPoolNumcpu', store=store).ioinit.update(
        pool='.salt.autoscale.pool.',
        event=('event', deque()),
        req=('.salt.eventer.job.req', deque(), True), )
    
    LoadavgPoolBosserSalt(name = 'saltBosserPoolLoadavg', store=store).ioinit.update(
        pool=('.salt.autoscale.pool.', ),
        event=('event', deque()),
        req=('.salt.eventer.job.req', deque(), True),)        
    
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
            
        local attributes created by initio
            .inode is inode node
            .event is ref to event share, value is deque of events incoming
            .req is ref to subscription request share, value is deque of subscription requests
                each request is duple of tag, share
            .pub is ref to pub share, with tag fields, value list of publication to subscriber shares
                each pub share value is deque of events put there by Eventer
            .period is ref to period share
            .parm is ref to node.parm share with fields
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
            .members = odict of pool members,
                 values are odicts that map to pool member shares
            
        local attributes created by initio
            .inode is inode node
            .pool is ref to pool node.
                Each value is node of pool member
                Each pool member node has shares
                    mid, status, overload, loadavg, numcpu
            .overload is ref share holding computed overload
            .count is ref share holding count of pool members

    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(OverloadPoolerSalt, self).__init__(**kw)
        self.members = odict()
        
    def postinitio(self):
        """ initialize overload of each pool member"""
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))            
            self.members[key]['overload'] = self.store.create('.'.join([node.name, 'overload'])).update(value=0.0)
            self.members[key]['loadavg'] = self.store.create('.'.join([node.name, 'loadavg']))
            self.members[key]['numcpu'] = self.store.create('.'.join([node.name, 'numcpu']))

    def action(self, **kw):
        """ update overloads for pool"""
        super(OverloadPoolerSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        for member in self.members.values():
            if member['status'].value: #pool member is on
                if member['loadavg'].value is not None and  member['numcpu'].value is not None:
                    try:
                        member['overload'].update(value=(member['loadavg'].value / member['numcpu'].value))
                        console.verbose("     {0} overload is {1:0.4f}\n".format(
                             member['mid'].value, member['overload'].value))
                    except ZeroDivisionError:
                        pass
                    except TypeError:
                        pass
            else: # turned off so clear overload
                member['overload'].value = None
                
        count = 0
        overloadSum = 0.0
        for member in self.members.values():
            overload = member['overload'].value
            if overload is not None:
                overloadSum += overload
                count += 1
        
        if count:
            self.overload.update(value=overloadSum / count)
            self.count.update(value=count)
            console.terse("     Pool overload is {0:0.4f} with onCount {1}\n".format(
                self.overload.value,  self.count.value))           
                
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
            .members = odict of pool members by name
                 values are odicts that map to pool member shares
            .mids is odict mapping minion ids to pool member names
            .alives is odict of pool members by name alive in given cycle
            .cycleStart is timestamp start of ping cycle
            
        local attributes created by initio
            .inode is inode node
            .pool is ref to pool node.
                Each value is node of pool member
                Each pool member node has shares
                    mid, status, overload, loadavg, numcpu
            .healthy is ref to share with health status of pool
            .deadCount is ref to share with count of dead members of pool
            .event is ref to event share, value is deque of events subbed from eventer
            .req is ref to subscription request share, value is deque of subscription requests
                each request is duple of tag, share
            .parm is ref to node.parm share
                timeout is time in seconds whereupon ping has failed
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(PingPoolBosserSalt, self).__init__(**kw)
        
        self.members = odict() 
        self.mids = odict() 
        self.cycleStart = None 
        self.alives = odict() 

    def postinitio(self):
        """ initialize poolees from pool"""
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))
            self.members[key]['alive'] = self.store.create('.'.join([node.name, 'alive'])).update(value=None)
            self.mids[self.members[key]['mid'].value] = key #assumes mid already inited elsewhere
            self.alives[key] = None
            
        self.healthy.update(value=None)
        self.deadCount.update(value=0)
            
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
                self.members[self.mids[data['id']]]['alive'].update(value=data['return'])
                self.alives[self.mids[data['id']]] = True
                
        for member in self.members.values(): # clear stale active
            if not member['status'].value: #pool member is off
                member['alive'].update(value=None)           
            
        if self.cycleStart is not None:
            # see if all are alive or any still dead
            alive = True # when all on are alive
            deadCount = 0
            for key, member in self.members.items():
                if member['status'].value: #pool member is on
                    if not self.alives[key]: #still dead
                        alive = False
                        deadCount += 1
            
            if alive: # immediately update if all alive
                self.healthy.update(value=alive)
                self.deadCount.update(value=deadCount)
                console.verbose("     Pool healthy is {0}\n".format(
                    self.healthy.value))
                
            else: # dead so far but only update as unhealthy (dead) at end of cycle
                if (self.stamp - self.cycleStart) > self.parm.data.timeout:
                    # cycle completed 
                    self.deadCount.update(value=deadCount)
                    for key, member in self.members.values():
                        if member['status'].value: #pool member is on
                            if not self.alives[key]: #still dead
                                member['alive'].update(value=False) #this one dead
                    self.healthy.update(value=False)
                    console.terse("     Pool healthy is {0} with {1} dead minions\n".format(
                        self.healthy.value, self.deadCount.value))
                    self.cycleStart = None
                           
        if self.cycleStart is None: #start new cycle
            self.cycleStart =  self.stamp
            
            for key in self.alives: #mark all as dead.
                self.alives[key] = False 
            
            target = ','.join([member['mid'].value for member in self.members.values() if member['status'].value ])
            
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
            .members = odict of pool members by name
                 values are odicts that map to pool member shares
            .mids is odict mapping minion ids to pool member names
            
        local attributes created by initio
            .inode is inode node
            .pool is ref to pool node
            .event is ref to event share, value is deque of events subbed from eventer
            .req is ref to subscription request share, value is deque of subscription requests
                each request is duple of tag, share
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(NumcpuPoolBosserSalt, self).__init__(**kw)
        
        self.members = odict() 
        self.mids = odict() 

    def postinitio(self):
        """ initialize poolees from pool"""
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))
            self.members[key]['numcpu'] = self.store.create('.'.join([node.name, 'numcpu'])).update(value=None)
            self.mids[self.members[key]['mid'].value] = key #assumes mid already inited elsewhere
            
            
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
                self.members[self.mids[data['id']]]['numcpu'].update(value=data['return'])
        
        for member in self.members.values(): # clear stale numcpu
            if not member['status'].value: #pool member is off
                member['numcpu'].update(value=None)                    
            
        target = ','.join([member['mid'].value for member in self.members.values() if member['status'].value ])
        
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
            .members = odict of pool members by name
                 values are odicts that map to pool member shares
            .mids is odict mapping minion ids to pool member names
            
        local attributes created by initio
            .inode is inode node
            .pool is ref to pool node
            .event is ref to event share, value is deque of events subbed from eventer
            .req is ref to subscription request share, value is deque of subscription requests
                each request is duple of tag, share
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(LoadavgPoolBosserSalt, self).__init__(**kw)
        
        self.members = odict() 
        self.mids = odict() 

    def postinitio(self):
        """ initialize poolees from pool"""
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))
            self.members[key]['loadavg'] = self.store.create('.'.join([node.name, 'loadavg'])).update(value=None)
            self.mids[self.members[key]['mid'].value] = key #assumes mid already inited elsewhere
            
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
                self.members[self.mids[data['id']]]['loadavg'].update(value=data['return']['1-min'])
        
        for member in self.members.values(): # clear stale loadavg
            if not member['status'].value: #pool member is off
                member['loadavg'].update(value=None)              
            
        target = ','.join([member['mid'].value for member in self.members.values() if member['status'].value ])
        
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
