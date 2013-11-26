""" salting.py saltstack integration behaviors


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
        """ Send runner command
            Request associated events
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
        
        if result:
            self.req.value.append((result['tag'], self.event))
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
        """ Send runner command
            Request associated events
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
        
        if result:
            self.req.value.append((result['tag'], self.event))
            self.req.stampNow()          
                
        return None
    
class DestroyCloudRunnerSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Runner Cloud destroy
    
        Destroys minion mid given by the destroyee share
       
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
            .destroyee is ref to share holding mid of minion to be destroyed
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
        """ Send runner command
            Request associated events
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
                
            if result:
                self.req.value.append((result['tag'], self.event))
                self.req.value.append(("salt/cloud/{0}/".format(mid), self.event)) # cloud events
                self.req.stampNow()              
                
        return None
    
class CreateCloudRunnerSalt(SaltDeed, deeding.LapseDeed):
    """ Salt Runner Cloud destroy
    
        Creates minion given by the mid from the createe share
       
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
            .createe is ref to share holding mid of minion to be created
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
        """ Send runner command
            Request associated events
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
                
            if result:
                self.req.value.append((result['tag'], self.event))
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
        """ process events
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
                        self.ret.value.update(data['return'])
                
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
        """ process events
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
                        self.ret.value.update(data['return'])
                
        return None


def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    Test()
