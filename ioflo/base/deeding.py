"""deeding.py deed module


"""
#print "module %s" % __name__

import time
import struct
from collections import deque,  Mapping
import inspect
import copy

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
    """Deed Actor run by 'do' command

        deeds are recur actions
        but building deed from hafscript checks 
        if deed instance has restart attribute then
           adds entry action to call restart method of deed
        TimeLapse deeds have restart method attribute

        inherited attributes
          .name = unique name for actor instance
          .store = shared data store
        
        local attributes
          ._iois
          .ioinit

    """
    #create Deed specific registry name space
    Counter = 0  
    Names = {}
    
    __slots__ = ('ioinit', '_iois',)

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
        
        self.ioinit = ioinit or odict() #dict with default ioinit arguments
        self._iois = odict() # attribute names inited with .initio if any

    def preinitio(self, **kw):
        """ Parse time Reinit
            Enables initializing instance at parse time from FloScript options
            The default init values in .ioinit are used to preload an odict
            which is updated/overwritted with **kw and returned.
            
            Each argument name is the name of an io attribute for the Deed
            
            The argument values are the pathname strings of Deed
            specific io shares or nodes
            
            This provides support for the 'per' and 'for' connectives in the do
            command
            
            The inital values of the shares must be performed somewhere else
            either in the .postinitio method of the Deed or by a FloScript command
            such as init or put
            
            This allows dynamic initialization of Deed instances at FloScript
            parse time not python module load time.
            
            Because preinitio is executed at parse time by the builder when deed
            appears in FloScript, preinitio will override the default values
            set in .ioinit (if any) when its updated in CreateInstances.
            
        """
        ioinit = odict(self.ioinit)
        ioinit.update(kw)
        return ioinit
                
    def initio(self, inode='', **kw):
        """ Intialize and hookup ioflo shares from node pathname inode and kw arguments.
            This implements a generic Deed interface protocol for associating the
            io data flow shares to the Deed.
            
            inode is the computed pathname string of the share node where shares associated
            with the Deed instance may be placed for use by the other kw arguments.
            
            The values of the items in the **kw argument may be either strings,
            non-string iterables such as list or tuple, or named iterables such as
            namedtuple or dicts.
            
            The init behavior of the other arguments is based on the form of the argument value.
            
            There are the following 3 forms for val:
            
            1- string
               ipath = pathnamestring
            
            2- dict of key: values (mapping)
            
                {
                    ipath: "pathnamestring",
                    ival: initial value,
                    iown: truthy,
                }
            
            2- tuple or list of values (non mapping non string iterable)
            
               (ipath, ival, iown) or [ipath, ival, iown]
               ipath = pathnamestring
               ival = initial value
               iown = truthy
            
            
            In all cases, three init values are produced, these are:
                ipath, ival, iown,
            
            Missing init values will be assigned a default value as per the rules below:
            
            The following rules are applied when given the values of
               ipath, ival, iown
            
            
            For each kw item (key, val)
                key is the name of the associated instance attribute.
                Extract ipath, ival, iown from val
                
                Shares are initialized with mappings passed into share.create or
                share.update. So to assign ival to share.value pass into share.create
                or share.update a mapping of the form {'value': ival} whereas
                passing in an empty mapping does nothing.
                
                If ival not provided
                     set ival to empty mapping which when passed to share.create
                     will not change share.value
                
                Else ival provided
                
                    If ival is an empty Mapping Then
                        assign a shallow copy of ival to share.value by passing
                        in {value: ival (copy)} to share.create 
                   
                    Else If ival is a non-string iterable and not a mapping
                        assign a shallow copy of ival to share.value by passing
                        in {value: ival (copy)} to share.create 
                   
                    Else If ival is a non-empty Mapping Then
                        Each item in ival is assigned as a field, value pair in the share
                        by passing ival directly into share.create or share.update
                        This means there is no way to init a share.value to a non empty mapping
                        It is possible to init a share.value to an empty mapping see below
                    
                    Else
                        assign ival to share.value by by passing
                        in {value: ival} to share.create or share.update

                Create share with pathname given by ipath
                    If ipath is provided
                    
                        If ipath starts with dot "." Then absolute path
                        
                        Else ipath does not start with dot "." Then relative path from inode
                        
                        If ipath ends with dot Then the path is to a node not share
                            node ref is created and remaining init values are ignored 
                           
                    Else
                        ipath is the default path inode.key
                        
                If iown Then
                    init share with ival value using update 
                    
                Else
                    init share with ival value using create ((change if not exist))
                    
                
                Assign attribute name of key and value is share
                

        """
        if not isinstance(inode, basestring):
            raise ValueError("Nonstring inode arg '{0}'".format(inode))
        
        if not inode:
            inode = nameToPath(self.name)
        
        if not inode.endswith('.'):
            inode = "{0}.".format(inode)        
        
        _parametric = hasattr(self, "_parametric")
        iois = odict()
        
        for key, val in kw.items():
            if not _parametric: #iois are attributes
                if hasattr(self, key):
                    if key not in self._iois:
                        raise ValueError("Trying to init non init attribute"
                               "'{0}' in Deed '{1}'".format(key, self.name))
                    else:
                        console.terse("Warning: Reinitializing ioinit attribute"
                                      " '{1}' for Deed {1}\n".format(key, self.name))    
                
            if val == None:
                continue
            
            if isinstance(val, basestring):
                ipath = val
                iown = None
                ival = odict() # effectively will not change share
                
            elif isinstance(val, Mapping): # dictionary
                ipath = val.get('ipath')
                iown = val.get('iown')
                
                if not 'ival' in val:
                    ival = odict() # effectively will not change share
                else:
                    ival = val['ival']
                    
                    if isinstance(ival, Mapping):
                        if not ival: #empty mapping
                            ival = odict(value=copy.copy(ival)) #make copy so each instance unique
                        # otherwise don't change since ival is non-empty mapping
                        
                    elif isinstance(ival, NonStringIterable): # not mapping and NonStringIterable
                        ival = odict(value=copy.copy(ival))
                    
                    else: 
                        ival = odict(value=ival)                    
            
            elif isinstance(val, NonStringIterable): # non dict non string iterable
                length = len(val)
                if not length:
                    raise ValueError("Bad init kw arg '{0}' with Value '{1}'".format(key, val))
                
                ipath = val[0]

                if length >= 3:
                    iown = val[2]
                else:
                    iown =  None
                    
                if length == 1:
                    ival = odict() # effectively will not change share
                else:
                    ival = val[1]
                    if isinstance(ival, Mapping):
                        if not ival: #empty mapping
                            ival = odict(value=copy.copy(ival)) #make copy so each instance unique
                        # otherwise don't change since ival is non-empty mapping
                        
                    elif isinstance(ival, NonStringIterable): # not mapping and NonStringIterable
                        ival = odict(value=copy.copy(ival))
                    
                    else: 
                        ival = odict(value=ival)
            
            else:
                raise ValueError("Bad init kw arg '{0}'with Value '{1}'".format(key, val))
            
            
            if ipath:
                if not ipath.startswith('.'): # full path is inode joined to ipath
                    ipath = '.'.join((inode.rstrip('.'), ipath)) # when inode empty prepends dot
            else:
                ipath = '.'.join(inode.rstrip('.'), key)    
            
            ioi = odict(ipath=ipath, ival=ival, iown=iown)
            if _parametric: # act resolveLinks will resolve share/node ref and init
                iois[key] = ioi
            else:           
                self._iois[key] = ioi
       
        ioi = odict(ipath=inode)
        if _parametric: # act resolveLinks will resolve node ref
            iois['inode'] = ioi
        else:
            self._iois['inode'] = ioi
        
        return iois # non-empty when parametric
    
    def postinitio(self):
        """ Base method to be overriden in sub classes. Perform post initio setup"""
        pass
    
    def resolveLinks(self, _act, **kwa):
        """ Resolves paths and links using _act from parms
            Uses Actor resolveLinks to resolve paths in act.iois
            Resolves paths for ._iois 
            Then calls and calls .postinitio
            
            Returns any updated parms
        """
        parms = {}
        parms.update(super(Deed,self).resolveLinks(_act, **kwa))
                     
        if self._iois:
            for key, ioi in self._iois.items():
                setattr(self, key, storing.resolvePath(  store=self.store,
                                                        ipath=ioi['ipath'],
                                                        ival=ioi.get('ival'), 
                                                        iown=ioi.get('iown'),
                                                        act=_act))
        self.postinitio()
        
        return parms
    
class ParamDeed(Deed):
    """ParamDeed Deed has the attribute ._parametric defined that indicates that
       its initio is to result in keyword parameters to its action method and
       not as instance attributes.
       
       Generic Super Class 
       Should be subclassed

       inherited attributes
          .name = unique name for actor instance
          .store = shared data store
          .ioinit = dict of ioinit data for initio

       local attributes
          ._parametric = None. Presence acts as flag to change initio behavior

    """
    __slots__ = ('_parametric', )
    
    def __init__(self, **kw):
        """Initialize Instance """
        if 'preface' not in kw:
            kw['preface'] = 'ParamDeed'

        #call super class method
        super(ParamDeed,self).__init__( **kw)  

        self._parametric = None

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
    __slots__ = ('stamp', )
    
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
        """ Restart Deed
            Override in subclass
            This is called by restarter action in enter context
        """
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

