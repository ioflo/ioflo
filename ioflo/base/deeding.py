"""deeding.py deed module


"""
print "module %s" % __name__

import time
import struct
from collections import deque,  Mapping
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

from .aiding import NonStringIterable, just, nameToPath


def CreateInstances(store):
    """Create action instances
       must be function so can recreate after clear registry
    """
    pass

#Class definitions

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

    def __init__(self, ioinit=None, **kw):
        """ Initialize super
            super init arguments
                preface
                name
                store
        """
        if 'preface' not in kw:
            kw['preface'] = 'Deed'

        super(Deed,self).__init__(**kw)
        
        self.ioinit = ioinit or {} #dict with ioinit arguments
        
    def preinitio(self,  **kw):
        """ Parse time Reinit
            Enables initializing instance at parse time from FloScript options
            
            Each argument name is the name of an init method keyword except inode
            Each argument value is the init pathname string of the share holding the
               four init values for that argument as fields in the share.
               creates tuples to pass to method .init
            
            This allows dynamic initialization of Deed instances at FloScript
            parse time not python module load time.
            
        """
        init = dict()
        for key, val in kw.items():
            if key == 'inode': #just return path name string for inode
                init[key] =  val
                continue
            share = self.store.fetchShare(val)
            if not share:
                raise  ValueError("Preinit value '{0}' not valid share pathname"
                                  "to init '{1}'".format(val, self.name))
            init[key] = tuple(  share.get('ipath'),
                                share.get('ival'), 
                                share.get('iown'), 
                                share.get('ipri'))
        
        self.ioinit.update(init)
        return self
    
    def initio(self, inode="", **kw):
        """ Intialize and hookup ioflo shares from node pathname inode and kw arguments.
            This implements a generic Deed interface protocol for associating the
            input and output data flow shares to the Deed.
            
            The inode argument is a pathname string of the share node for the instance
            where associated shares may be placed. If inode is empty then the default
            value for inode will be created from the instance name where uppercase
            letters indicate intermediate nodes. For example an Deed instance named
            thingGoneWrong would have a default inode of "thing.gone.wrong".
            
            The values of the items in the **kw argument may be either tuples
            (lists or other non-string iterables), or dicts.
            The init behavior is based on the form of the argument value.
            
            There are the following 2 forms:
            
            1- tuple of values
            
            (ipath, ival, iown, ipri)
            
            2- dict of key: values
            
            {
                ipath: "pathnamestring",
                ival: initial value,
                iown: truthy,
                ipri: truthy
            }
            
            
            In both cases, four init values are produced, that are,
                ipath, ival, iown, ipri. 
            
            Missing init values will be assigned a value of None
            
            The following rules are applied when given the values of
               ipath, ival, iown, ipri
            as determined by the corresponding tuple elements or dict keys: 
            
            inode is provided pathname else default derived form instance name
            
            For each kw arg item
                Create attribute with name given by kw arg item key
                Create share with store pathname given by ipath
                    If ipath
                        If ipath starts with dot "." Then absolute path
                        Else ipath does not start with dot "." Then relative path to inode
                           
                    Else
                        ipath is relative path of kw arg name to inode
                        
                If not iown Then
                    init share with init value using create (change if not exist)
                    add share to iflos dict with key given by arg/attribute name
                        If ipri Then make it first item in iflos
                    
                Else
                    init share with init value using update
                    add share to oflos dict with key given by arg/attribute name
                        If ipri then make it first item in oflos
                
                init may be single value or dict of field, values
                
                assign .inode attribute of deed to inode node
                assign .iflos and .oflos dict attribute of Deed
        """
        self.iflos = odict()
        self.oflos = odict()
        
        for key, val in kw.items():
            if val == None:
                continue
            
            if not isinstance(val, NonStringIterable):
                raise ValueError("Bad init kw arg '{0}'. Value '{1}'. Not non string iterable".format(key, val))
            
            if isinstance(val, Mapping): # dictionary
                ipath = val.get('ipath')
                ival = val.get('ival')
                iown = val.get('iown')
                ipri = val.get('ipri')
            else: # non dict non string iterable
                ipath, ival, iown, ipri = just(4, val) #unpack 4 elements, None for default
                
            if not inode:
                inode = nameToPath(self.name)
            
            if ipath:
                if not ipath.startswith('.'): # full path is inode joined to ipath
                    ipath = '.'.join((inode.rstrip('.'), ipath)) # when inode empty prepends dot
            else:
                ipath = '.'.join(inode, key)
            
            # Infer intent of initialization of share with ival:
            # ival is None means don't initialize share
            # ival is anything but mapping means assign share.value to ival
            # ival is empty mapping means assign share.value to ival (empty mapping)
            # ival is non empty mapping means assign share[key] =val for key, val in ival.items()
            # This means there is no way to init a share.value to a non empty mapping
            if ival is None:
                ival = odict() #empty dict so update or create not change share
            elif not isinstance(ival, Mapping): #make a dict with 'value' key
                ival = odict(value=ival)
            elif isinstance(ival, Mapping) and not ival: #empty mapping so set value
                ival = odict(value=ival)
            
            if hasattr(self, key):
                ValueError("Trying to init preexisting attribute"
                           "'{0}' in Deed '{1}'".format(key, self.name))            
            
            if not iown:
                setattr(self, key, self.store.create(ipath).create(ival))
                if ipri: #make primary iflo (if multiple last one wins)
                    self.iflos.insert(0, key, getattr(self, key))
                else:
                    self.iflos[key] = getattr(self, key)
            else:
                setattr(self, key, self.store.create(ipath).update(ival))
                if ipri: #make primary oflo (if multiple last one wins)
                    self.oflos.insert(0, key, getattr(self, key))
                else:
                    self.oflos[key] = getattr(self, key)
            
        self.inode = self.store.fetchNode(inode) # None if not exist
        
        return self #allow chaining

class SinceDeed(Deed):
    """SinceDeed Deed Actor Patron Registry Class
       Generic Super Class acts if input updated Since last time ran
       knows time of current iteration and last time processed input

       Should be subclassed

       inherited attributes
          .name = unique name for actor instance
          .store = shared data store
          .ioinit = dict of ioinit data for initio

       local attributes
          .stamp = current time of deed evaluation in seconds

    """
    __slots__ = ('stamp')
    
    def __init__(self, **kw):
        """Initialize Instance """
        if 'preface' not in kw:
            kw['preface'] = 'SinceDeed'

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
          .ioinit = dict of ioinit data for initio

       local attributes
          .stamp =  current time deed evaluation in seconds
          .lapse = elapsed time betweeen evaluations of a behavior

       has restart method when resuming after noncontiguous time interruption
       builder creates implicit entry action of restarter for deed
    """
    __slots__ = ('stamp', 'lapse')
    
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
    pass


if __name__ == "__main__":
    test()

