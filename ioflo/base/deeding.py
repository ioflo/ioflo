"""deeding.py deed module


"""
#print "module %s" % __name__

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
        
        local attributes
          ._iois
          .ioinit

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
        
        self._iois = odict() # attribute names inited with .initio
        self.ioinit = ioinit or odict() #dict with ioinit arguments
        
    def preinitio(self, **kw):
        """ Parse time Reinit
            Enables initializing instance at parse time from FloScript options
            by saving the init values in .ioinit attribute of the deed.
            
            Each argument name is the name of an io attribute for the Deed
            
            The name "inode" is special, its value is a pathname string for
               the Deed default Store Node
            
            The other argument values are the pathname strings of Deed
            specific io shares or nodes
            
            The inital values of the shares must be performed somewhere else
            either in the .postinitio method of the Deed or by a FloScript command
            such as init or put
            
            This allows dynamic initialization of Deed instances at FloScript
            parse time not python module load time.
            
            Need to change signatue so can pass in odict as pa or list of tuples
            like the update method for shares
            
            Because preinitio is executed at parse time by the builder when deed
            appears in FloScript, preinitio will override the effective pathname
            .ipath in .ioinit set by CreateInstances which happens when new house
            is created in FloScript.
            
        """
        self.ioinit.update(kw)
        return self
    
    def initio(self, inode="", **kw):
        """ Intialize and hookup ioflo shares from node pathname inode and kw arguments.
            This implements a generic Deed interface protocol for associating the
            io data flow shares to the Deed.
            
            The 'inode' argument is a pathname string of the share node for the instance
            where associated shares may be placed. If inode is empty then the default
            value for inode will be created from the instance name where uppercase
            letters indicate intermediate nodes.
            
            For example an Deed instance named 'thingGoneWrong' would have a default
            inode of "thing.gone.wrong".
            
            The values of other items in the **kw argument may be either strings,
            non-string iterables such as list or tuple, or named iterables such as
            namedtuple or dicts.
            
            The init behavior of the other arguments is based on the form of the argument value.
            
            There are the following 3 forms:
            
            1- string
               ipath  pathnamestring
            
            2- tuple of values
            
               (ipath, ival, iown)
            
            2- dict of key: values
            
                {
                    ipath: "pathnamestring",
                    ival: initial value,
                    iown: truthy,
                }
            
            
            In all cases, three init values are produced, these are:
                ipath, ival, iown,
            
            Missing init values will be assigned a default value as per the rules below:
            
            The following rules are applied when given the values of
               ipath, ival, iown
            
            If argument 'inode' provided:
               inode is assigned the item value which is a pathname string
            Else
               inode is derived from the Deed instance name
            
            Assign .inode attribute with value of inode node
            
            For each kw item (key, val)
                key is the name of the associated instance attribute.
                
                If ival not provided do not initialize share leave as is
                
                If ival provided and is not a non-empty Mapping Then
                   assign ival as value of share
                   # This means there is no way to init a share.value to a non empty mapping
                   
                Otherwise each item in ival is assigned as a field, value in the share 

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
        if not inode:
            inode = nameToPath(self.name)
        self.inode = self.store.fetchNode(inode) # None if not exist
        
        for key, val in kw.items():
            if hasattr(self, key):
                if key not in self._iois:
                    raise ValueError("Trying to init preexisting attribute"
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
                
                if not (ival and isinstance(ival, Mapping)): #not non-empty mapping
                    ival = odict(value=ival)
                #else: #ival = ival
            
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
                    if not (ival and isinstance(ival, Mapping)): #not non-empty mapping
                        ival = odict(value=ival)
                    #else:  #ival = ival
            
            else:
                raise ValueError("Bad init kw arg '{0}'with Value '{1}'".format(key, val))
                
            
            if ipath:
                if not ipath.startswith('.'): # full path is inode joined to ipath
                    ipath = '.'.join((inode.rstrip('.'), ipath)) # when inode empty prepends dot
                
                if ipath.endswith('.'): #init a node not share not in iflos or oflos
                    ipath = ipath.rstrip('.') # remove trailing dot
                    setattr(self, key, self.store.createNode(ipath))
                    continue
                    
            else:
                ipath = '.'.join(inode, key)
            
            if not iown:
                setattr(self, key, self.store.create(ipath).create(ival))
            else:
                setattr(self, key, self.store.create(ipath).update(ival))
            self._iois[key] = True
        
        self.postinitio()
        
        return self #allow chaining
    
    def postinitio(self):
        """ Base method to be overriden in sub classes. Perform post initio setup"""
        pass

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

