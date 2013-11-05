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

from .aiding import NonStringIterable, just

#debugging support
#debug = True
debug = False

#Constant Definitions

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

    def __init__(self,  **kw):
        """ Initialize super
            super init arguments
                preface
                name
                store
        """
        if 'preface' not in kw:
            kw['preface'] = 'Deed'

        super(Deed,self).__init__(**kw)
        
    def preinit(self,  **kw):
        """ Parse time Reinit
            Enables initializing instance at parse time from FloScript options
            
            Each argument name is the name of an init method keyword except proem
            Each argument value is the init pathname string of the share holding the
               four init values for that argument as fields in the share.
               creates tuples to pass to method .init
            
            This allows dynamic initialization of Deed instances at FloScript
            parse time not python module load time.
            
        """
        init = dict()
        for key, val in kw.items():
            if key == 'proem': #just return path name string for proem
                init[key] =  val
                continue
            share = self.store.fetchShare(val)
            if not share:
                raise  ValueError("Preinit value '{0}' not valid share pathname"
                                  "to init '{1}'".format(val, self.name))
            init[key] = tuple(  share.get('path'),
                                share.get('valu'), 
                                share.get('iflo'), 
                                share.get('prim'))
        
        self.init(**init)
        return self
    
    def init(self, proem="", **kw):
        """ Intialize and hookup ioflo shares from node pathname proem and kw arguments.
            This implements a generic Deed interface protocol for associating the
            input and output data flow shares to the Deed.
            
            kw arguments may be either tuples (lists or other non-string iterables), or dicts.
            The init behavior is based on the form of the argument.
            
            There are the following 2 forms:
            
            1- tuple of values
            
            (path, valu, iflo, prim)
            
            2- dict of key: values
            
            {
                path: "pathnamestring",
                valu: initial value,
                iflo: truthy,
                prim: truthy
            }
            
            
            In both cases, four init values are produced, that are,
                path, valu, iflo, prim. 
            
            Missing init values will be assigned a value of None
            
            The following rules are applied when given the values of
               path, init, iflo, prim
            as determined by the corresponding tuple elements or dict keys: 
            
            For each kw arg item
                Create attribute with name given by kw arg item key
                Create share with store pathname given by path
                    If path
                        If path starts with dot "." Then absolute path
                        Else path does not start with dot "." Then relative path to proem
                           Unless proem is empty then absolute path with assumed initial dot
                    Else
                        If proem Then relative path of kw arg name to proem
                        Else Error
                If iflo Then
                    init share with init value using create (change if not exist)
                    add share to iflos dict with key given by arg/attribute name
                        If prim Then make it first item in iflos
                    
                Else
                    init share with init value using update
                    add share to oflos dict with key given by arg/attribute name
                        If prim then make it first item in oflos
                
                init may be single value or dict of field, values
                
                assign .node attribute of deed to proem node if given else None
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
                path = val.get('path')
                valu = val.get('valu')
                iflo = val.get('iflo')
                prim = val.get('prim')
            else: # non dict non string iterable
                path, valu, iflo, prim = just(4, val) #unpack 4 elements, None for default
            
            if path:
                if not path.startswith('.'): # full path is proem joined to path
                    path = '.'.join((proem.rstrip('.'), path)) # when proem empty prepends dot
            else:
                if not proem:
                    raise ValueError("Bad init kw arg '{0}'. Missing path '{1}'"
                                     "and node proem '{2}".format(key, path, proem))
                path = '.'.join(proem, key)
            
            # Infer intent of initialization of share with valu:
            # valu is None means don't initialize share
            # valu is anything but mapping means assign share.value to valu
            # valu is empty mapping means assign share.value to valu (empty mapping)
            # valu is non empty mapping means assign share[key] =val for key, val in valu.items()
            # This means there is no way to init a share.value to a non empty mapping
            if valu is None:
                valu = odict() #empty dict so update or create not change share
            elif not isinstance(valu, Mapping): #make a dict with 'value' key
                valu = odict(value=valu)
            elif isinstance(valu, Mapping) and not valu: #empty mapping so set value
                valu = odict(value=valu)
            
            if hasattr(self, key):
                ValueError("Trying to init preexisting attribute"
                           "'{0}' in Deed '{1}'".format(key, self.name))            
            
            if iflo:
                setattr(self, key, self.store.create(path).create(valu))
                if prim: #make primary iflo (if multiple last one wins)
                    self.iflos.insert(0, key, getattr(self, key))
                else:
                    self.iflos[key] = getattr(self, key)
            else:
                setattr(self, key, self.store.create(path).update(valu))
                if prim: #make primary iflo (if multiple last one wins)
                    self.oflos.insert(0, key, getattr(self, key))
                else:
                    self.oflos[key] = getattr(self, key)
            
        self.node = self.store.fetchNode(proem) # None if not exist
        
        self.reinit()
        
        return self #allow chaining
    
    def reinit(self,  **kw):
        """ Subclasses should override this to perform any reinitialization that
            needs to happen after init is performed at parse time not module load time.
            
          """
        pass           
            

class SinceDeed(Deed):
    """SinceDeed Deed Actor Patron Registry Class
       Generic Super Class acts if input updated Since last time ran
       knows time of current iteration and last time processed input

       Should be subclassed

       inherited attributes
          .name = unique name for actor instance
          .store = shared data store

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
    global debug

    oldDebug = debug
    debug = True #turn on debug during tes


    debug = oldDebug #restore debug value


if __name__ == "__main__":
    test()

