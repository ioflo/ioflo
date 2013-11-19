"""storing.py datashare module

"""
#print "module %s" % __name__

import time
import struct
import re
import copy



from .globaling import *
from .odicting import odict

from . import excepting
from . import registering

from .consoling import getConsole
console = getConsole()


class Node(odict):
    """ Special odict with name property to hold the pathname to the node
    """
    __slots__ = ['_name'] # attribute supporting name property
    
    
    def __init__(self, *pa, **kwa):
        """ Initialize instance. name is empty """
        super(Node,self).__init__(*pa, **kwa)
        
        self._name = ""
    
    #property name
    def getName(self):
        """getter for name property """
        return self._name

    def setName(self, name):
        """setter for name property """
        self._name = name

    name = property(fget = getName, fset = setName, doc = "Pathname to node.")
    
    def byName(self, name):
        """ Sets name and returns self.
            Enables setting name as part of method chaining.
        """
        self.name = name
        return self
    

class Store(registering.Registry):
    """global data store to be shared amoungst all taskers.

       Each object has the concept of ownership in the datashare.

       inherited instance attributes:
       .name  = unique data store name

       instance attributes
       .stamp = global time stamp for store 
       .house = reference to house owning this store
       .shares = dictionary of shared data store items
       .realtime = share for realtime when .stamp is updated

    """
    Counter = 0  
    Names = {}

    def __init__(self, stamp = None, house = None, **kwa):
        """Initialize instance

           *pa and **kwa allow multiple inheritance

        """

        if 'preface' not in kwa:
            kwa['preface'] = 'Store'

        super(Store,self).__init__(**kwa)

        try: #stamp must be a number or None
            stamp = float(stamp)
        except TypeError:
            stamp = None

        self.stamp = stamp #must be None or number
        self.house = house
        self.shares = Node().byName('') #dictionary of data store shares indexed by name
        
        #create node for meta data
        self.metaShr = self.createNode('.meta')
        #create share for stamp
        self.timeShr = self.create('.time').update(value = self.stamp or 0.0)        
        #create share for realtime
        self.realTimeShr = self.create('.realtime').update(value = time.time()) 

    def changeStamp(self, stamp):
        """change time stamp for this store """
        try: #stamp must be a number or None
            self.stamp = float(stamp)
            self.timeShr.update(value=self.stamp)
            self.realTimeShr.update(value=time.time())
        except TypeError:
            self.stamp = None
            print "Error: Store %s, Change stamp to %s not a number" %\
                  (self.name, self.stamp)
            raise

    def advanceStamp(self, delta):
        """change time stamp for this store """
        try:
            self.stamp += delta
            self.timeShr.update(value=self.stamp)
            self.realTimeShr.update(value=time.time())
        except TypeError:
            print "Error: Store %s, Can't advance stamp = %s by delta = %s" %\
                  (self.name, self.stamp, delta)
            raise

    def fetch(self, name):
        """Retrieve from .shares a  node (or special case share)  by its name
           where name is path through hierarchy (may be partial)
           return node or share or if not exist return None

           User of this method needs to test result to determine if node or share

           isinstance(nos, Share)

           since .shares is hierachical dictionary of dictionaries
           need to traverse the hirearchy
        """
        try:
            levels = name.strip('.').split('.')
            nos = self.shares #start at top where nos is node dict or share
            for level in levels:
                nos = nos[level] #attempt dict reference

        except KeyError: #key error when level not in dict so bad name
            return None

        return nos #node or share

    def fetchShare(self, name):
        """Retrieve from .shares a  share by its name 
           return share or if not exist or if not a share (node by same name then
              return None

           since .shares is hierachical dictionary of dictionaries
           need to traverse the hirearchy
        """
        try:
            levels = name.strip('.').split(".")
            nos = self.shares #start at top where nos =node dict or share
            for level in levels:
                nos = nos[level]

        except KeyError:
            return None

        if not isinstance(nos, Share):
            return None

        return nos  #this is actually a share

    def fetchNode(self, name):
        """Retrieve from .shares a  node by its name from .shares
           return node or if not exist or if not a node (share by same name then
              return None

           since .shares is hierachical dictionary of dictionaries
           need to traverse the hirearchy
        """
        try:
            levels = name.strip('.').split(".")
            nos = self.shares
            for level in levels:
                nos = nos[level]

        except KeyError:
            return None

        if isinstance(nos, Share):
            return None

        return nos # this is a node


    def add(self, share):
        """Add share to store and change shares .store to self
           Creates node hierarchy from name as needed
           If share already exists with same name then raises exception. Should use .change instead
           This is to prevent inadvertant adding of shares that clobber node hierarchy

           for a single item list 
              the slice [0:-1] is empty
              the slice [-1] = [0] is the single item 
        """
        if  not isinstance(share, Share):
            raise ValueError("Not Share %s" % share)

        levels = share.name.strip('.').split('.') #strip leading and following '.' and split
        node = self.shares
        depth = 0
        for level in levels[0:-1]: #all but last
            if not level:
                raise ValueError("Empty level in '%s'" % share.name)
            depth += 1
            node = node.setdefault(level, Node().byName('.'.join(levels[:depth]))) #add node if not exist
            if isinstance(node, Share):
                raise ValueError("Level  '%s' in '%s' is preexisting share" % (level, share.name))

        tail = levels[-1]

        if tail in node:
            raise ValueError("Tail '%s' of '%s' is preexisting level" % (tail, share.name))

        node[tail] = share
        share.changeStore(self)

        console.profuse("     Added share {0} to {1}\n".format(share.name, self.name))

        return share
    
    def addNode(self, name):
        """Add node with pathname name to store
           Creates node hierarchy from name as needed
           If node already exists with same name then raises exception. 
           This is to prevent inadvertant adding of node that clobber node/share hierarchy

           for a single item list 
              the slice [0:-1] is empty
              the slice [-1] = [0] is the single item 
        """
        levels = name.strip('.').split('.') #strip leading and following '.' and split
        node = self.shares
        depth = 0
        for level in levels:
            if not level:
                raise ValueError("Empty level in '%s'" % name)
            depth += 1
            node = node.setdefault(level, Node().byName('.'.join(levels[:depth]))) #add node if not exist
            if isinstance(node, Share):
                raise ValueError("Level  '%s' in '%s' is preexisting share" % (level, share.name))

        console.profuse("     Added node {0} to {1}\n".format(name, self.name))

        return node    

    def change(self, share):
        """change existing share with same name in store to share and change share's .store to self
           if share and node hierachy do not exist then raises exception 
           this is to make it harder to inadvertantly mess up node hierarchy
        """
        if  not isinstance(share, Share):
            raise ValueError("Not share %s" % share)

        levels = share.name.strip('.').split(".")
        node = self.shares
        for level in levels[0:-1]: #all but last
            if not level:
                raise ValueError("Empty level in '%s'" % share.name)

            if level in node: 
                node = node[level]
                if isinstance(node, Share):
                    raise ValueError("Level  '%s' in '%s' is preexisting share" % (level, share.name))

            else:
                raise ValueError("No share with name '%s'" % share.name)

        tail = levels[-1]
        if (tail not in node) or (not isinstance(node[tail], Share)):
            raise ValueError("No share with name '%s'" % share.name)

        node[tail] = share

        share.changeStore(self)

        return share

    def create(self, name):
        """Retrieve share with name if it exits  
           otherwise create a share with  name 
              and add to store
        """
        share = self.fetchShare(name)  #does share already exist
        if share is not None: #must compare to none since empty container would also be false
            return share

        return self.add(Share(name = name.strip('.')))
    
    def createNode(self, name):
        """Retrieve node with name if it exits  
           otherwise create a node with  name and add to store
        """
        node = self.fetchNode(name)  #does node already exist
        if node is not None: #must compare to none since empty container would also be false
            return node

        return self.addNode(name=name)   

    def expose(self):
        """   """
        print "Store name = %s, stamp = %s" % (self.name, self.stamp)
        print "Nodes & Shares:"
        Store.ShowNode(self.shares, indent = 0)


    @staticmethod
    def ShowNode(node, indent = 0):
        if isinstance(node, dict):
            for key, value in node.items():
                for i in range(indent):
                    print "  ",
                print ".%s " % key
                Store.ShowNode(value, indent = indent + 1)
        else:
            for i in range(indent):
                print "  ",
            for key in node.keys():
                print "%s " % key,
            print

class Share(object):
    """Shared item in data store

        so it functions somewhat like a dictionary defines:
        __setitem__
        __getitem__
        __delitem__
        __contains__
        __iter__
        __len__
        clear()
        items()
        iteritems()
        iterkeys()
        itervalues()
        keys()
        values()

        properties are used so that time stamps etc are updated properly for logging
 
        properties (properites are stored in class):
            .owner property holds a reference to owner of share (writer)
            .data property holds data record 
                one time stamp applies to the whole data structure
            .value property manages default single field value in data
            .truth property holds the confidence of the value/data. may be None, True, False, [0.0, 1.0]
                truth should not be updated unless value/data is, they are coupled
                thus log if changed on truth also uses last value
            .unit property hold units for fields
           
 
        inherited instance attributes: 
            .name = holds unique store path entry name of share '.' notation
            .store = data store holding share
 
        instance attributes:
            .stamp = time stamp of this share
         
            ._owner used by owner property
            ._data used by data property and also by private accessor methods
            ._truth used by truth property
            ._unit used by unit property
   


          

    """
    def __init__(self, name = '',store = None, 
                 value = None, data = None, truth = None, stamp = None,
                 unit = None, owner = None,  **kwa):
        """Initialize instance

           Parameters:
           name = path name of share in store if created by store
           store = shared data store
           value = value of data field 'value' if any
           data = dictionary (preferable ordered) of data fields and values
           truth = truth for this share
           stamp = time stamp for this share
           unit = measurement units for this share dict (preferably ordered) of fields and values
           owner = owner framework for this share
        """

        self._data = Data() #new data object
        self._truth = None
        self._unit = None 

        self._owner = None
        self.stamp = None
        
        if not isinstance(name,str): #name must be string
            name = ''
        self.name = name
        
        self.changeStore(store = store)
        #if store is not none then
        #   should really make sure share.name is path name in store and is added to store
        #   must double check above where store adds or creates share

        if value is not None:
            self.value = value
        if data is not None:
            self.change(**data)
        if truth is not None:
            self.truth = truth
        if stamp is not None:
            try:
                stamp = float(stamp)
                self.stamp = stamp
            except TypeError:
                print "Error: Share %s bad initializer stamp = %s" % (self.name, stamp)

        if unit is not None:
            self.changUnit(**unit)
        if owner is not None:
            self.owner = owner


    #make share look like a dictionary for .data record fields
    def __contains__(self, key):
        """       """
        return hasattr(self._data, key)

    def __delitem__(self, key):
        """       """
        try:
            delattr(self._data, key)
        except AttributeError:
            raise KeyError("%s object has no key '%s'" % (self.__class__.__name__, key))

    def __getitem__(self, key):
        """    """
        try:
            return getattr(self._data, key)
        except AttributeError:
            raise KeyError("%s object has no key '%s'" % (self.__class__.__name__, key))

    def __setitem__(self, key, value):
        """          """
        try:
            setattr(self._data, key, value)
        except AttributeError:
            raise KeyError("%s invalid key '%s'" % (self.__class__.__name__, key))
        #don't update stamp here since used by change

    def __iter__(self):
        """      """
        for key in self.keys():
            yield key

    def __len__(self):
        """    """
        return len(self._data.__dict__)

    def __repr__(self):
        """    """
        itemreprs = repr(self._data.__dict__)
        return 'Share '  + itemreprs

    def clear(self):
        """   """
        self._data.__dict__.clear()

    def get(self, key, default = None):
        """D.get(k,d)"""
        if key in self:
            return self[key]
        else:
            return default

    def has_key(self, key):
        """  """
        return key in self

    def insert(self, index, key, item):
        """Insert key:item at index."""
        self._data.__dict__.insert(index, key, item)
        #don't update stamp here since used by change

    def items(self):
        """   """
        return self._data.__dict__.items()

    def iterkeys(self):
        """   """
        return iter(self)

    def iteritems(self):
        """   """
        return ((key, self[key]) for key in self.keys())

    def itervalues(self):
        """    """
        return (self[key] for key in self.keys())

    def keys(self):
        """   """
        return self._data.__dict__.keys()

    def values(self):
        """  """
        return [self[key] for key in self.keys()]
    
    # store management
    def changeStore(self, store = None):
        """Replace .store """
        if store is not None: 
            if  not isinstance(store, Store):
                raise ValueError("Not store %s" % store)
        self.store = store
    
    #property owner
    def getOwner(self):
        """getter for  owner property """
        return self._owner

    def setOwner(self, owner):
        """setter for owner property """
        self._owner = owner

    owner = property(fget = getOwner, fset = setOwner, doc = "Owner of share")

    def stampNow(self):
        """Force time stamp this share to store.stamp
           This is useful when share field is a collection that is modified
           in place, i.e. can't use update since update copies
           so stampNow update the stamp. 
        """
        self.stamp = self.store.stamp

        return self.stamp

    #property truth
    def getTruth(self):
        """getter for truth property """
        return self._truth

    def setTruth(self, truth):
        """setter for value property """
        self._truth = truth

    truth = property(fget = getTruth, fset = setTruth, doc = "Truth for this share")

    #property value
    def getValue(self):
        """getter for value property
           returns none if no field in data of name 'value'
        """
        try:
            return getattr(self._data, 'value')
        except AttributeError:
            return None

    def setValue(self, value):
        """setter for value property """
        setattr(self._data, 'value', value)
        self.stamp = self.store.stamp

    value = property(fget = getValue, fset = setValue, doc = "Value for this share")

    #property data
    def getData(self):
        """getter for data property """
        return self._data

    def setData(self, data):
        """setter for data property """
        if not isinstance(data, Data):
            raise ValueError("Not Data object %s" % data)
        self._data = data
        self.stamp = self.store.stamp

    data = property(fget = getData, fset = setData, doc = "Data for this share")

    def change(self, *pa, **kwa):
        """Change data fields without affecting stamp. 
           Create if not already exist.
        """
        for a in pa: 
            if isinstance(a, dict): #positional arg is dictionary
                for k, v in a.items():
                    setattr(self._data, k, v)
            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    setattr(self._data, k, v)
        for k,v in kwa.items():
            setattr(self._data, k, v)

        return self

    def update(self, *pa, **kwa):
        """Update data fields of this share. 
           create field if not already exist
           set stamp to store.stamp
        """
        self.change(*pa, **kwa)
        #self.stamp = None #update stamp with default
        self.stamp = self.store.stamp

        return self

    def create(self, *pa, **kwa):
        """Create and update fields if they do not already exist otherwise do nothing
           This allows setting defaults only if they have not already been set 
        """
        update = False  #do we need to update stamp
        for a in pa: 
            if isinstance(a, dict): #positional arg is dictionary
                for k, v in a.items():
                    if not hasattr(self._data, k):
                        setattr(self._data, k, v)
                        update = True
            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    if not hasattr(self._data, k):
                        setattr(self._data, k, v)
                        update = True
        for k, v in kwa.items():
            if not hasattr(self._data, k):
                setattr(self._data, k, v)
                update = True

        if update:
            #self.stamp = None #update stamp with default
            self.stamp = self.store.stamp

        return self

    def fetch(self, field, default = None):
        """Retrieve from .data the the value of attribute field or 
           None if it does not exist
        """
        return self.get(field, default)

    def copyDataDict(self):
        """returns a copy of the data odict dictionary
        """
        return self._data.__dict__.copy()

    #property unit
    def getUnit(self):
        """getter for unit property """
        return self._unit

    def setUnit(self, unit):
        """setter for unit property """
        if not isinstance(unit, Data):
            raise ValueError("Not Data object %s" % unit)
        self._unit = unit

    unit = property(fget = getUnit, fset = setUnit, doc = "Unit(s) for this share")

    def changeUnit(self, *pa, **kwa):
        """update unit from kw """
        if self.unit is None:
            self.unit = Data()

        for a in pa: 
            if isinstance(a, dict): #positional arg is dictionary
                for k, v in a.items():
                    setattr(self.unit, k, v)
            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    setattr(self.unit, k, v)
        for k,v in kwa.items():
            setattr(self.unit, k, v)

        return self

    def createUnit(self, *pa, **kwa):
        """create unit from kw  """
        if self.unit is None:
            self.unit = Data()

        for a in pa: 
            if isinstance(a, dict): #positional arg is dictionary
                for k, v in a.items():
                    if not hasattr(self._unit, k):
                        setattr(self._unit, k, v)
            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    if not hasattr(self._unit, k):
                        setattr(self._unit, k, v)
        for k, v in kwa.items():
            if not hasattr(self._unit, k):
                setattr(self._unit, k, v)

        return self

    def fetchUnit(self, field, default = None):
        """Retrieve from .unit the value of attribute field or None if it does not exist """
        if self.unit:
            if hasattr(self._unit, field):
                return getattr(self._unit, field)
        return default

    def expose(self):
        """print out important attributes for debugging """
        print "Name %s Store %s Stamp %s Value %s  Dict %s\nTruth %s Unit %s Owner %s " % \
              (self.name, self.store, self.stamp, self.value,  self.data, self.truth,
               self.unit,  self.owner)

    def show(self):
        """print name and data files"""
        print "Name %s Value %s" % (self.name, self.value)
        for key, value in self.data.__dict__.items():
            print "%s = %s" % (key, value),
        print


import optimize


#from types import ListType, TupleType

class Data(object):
    """Data class

    """

    def __new__(cls, *pa, **kwa): 
        """Set up at instance creation """
        #self = object.__new__(cls, *pa, **kwa)
        self = object.__new__(cls)
        self.__dict__ = odict()
        return self

    def __init__(self, *pa, **kwa):
        """Data() -> new empty Data record.

           Data(pa1, pa2, ...) where pa = tuple of positional args, (pa1, pa2, ...)
              each paX may be  a sequence of duples (k,v) or a dict

           Data(k1 = v1, k2 = v2, ...) where kwa = dictionary of keyword args, {k1: v1, k2 : v2, ...}
        """
        for a in pa: 
            if isinstance(a, dict): #positional arg is dictionary
                for k, v in a.items():
                    setattr(self, k, v)
            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    setattr(self, k, v)

        for k,v in kwa.items():
            setattr(self, k, v)

    def __setattr__(self, key, value):
        """Convert setattr to setitem on self.__dict__

           need to override __setattr__ because 
           we shadowed .__dict__  in __new__ above and 
           class's __setattr__  only uses .__dict__ descriptor's 
           setter/getter  methods in  class where descripter created 
           not in subclass. This is odd behavior by python because
           to be symmetric with how __getattr__ works python should check if 
           instance has .__dict__ and use that instead.
           By overriding __setattr__  we insure that when
           need to add to __dict__ we are using the instance version not
           the descriptor version in class. what if we bind a descriptor? 
           normally descriptors go in class.__dict__
           not instance .__dict__ Do we need to check assigned value for being
           as descriptor and pass on to class?

           Don't need __getattr__ override because __getattribute__ always
           looks in instance.__dict__ as last resort if can't find in 
           class.__dict__ descriptor or elsewhere
        """
        try: #see if super class already has attribute so don't shadow
            super(Data,self).__getattribute__(key)
        except AttributeError: #super doesn't have it so put in dictionary
            if (key in self.__dict__) or REO_IdentPub.match(key): #don't do check if already there
                self.__dict__.__setitem__(key,value)
            else:
                raise AttributeError("Invalid attribute name '%s'" % key)
        else: #pass on to superclass
            super(Data,self).__setattr__(key,value)

optimize.bind_all(Data)


def Test():
    """Module self test """


    try:
        Store.Clear()

        store = Store()
        print "Store shares = %s" % store.shares

        store.add(Share(name = 'autopilot.depth')).create(depth = 0.0)
        print store.fetch('autopilot.depth').data.depth
        try:
            print store.fetch('autopilot.depth').data.value
        except AttributeError, e1:
            print e1.message
        print store.fetch('autopilot.depth').value
        print "Store shares = %s" % store.shares

        store.create('autopilot.heading').create(heading = 0.0)
        print store.fetch('autopilot.heading').data.heading
        try:
            print store.fetch('autopilot.heading').data.value
        except AttributeError, e1:
            print e1.message
        print store.fetch('autopilot.heading').value
        print "Store shares = %s" % store.shares

        s = Share(store = store, name = 'autopilot.heading')
        s.create(value = 60.0)
        s.create(value = 50.0)
        print s.data.value
        print s.value
        print s.data.value
        print s.value
        store.change(s)
        print "Store shares = %s" % store.shares

        try:
            store.add(Share(name = 'autopilot.depth'))
        except ValueError, e1:
            print e1.message
        print "Store shares = %s" % store.shares

        try:
            store.change(Share(name = 'autopilot.speed'))
        except ValueError, e1:
            print e1.message
        print "Store shares = %s" % store.shares

        print "autopilot.heading = %s" % store.fetch('autopilot.heading')
        print "autopilot = %s" % store.fetch('autopilot')
        print "dog = %s" % store.fetch('dog')

        store.expose()

    except ValueError, e1:
        print e1.message

    return store


if __name__ == "__main__":
    Test()

