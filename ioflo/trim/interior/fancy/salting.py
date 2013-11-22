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
            .destroyee
            .createe

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
    
    .pooler
        .destroy
           
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
from salt.exceptions import EauthAuthenticationError

from ....base.odicting import odict
from ....base.globaling import *

from ....base import aiding
from ....base import storing 
from ....base import deeding

from ....base.consoling import getConsole
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
        parm=('parm', odict(throttle=0.0, tag='salt/'), True),)
    
    EventerSalt(name = 'saltEventer', store=store).ioinit.update(
        period= '.meta.period',
        req=('req', deque()), 
        event=('event', odict(), True),
        pub=('pub', odict(), True), 
        parm=('parm', odict(throttle=0.0, tag='salt/'), True),)     
    
    EventerSalt(name = 'saltEventerJob', store=store).ioinit.update(
        period=('.meta.period',),
        req=('req', deque()), 
        event=('event', odict(), True),
        pub=('pub', odict(), True), 
        parm=('parm', odict(throttle=0.0, tag='salt/job/'), True),)
    
    EventerSalt(name = 'saltEventerRun', store=store).ioinit.update(
        period=('.meta.period',),
        req=('req', deque()), 
        event=('event', odict(), True),
        pub=('pub', odict(), True), 
        parm=('parm', odict(throttle=0.0, tag='salt/run/'), True),)    
    
    EventerSalt(name = 'saltEventerCloud', store=store).ioinit.update(
        period=('.meta.period',),
        req=('req', deque()), 
        event=('event', odict(), True),
        pub=('pub', odict(), True), 
        parm=('parm', odict(throttle=0.0, tag='salt/cloud/'), True),)    
                                
    OverloadPoolerSalt(name = 'saltPoolerOverload', store=store).ioinit.update(
        pool = '.salt.autoscale.pool.',
        overload = ('.salt.autoscale.status.overload', 0.0, True),
        count = ('.salt.autoscale.status.count', 0, True),)
    
    ChangePoolerSalt(name = 'saltPoolerChange', store=store).ioinit.update(
        pool = '.salt.autoscale.pool.',
        destroyee = ('.salt.autoscale.status.destroyee', "", True),
        createe = ('.salt.autoscale.status.createe', "", True),)
    
    PingPoolBosserSalt(name = 'saltBosserPoolPing', store=store).ioinit.update(
        pool='.salt.autoscale.pool.',
        healthy = ('.salt.autoscale.status.healthy', None, True),
        deadCount = ('.salt.autoscale.status.deadCount', 0, True),
        event=('event', deque()),
        req=('.salt.eventer.req', deque(), True),
        parm=('parm', odict(timeout=5.0), True),)    
    
    NumcpuPoolBosserSalt(name = 'saltBosserPoolNumcpu', store=store).ioinit.update(
        pool='.salt.autoscale.pool.',
        event=('event', deque()),
        req=('.salt.eventer.req', deque(), True), )
    
    LoadavgPoolBosserSalt(name = 'saltBosserPoolLoadavg', store=store).ioinit.update(
        pool=('.salt.autoscale.pool.', ),
        event=('event', deque()),
        req=('.salt.eventer.req', deque(), True),)
    
    CloudRunnerSalt(name = 'cloudRunnerSalt', store=store).ioinit.update(
        event='event',
        req=('.salt.eventer.req', deque(), True),)
    
    ListsizesCloudRunnerSalt(name = 'saltRunnerCloudListsizes', store=store).ioinit.update(
        event=('.salt.chaser.cloud.listsizes.event', deque()),
        req=('.salt.eventer.req', deque(), True),)
    
    DestroyCloudRunnerSalt(name = 'saltRunnerCloudDestroy', store=store).ioinit.update(
        destroyee='.salt.autoscale.status.destroyee', 
        event=('.salt.chaser.cloud.destroy.event', deque()),
        req=('.salt.eventer.req', deque(), True),)
    
    CreateCloudRunnerSalt(name = 'saltRunnerCloudCreate', store=store).ioinit.update(
        createe='.salt.autoscale.status.createe', 
        event=('.salt.chaser.cloud.create.event', deque()),
        req=('.salt.eventer.req', deque(), True),)       
    
    RunChaserSalt(name = 'runChaserSalt', store=store).ioinit.update(
        kind=('kind', odict(new=False, ret=False), True), 
        ret=('ret', odict(), True),
        event=('event', deque()), )
    
    RunChaserSalt(name = 'saltChaserRun', store=store).ioinit.update(
        kind=('kind', odict(new=False, ret=False), True), 
        ret=('ret', odict(), True),
        event=('event', deque()), )    
    
    ListsizesCloudChaserSalt(name = 'saltChaserCloudListsizes', store=store).ioinit.update(
        kind=('kind', odict(new=False, ret=False), True), 
        ret=('ret', odict(), True),
        event=('event', deque()), )
    
    DestroyCloudChaserSalt(name = 'saltChaserCloudDestroy', store=store).ioinit.update(
        destroyee ='.salt.autoscale.status.destroyee',
        pool = '.salt.autoscale.pool.',
        success=('success', False, True), 
        kind=('kind', odict(new=False, ret=False), True), 
        ret=('ret', odict(), True),
        event=('event', deque()), )
    
    CreateCloudChaserSalt(name = 'saltChaserCloudCreate', store=store).ioinit.update(
        createe ='.salt.autoscale.status.createe',
        pool = '.salt.autoscale.pool.',
        success=('success', False, True), 
        kind=('kind', odict(new=False, ret=False), True), 
        ret=('ret', odict(), True),
        event=('event', deque()), )        

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
            .req is ref to subscription request share, value is deque of
                subscription requests
                each request is duple of tag, share
            .pub is ref to pub share, with tag fields,
                value list of publication to subscriber shares
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
            console.verbose("     Eventer '{0}' subreq tag '{1}' "
                            "share '{2}'\n".format(self.name, tag, share.name))
            if not share: #value not inited to put empty deque()
                share.value = deque()
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
        """ initialize members of pool"""
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))            
            self.members[key]['overload'] = self.store.create('.'.join([node.name, 'overload'])
                                                              ).update(value=0.0)
            self.members[key]['loadavg'] = self.store.create('.'.join([node.name, 'loadavg']))
            self.members[key]['numcpu'] = self.store.create('.'.join([node.name, 'numcpu']))

    def action(self, **kw):
        """ update overloads for pool"""
        super(OverloadPoolerSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        for member in self.members.values():
            if member['status'].value: #pool member is on
                if member['loadavg'].value is not None and member['numcpu'].value is not None:
                    try:
                        member['overload'].update(value=(member['loadavg'].value /
                                                         member['numcpu'].value))
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
    
class ChangePoolerSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Pooler Change
        Computes the destroyee and createe for the pool. That is the minion ids
        of the minion to destroy or create respectively.
        
        The destroyee is the last created minion unless there is only one minion
        then the destroyee is empty.
        
        The createe is the next not on minion in the pool unless all are on then
        the createe is empty
       
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
            .destroyee is ref share holding mid of destroyee
            .createe is ref share holding mid of createe

    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(ChangePoolerSalt, self).__init__(**kw)
        self.members = odict()
        
    def postinitio(self):
        """ initialize members of pool"""
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))            
            
    def action(self, **kw):
        """ update createe and destroyee for pool"""
        super(ChangePoolerSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        destroyee = ""
        count = 0
        for member in self.members.values():
            console.verbose("Member: {0} is {1}\n".format(member['mid'].value,
                                                        member['status'].value))
            if member['status'].value: #pool member is on
                count += 1
                if count > 1: 
                    destroyee = member['mid'].value
        #after loop destroyee is mid of last on member in loop if not the first
        self.destroyee.value = destroyee
        console.terse("     Changed destroyee to '{0}'\n".format(destroyee))
        
        createe = ""
        for member in self.members.values():
            if not member['status'].value: #pool member is on
                createe = member['mid'].value
                break 
        
        self.createe.value = createe
        console.terse("     Changed createe to '{0}'\n".format(createe))
        
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
            .req is ref to subscription request share, value is deque
                of subscription requests
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
        """ initialize members from pool"""
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))
            self.members[key]['alive'] = self.store.create('.'.join([node.name, 'alive'])
                                                           ).update(value=None)
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
                    for key, member in self.members.items():
                        if member['status'].value: #pool member is on
                            if not self.alives[key]: #still dead
                                member['alive'].update(value=False) #this one dead
                    self.healthy.update(value=False)
                    console.terse("     Pool healthy is {0} with {1}"
                        " dead minions\n".format(self.healthy.value, self.deadCount.value))
                    self.cycleStart = None
                           
        if self.cycleStart is None: #start new cycle
            self.cycleStart = self.stamp
            
            for key in self.alives: #mark all as dead.
                self.alives[key] = False 
            
            target = ','.join([member['mid'].value for member in self.members.values()
                               if member['status'].value ])
            
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
        """ initialize members from pool"""
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))
            self.members[key]['numcpu'] = self.store.create('.'.join([node.name, 'numcpu'])
                                                            ).update(value=None)
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
            
        target = ','.join([member['mid'].value for member in self.members.values()
                           if member['status'].value ])
        
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
            .req is ref to subscription request share,
                value is deque of subscription requests
                each request is duple of tag, share
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(LoadavgPoolBosserSalt, self).__init__(**kw)
        
        self.members = odict() 
        self.mids = odict() 

    def postinitio(self):
        """ initialize members from pool"""
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))
            self.members[key]['loadavg'] = self.store.create('.'.join([node.name, 'loadavg'])
                                                             ).update(value=None)
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
            
        target = ','.join([member['mid'].value for member in self.members.values()
                           if member['status'].value ])
        
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
    
class CloudRunnerSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Runner Cloud
        Generic cloud runner:
        
        Requires:
            Unique deed name for 'do'
            New instance to be created using 'as cloud runner salt'
            The cloud function 'fun' to be provided in action parms using
            'to' or 'from' connective for field 'fun'
            The cloud chaser deed event deque 'event' attributed to be provided
            in ioinit using 'per' or 'with' connective for effective attribute 'event'
              
        Example:
            do salt cloud runner listimages as runner salt \
                to fun "list_images" per event "salt.chaser.cloud.listimages.event"
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            
        local attributes created by initio
            .inode is inode node
            .event is ref to event share, of associated chaser Deed
                 value is deque of events subbed from eventer
            .req is ref to subscription request share,
                value is deque of subscription requests
                each request is duple of tag, share
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(CloudRunnerSalt, self).__init__(**kw)

    def postinitio(self):
        """ initialize """
        self.event.value = deque()
            
    def action(self, fun, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(CloudRunnerSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
            
        fun = '.'.join(['runner', 'cloud', fun])
        
        cmd = dict(fun=fun,
                   kwarg=dict(provider='techhat-rackspace'),
                   username='saltwui', password='dissolve', eauth='pam')            
        
        result = None
        try:
            result = self.client.run(cmd)
            console.verbose("     Salt command result = {0}\n".format(result))
        except EauthAuthenticationError as ex:
            console.terse("Eauth failure for salt command {0} with {1}\n".format(cmd, ex))
                      
        if result and result.startswith('salt/run/'):
            self.req.value.append((result, self.event))
            self.req.stampNow()
                
        return None
    
class ListsizesCloudRunnerSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Runner Cloud Listsizes
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            
        local attributes created by initio
            .inode is inode node
            .event is ref to event share, of associated chaser Deed
                 value is deque of events subbed from eventer
            .req is ref to subscription request share,
                value is deque of subscription requests
                each request is duple of tag, share
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(ListsizesCloudRunnerSalt, self).__init__(**kw)


    def postinitio(self):
        """ initialize """
        pass
        #self.event.value = deque()
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(ListsizesCloudRunnerSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        cmd = dict(fun="runner.cloud.list_sizes",
                   kwarg=dict(provider='techhat-rackspace'),
                   username='saltwui', password='dissolve', eauth='pam')            
        
        result = None
        try:
            result = self.client.run(cmd)
            console.verbose("     Salt command result = {0}\n".format(result))
        except EauthAuthenticationError as ex:
            console.terse("Eauth failure for salt command {0} with {1}\n".format(cmd, ex))
                      
        if result and result.startswith('salt/run/'):
            self.req.value.append((result, self.event))
            self.req.stampNow()
                
        return None
    
class DestroyCloudRunnerSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Runner Cloud destroy
    
        Destroys minion in pool given by the destroyee share
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            
        local attributes created by initio
            .inode is inode node
            .destroyee is ref to share holding mid of minion in pool to be destroyed
            .event is ref to event share, of associated chaser Deed
                 value is deque of events subbed from eventer
            .req is ref to subscription request share,
                value is deque of subscription requests
                each request is duple of tag, share
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(DestroyCloudRunnerSalt, self).__init__(**kw)


    def postinitio(self):
        """ initialize """
        pass
        #self.event.value = deque()
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(DestroyCloudRunnerSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        mid = self.destroyee.value
        
        if mid: # minionId to destroy
            cmd = dict(fun="runner.cloud.destroy",
                       kwarg=dict(names=[mid]),
                       username='saltwui', password='dissolve', eauth='pam')
            
            result = None
            try:
                result = self.client.run(cmd)
                console.verbose("     Salt command result = {0}\n".format(result))
            except EauthAuthenticationError as ex:
                console.terse("Eauth failure for salt command {0} with {1}\n".format(cmd, ex))
                          
            if result and result.startswith('salt/run/'):
                self.req.value.append((result, self.event)) #job events
                self.req.value.append(("salt/cloud/{0}/".format(mid), self.event)) # cloud events
                self.req.stampNow()
                
        return None
    
class CreateCloudRunnerSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Runner Cloud destroy
    
        Creates minion in pool given by the createe share
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            
        local attributes created by initio
            .inode is inode node
            .createe is ref to share holding mid of minion in pool to be created
            .event is ref to event share, of associated chaser Deed
                 value is deque of events subbed from eventer
            .req is ref to subscription request share,
                value is deque of subscription requests
                each request is duple of tag, share
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(CreateCloudRunnerSalt, self).__init__(**kw)


    def postinitio(self):
        """ initialize """
        pass
        #self.event.value = deque()
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(CreateCloudRunnerSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        mid = self.createe.value
        
        if mid: # minionId to create
            
            cmd = dict(fun="runner.cloud.profile",
                       kwarg=dict(prof='rackspace_512',
                                    names=[mid]),
                       username='saltwui', password='dissolve', eauth='pam')
            
            result = None
            try:
                result = self.client.run(cmd)
                console.verbose("     Salt command result = {0}\n".format(result))
            except EauthAuthenticationError as ex:
                console.terse("Eauth failure for salt command {0} with {1}\n".format(cmd, ex))
                          
            if result and result.startswith('salt/run/'):
                self.req.value.append((result, self.event)) #job events
                self.req.value.append(("salt/cloud/{0}/".format(mid), self.event)) # cloud events
                self.req.value.append(("salt/minion/{0}/".format(mid), self.event)) # minion events
                self.req.stampNow()
                
        return None
    
class RunChaserSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Chaser Run Generic
        
        Requires:
            Unique deed name for 'do'
            New instance to be created using 'as chaser salt'
            The associated runners are responsible for making the requests to the
                salt eventer with this deeds event deque()
              
        Example:
            do salt chaser run mychaser as run chaser salt
            do salt runner myrunner as runner salt with event "salt.chaser.mychaser.event"
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            
        local attributes created by initio
            .inode is inode node
            .kind is ref to event kinds recieved share fields are event kinds
            .ret is ref to ret share, value is odict of ret event from call
            .event is ref to event share, value is deque of events subbed from eventer
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(RunChaserSalt, self).__init__(**kw)


    def postinitio(self):
        """ initialize """
        pass
    
    def restart(self):
        """ Restart Deed
            Reset to False the fields in .kind share
        """
        console.profuse("Restarting LapseDeed  {0}\n".format(self.name))
        for field in self.kind.keys():
            self.kind[field] = False
        self.kind.stampNow()    
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(RunChaserSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        while self.event.value: #deque of events is not empty
            edata = self.event.value.popleft()
            console.verbose("     {0} got event {1}\n".format(self.name, edata['tag']))
            data = edata['data']            
            tag = edata['tag']
            parts = tag.split('/')
            if parts[0] == 'salt':
                if parts[1] == 'run':
                    jid = parts[2]
                    kind = parts[3]
                    self.kind.update([(kind, True)]) #got set status for event
                    if kind == 'ret':
                        #if data.get('success'): #only ret events
                        self.ret.value.update(data['ret'])
                
        return None
    
    
class ListsizesCloudChaserSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Chaser Cloud Listsizes
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            
        local attributes created by initio
            .inode is inode node
            .kind is ref to event kinds recieved share fields are event kinds
            .ret is ref to ret share, value is odict of ret event from call
            .event is ref to event share, value is deque of events subbed from eventer
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(ListsizesCloudChaserSalt, self).__init__(**kw)


    def postinitio(self):
        """ initialize """
        pass
    
    def restart(self):
        """ Restart Deed
            Reset to False the fields in .kind share
        """
        console.profuse("Restarting LapseDeed  {0}\n".format(self.name))
        for field in self.kind.keys():
            self.kind[field] = False
        self.kind.stampNow()    
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(ListsizesCloudChaserSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        while self.event.value: #deque of events is not empty
            edata = self.event.value.popleft()
            console.verbose("     {0} got event {1}\n".format(self.name, edata['tag']))
            data = edata['data']            
            tag = edata['tag']
            parts = tag.split('/')
            if parts[0] == 'salt':
                if parts[1] == 'run':
                    jid = parts[2]
                    kind = parts[3]
                    self.kind.update([(kind, True)]) #got set status for event
                    if kind == 'ret':
                        #if data.get('success'): #only ret events
                        self.ret.value.update(data['ret'])
                
        return None

class DestroyCloudChaserSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Chaser Cloud Destroy
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            
        local attributes created by initio
            .inode is inode node
            .destroyee is ref to share with mid of detroyed minion
            .pool is ref to pool member node
            .success is ref to success share, value is True if destroy successful
            .kind is ref to event kinds recieved share fields are event kinds
            .ret is ref to ret share, value is odict of ret event from call
            .event is ref to event share, value is deque of events subbed from eventer
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(DestroyCloudChaserSalt, self).__init__(**kw)
        self.members = odict()
        self.mids = odict()

    def postinitio(self):
        """ initialize """
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))
            self.mids[self.members[key]['mid'].value] = key #assumes mid already inited elsewhere
    
    def restart(self):
        """ Restart Deed
            Reset to False the fields in .kind share
        """
        console.profuse("Restarting LapseDeed  {0}\n".format(self.name))
        for field in self.kind.keys():
            self.kind[field] = False
        self.kind.stampNow()
        self.success.value = False
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(DestroyCloudChaserSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        while self.event.value: #deque of events is not empty
            edata = self.event.value.popleft()
            console.verbose("     {0} got event {1}\n".format(self.name, edata['tag']))
            data = edata['data']            
            tag = edata['tag']
            parts = tag.split('/')
            if parts[0] == 'salt':
                if parts[1] == 'run':
                    jid = parts[2]
                    kind = parts[3]
                    self.kind.update([(kind, True)])
                    console.terse("     Event Run {0}\n".format(kind))
                    if kind == 'ret':
                        self.ret.value.update(data['ret'])
                        if data.get('success'): #only ret events
                            self.success.value = True
                            self.members[self.mids[self.destroyee.value]]['status'].value = False
                            console.terse("     Disabled '{0}'\n".format(self.destroyee.value))
                        
                elif parts[1] == 'cloud':
                    mid = parts[2]
                    kind =  parts[3]
                    self.kind.update([(kind, True)])
                    console.terse("     Event Cloud {0}\n".format(kind))
                    
        return None
    
class CreateCloudChaserSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Chaser Cloud Destroy
       
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            .stamp is time stamp
            .lapse is time lapse between updates of deed
            .client is salt client interface
            
        local attributes
            
        local attributes created by initio
            .inode is inode node
            .createe is ref to share with mid of created minion
            .pool is ref to pool member node
            .success is ref to success share, value is True if destroy successful
            .kind is ref to event kinds recieved share fields are event kinds
            .ret is ref to ret share, value is odict of ret event from call
            .event is ref to event share, value is deque of events subbed from eventer
            
    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(CreateCloudChaserSalt, self).__init__(**kw)
        self.members = odict()
        self.mids = odict()

    def postinitio(self):
        """ initialize """
        for key, node in self.pool.items():
            self.members[key] = odict()
            self.members[key]['mid'] = self.store.create('.'.join([node.name, 'mid']))
            self.members[key]['status'] = self.store.create('.'.join([node.name, 'status']))
            self.mids[self.members[key]['mid'].value] = key #assumes mid already inited elsewhere
    
    def restart(self):
        """ Restart Deed
            Reset to False the fields in .kind share
        """
        console.profuse("Restarting LapseDeed  {0}\n".format(self.name))
        for field in self.kind.keys():
            self.kind[field] = False
        self.kind.stampNow()
        self.success.value = False
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(CreateCloudChaserSalt, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        while self.event.value: #deque of events is not empty
            edata = self.event.value.popleft()
            console.verbose("     {0} got event {1}\n".format(self.name, edata['tag']))
            data = edata['data']            
            tag = edata['tag']
            parts = tag.split('/')
            if parts[0] == 'salt':
                if parts[1] == 'run':
                    jid = parts[2]
                    kind = parts[3]
                    self.kind.update([(kind, True)])
                    console.terse("     Event Run {0}\n".format(kind))
                    if kind == 'ret':
                        self.ret.value.update(data['ret'])
                        if data.get('success'): #only ret events
                            self.success.value = True
                            self.members[self.mids[self.createe.value]]['status'].value = True
                            console.terse("     Enabled '{0}'\n".format(self.createe.value))
                        
                elif parts[1] == 'cloud':
                    mid = parts[2]
                    kind =  parts[3]
                    self.kind.update([(kind, True)])
                    console.terse("     Event Cloud {0}\n".format(kind))
                
                elif parts[1] == 'minion':
                    mid = parts[2]
                    kind = parts[3]
                    self.kind.update([(kind, True)])
                    console.terse("     Event Minion {0}\n".format(kind))
                    
        return None

def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    Test()
