"""poking.py goal action module


"""
print "module %s" % __name__

import time
import struct

from collections import deque
from itertools import izip
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

#debugging support
#debug = True
debug = False


#Constant Definitions


#Class definitions
#since put is explicity then no subclasses for a given share
def CreateInstances(store):
    """Create action instances
        must be function so can recreate after clear registry
        globals good for module self tests
    """
    #global poke

    poke = Poke(name = 'poke', store = store)

    pokeDirect = DirectPoke(name = 'pokeDirect', store = store)
    pokeIndirect = IndirectPoke(name = 'pokeIndirect', store = store)
    incDirect = DirectInc(name = 'incDirect', store = store)
    incIndirect = IndirectInc(name = 'incIndirect', store = store)

class Poke(acting.Actor):
    """Poke Class to put values into explicit shares

    """
    Counter = 0  
    Names = {}

    def __init__(self, **kw):
        """Initialization method for instance.

        """
        if 'preface' not in kw:
            kw['preface'] = 'Poke'

        super(Poke,self).__init__(**kw)  

    def action(self, share, data, **kw):
        """Put data into share

        """
        if debug:
            print "Put %s into %s" % ( data, share.name)

        share.update(data)


class DirectPoke(Poke):
    """Direct Poke Class to put direct data values into destination share

    """

    def __init__(self, **kw):
        """Initialization method for instance.

           inherited attributes:
              .name = unique name for action instance
              .store = shared data store

           parameters:
              data = data to copy from
              destination = share to copy to
        """
        if 'preface' not in kw:
            kw['preface'] = 'Poke'

        super(DirectPoke,self).__init__(**kw)  

    def action(self, data, destination, **kw):
        """Put data into share

        """
        if debug:
            print "Put %s into %s" % ( data, destination.name)

        destination.update(data)


class IndirectPoke(Poke):
    """Indirect Poke Class to copy values from one share to another
       based on source and destination field lists

    """

    def __init__(self, **kw):
        """Initialization method for instance.

           inherited attributes:
              .name = unique name for action instance
              .store = shared data store

           parameters:

              source = share to copy from
              sourceFields = list of fields to copy from
              destination = share to copy to
              destinationFields = list of fields to copy to

        """
        super(IndirectPoke, self).__init__(**kw)  

    def action(self, source, sourceFields, destination, destinationFields, **kw): 
        """copy sourceFields in source to destinationFields in destination

           copy fields in order according to field lists
              field list order is significant 
                 a field of same name in source and destination will
                 not be copied to each other unless appear in same place 
                 in both field lists

        """
        if debug: print "Copy %s in %s into %s in %s" %\
           (sourceFields, source.name, destinationFields, destination.name)

        data = odict()

        for df, sf in izip(destinationFields, sourceFields):
            data[df] = source[sf]

        destination.update(data) #updates time stamp as well

        if debug: print "Copied %s into %s" %\
           (data, destination.name)

        return None

class DirectInc(Poke):
    """Direct Poke Class to put direct data values into destination share

    """

    def __init__(self, **kw):
        """Initialization method for instance.

           inherited attributes:
              .name = unique name for action instance
              .store = shared data store

           parameters:
              destination = share to increment
              data = dict of field values to increment by
        """
        if 'preface' not in kw:
            kw['preface'] = 'Poke'

        super(DirectInc,self).__init__(**kw)  

    def action(self, destination, data, **kw):
        """Increment destinationFields in destination by values in data

           if only one field then single increment
           if multiple fields then vector increment
        """
        try:
            dstData = odict()
            for field in data:
                dstData[field] = destination[field] + data[field]
            #update so time stamp updated, use dict
            destination.update(dstData) 

        except TypeError, ex1: #in case value is not a number
            if debug:
                print ex1

        if debug:
            print "Inc %s in %s by %s to %s" %\
                  ( data.keys(), destination.name, data.values(), dstData.values())

class IndirectInc(Poke):
    """Indirect Poke Class to copy values from one share to another
       based on source and destination field lists

    """

    def __init__(self, **kw):
        """Initialization method for instance.

           inherited attributes:
              .name = unique name for action instance
              .store = shared data store

           parameters:

              destination = share to increment
              destinationField = field in share to increment
              source = share with value to increment by
              sourceField = field in share with value to increment by

        """
        super(IndirectInc, self).__init__(**kw)  

    def action(self, destination, destinationFields, source, sourceFields, **kw): 
        """Increment destinationFields in destination by sourceFields in source

        """
        try:
            data = odict()
            for dstField, srcField in izip(destinationFields, sourceFields):
                data[dstField] = destination[dstField] + source[srcField]
            #update so time stamp updated, use dict
            destination.update(data) 

        except TypeError, ex1:
            if debug:
                print ex1

        if debug:
            print "Inc %s in %s from %s in %s to %s" %\
                  ( destinationFields, destination.name, sourceFields, source.name, data.values)

        return None


def Test():
    """Module Common self test

    """
    global debug

    oldDebug = debug
    debug = True #turn on debug during tes



    debug = oldDebug #restore debug value


if __name__ == "__main__":
    test()

