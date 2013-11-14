""" salting.py saltstack integration behaviors


Shares

.meta
    .period
        value

.salt 
   .pool 
      .m1 
         mid  status  overload  loadavg  numcpus 
      .m2 
         mid  status  overload  loadavg  numcpus 
      .m3 
         mid  status  overload  loadavg  numcpus 
      .m4 
         mid  status  overload  loadavg  numcpus 
      .m5 
         mid  status  overload  loadavg  numcpus 
      .m6 
         mid  status  overload  loadavg  numcpus 
      .mid 
         alpha  ms_0  ms_1  ms_2  ms_3  ms_4 
      .status 
         alpha  ms_0  ms_1  ms_2  ms_3  ms_4 
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
   .bosser 
      .overload 
         .event 
            value 
         .parm 
            value 

init salt.pool.m1 to mid "alpha" status on overload 0.0 loadavg 0.0 numcpus 1
init salt.pool.m2 to mid "ms-0" status on overload 0.0 loadavg 0.0 numcpus 1
init salt.pool.m3 to mid "ms-1" status on overload 0.0 loadavg 0.0 numcpus 1
init salt.pool.m4 to mid "ms-2" status off overload 0.0 loadavg 0.0 numcpus 1
init salt.pool.m5 to mid "ms-3" status off overload 0.0 loadavg 0.0 numcpus 1
init salt.pool.m6 to mid "ms-4" status off overload 0.0 loadavg 0.0 numcpus 1

init salt.pool.mid to alpha "alpha" ms_0 "ms-0" ms_1 "ms-1" ms_2 "ms_2" \
      ms_3 "ms-3" ms_4 "ms-4" 
init salt.pool.status to alpha on ms_0 on ms_1 on ms_2 off ms_3 off ms_4 off 
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
    
       init protocol:  inode  and (ipath, ival, iown, ipri)
    """

    Eventer(name = 'saltEventerJob', store=store).ioinit.update(
        event=('event', odict(), True, True), 
        req=('req', deque(), False, True), 
        pub=('pub', odict(), True), 
        period=('.meta.period', None),
        parm=('parm', dict(throttle=0.0, tag='salt/job'), True), 
        inode='.salt.eventer.job', )  
                                
    OverloadPooler(name = 'saltPoolerOverload', store=store).ioinit.update(
        overload=('.salt.overload', 0.0, True, True),
        pool=('.salt.pool.', ), 
        parm=('parm', dict(), True), 
        inode='.salt.bosser.overload',)
    
    NumcpuPoolBosser(name = 'saltBosserPoolNumcpu', store=store).ioinit.update(
        event=('event', deque(), False, True),
        req=('.salt.eventer.job.req', deque(), True),
        pool=('.salt.pool.', ), 
        parm=('parm', dict(), True), 
        inode='.salt.bosser.numcpu',)
    
    LoadavgPoolBosser(name = 'saltBosserPoolLoadavg', store=store).ioinit.update(
        event=('event', deque(), False, True),
        req=('.salt.eventer.job.req', deque(), True),
        pool=('.salt.pool.', ), 
        parm=('parm', dict(), True), 
        inode='.salt.bosser.loadavg',)        
    
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

class Eventer(SaltDeed, deeding.SinceDeed):
    """ Eventer LapseDeed Deed Class
        Salt Eventer
       
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
        super(Eventer, self).action(**kw) #updates .stamp here
        
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
            console.verbose("     Eventer '{0}' event tag '{1}'\n".format(self.name, utag))
            # loop to pub event to publications for subscribers
            for tag, shares in self.pub.value.items():
                if edata['tag'].startswith(tag):
                    for share in shares:
                        share.value.append(edata)

        return None


class OverloadPooler(SaltDeed, deeding.LapseDeed):
    """ Overloader LapseDeed Deed Class
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
            overload is share initer of current overload value for pool
            pool is node initer of shares in node are the pool minions
            parm = inode.parm field values
            inode is node path name in store
            
            
        local attributes created by initio
            .inode is inode node
            .oflos is ref to out flos odict
            .iflos is ref to in flos odict
            
            .overload is ref to overload share, value is computed overload
            .pool is ref to pool node. Each value is share with minion details
                mid, status, overload, loadavg, numcpu
            .parm is ref to node.parm share

    """

    def __init__(self, **kw):
        """Initialize instance """
        #call super class method
        super(OverloadPooler, self).__init__(**kw)

    def action(self, **kw):
        """ update overloads for pool"""
        super(OverloadPooler, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        for share in self.pool.values():
            if share.data.status: #pool member is on
                if share.get('loadavg') is not None and share.get('numcpu') is not None:
                    try:
                        share.data.overload = share.data.loadavg / share.data.numcpu
                        console.terse("     {0} overload is {1:0.4f}\n".format(
                             share.data.mid, share.data.overload))
                    except ZeroDivisionError:
                        pass
            else: # turned off clear stale overload
                share.data.overload = None
                
        
        count = 0
        overloadSum = 0.0
        for share in self.pool.values():
            overload = share.get('overload')
            if overload is not None:
                overloadSum += overload
                count += 1
        
        if count:
            self.overload.value = overloadSum / count
            console.terse("     Pool size {0}, overload is {1:0.4f} \n".format(
                count, self.overload.value))
            
                
        return None
    
    
class NumcpuPoolBosser(SaltDeed, deeding.LapseDeed):
    """Bosser LapseDeed Deed Class
       Salt Bosser 
       
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
            .oflos is ref to out flos odict
            .iflos is ref to in flos odict
            
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
        super(NumcpuPoolBosser, self).__init__(**kw)
        
        self.poolees = odict() #mapping between pool shares and mid

    def postinitio(self):
        """ initialize poolees from pool"""
        for key, share in self.pool.items():
            self.poolees[share.data.mid] = share #map minion id to share
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(NumcpuPoolBosser, self).action(**kw) #updates .stamp and .lapse here

        while self.event.value: #deque of events is not empty
            edata = self.event.value.popleft()
            console.verbose("     Bosser {0} got event {1}\n".format(self.name, edata['tag']))
            data = edata['data']
            if data.get('success'): #only ret events
                self.poolees[data['id']].data.numcpu = data['return']
            
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
                     
                
        return None

class LoadavgPoolBosser(SaltDeed, deeding.LapseDeed):
    """Bosser LapseDeed Deed Class
       Salt Bosser 
       
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
            .oflos is ref to out flos odict
            .iflos is ref to in flos odict
            
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
        super(LoadavgPoolBosser, self).__init__(**kw)
        
        self.poolees = odict() #mapping between pool shares and mid

    def postinitio(self):
        """ initialize poolees from pool"""
        for key, share in self.pool.items():
            self.poolees[share.data.mid] = share #map minion id to share
            
    def action(self, **kw):
        """ check for events
            poll the active pool minions
            request events for associated jobid
        """
        super(LoadavgPoolBosser, self).action(**kw) #updates .stamp and .lapse here

        #if self.lapse <= 0.0:
            #pass
        
        while self.event.value: #deque of events is not empty
            edata = self.event.value.popleft()
            console.verbose("     Bosser {0} got event {1}\n".format(self.name, edata['tag']))
            data = edata['data']
            if data.get('success'): #only ret events
                self.poolees[data['id']].data.loadavg = data['return']['1-min']
            
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
                
        return None


def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    Test()
