"""poking.py goal action module


"""
#print("module {0}".format(__name__))

import time
import struct

from collections import deque
try:
    from itertools import izip
except ImportError: # python3
    izip = zip
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

class Poke(acting.Actor):
    """Poke Class to put values into explicit shares"""
    Registry = odict()

    def action(self, share, data, **kwa):
        """Put data into share """
        console.profuse("Put {0} into {1}\n".format( data, share.name))

        share.update(data)

class PokeDirect(Poke):
    """Class to put direct data values into destination share"""

    def resolve(self, sourceData, destination, destinationFields, **kwa):
        parms = super(PokeDirect, self).resolve( **kwa)

        destination = self.resolvePath(ipath=destination,  warn=True) # now a share
        srcFields = sourceData.keys()
        dstFields = self.prepareDstFields(srcFields, destination, destinationFields)

        dstData = odict()
        for dstField, srcField in izip(dstFields, srcFields):
            dstData[dstField] = sourceData[srcField]

        parms['data'] = dstData
        parms['destination'] = destination
        return parms

    def action(self, data, destination, **kwa):
        """ Put data into share
            parameters:
              data = data to copy from
              destination = share to copy to
        """
        console.profuse("Put {0} into {1}\n".format( data, destination.name))

        destination.update(data)

class PokeIndirect(Poke):
    """
    Class to copy values from one share to another
       based on source and destination field lists

    """
    def resolve(self, source, sourceFields, destination, destinationFields, **kwa):
        parms = super(PokeIndirect, self).resolve( **kwa)

        source = self.resolvePath(ipath=source,  warn=True) # now a share
        destination = self.resolvePath(ipath=destination,  warn=True) # now a share

        sourceFields, destinationFields = self.prepareSrcDstFields(source,
                                                        sourceFields,
                                                        destination,
                                                        destinationFields)

        parms['source'] = source
        parms['sourceFields'] = sourceFields
        parms['destination'] = destination
        parms['destinationFields'] = destinationFields
        return parms

    def action(self, source, sourceFields, destination, destinationFields, **kwa):
        """ Copy sourceFields in source to destinationFields in destination

            copy fields in order according to field lists
              field list order is significant
                 a field of same name in source and destination will
                 not be copied to each other unless appear in same place
                 in both field lists

            parameters:
                source = share to copy from
                sourceFields = list of fields to copy from
                destination = share to copy to
                destinationFields = list of fields to copy to

        """
        console.profuse("Copy {0} in {1} into {2} in {3}\n".format(
            sourceFields, source.name, destinationFields, destination.name))

        data = odict()

        for df, sf in izip(destinationFields, sourceFields):
            data[df] = source[sf]

        destination.update(data) #updates time stamp as well

        console.profuse("Copied {0} into {1}\n".format(
                    data, destination.name))
        return None

class IncDirect(Poke):
    """Class to incremate destination share by direct data values"""

    def resolve(self, destination, destinationFields, sourceData, **kwa):
        parms = super(IncDirect, self).resolve( **kwa)

        destination = self.resolvePath(ipath=destination,  warn=True) # now a share
        sourceFields = sourceData.keys()
        destinationFields = self.prepareDstFields(sourceFields,
                                          destination,
                                          destinationFields)

        parms['destination'] = destination
        parms['data'] = sourceData
        return parms

    def action(self, destination, sourceData, **kwa):
        """ Increment corresponding items in destination by items in data

            if only one field then single increment
            if multiple fields then vector increment

            parameters:
                destination = share to increment
                sourceData = dict of field values to increment by
        """
        try:
            dstData = odict()
            for field in sourceData:
                dstData[field] = destination[field] + sourceData[field]
            destination.update(dstData) #update so time stamp updated, use dict
        except TypeError as ex: #in case value is not a number
            console.terse("Error in Inc: {0}\n".format(ex))
        else:
            console.profuse("Inc {0} in {1} by {2} to {3}\n".format(
                sourceData.keys(), destination.name, sourceData.values(), dstData.values()))


class IncIndirect(Poke):
    """
    Class to increment values in one share with values from another share
       based on source and destination field lists

    """
    def resolve(self, destination, destinationFields, source, sourceFields, **kwa):
        parms = super(IncIndirect, self).resolve( **kwa)

        destination = self.resolvePath(ipath=destination,  warn=True) # now a share
        source = self.resolvePath(ipath=source,  warn=True) # now a share

        sourceFields, destinationFields = self.prepareSrcDstFields(source,
                                                        sourceFields,
                                                        destination,
                                                        destinationFields)

        parms['destination'] = destination
        parms['destinationFields'] = destinationFields
        parms['source'] = source
        parms['sourceFields'] = sourceFields
        return parms

    def action(self, destination, destinationFields, source, sourceFields, **kwa):
        """ Increment destinationFields in destination by sourceFields in source
            parameters:
                destination = share to increment
                destinationField = field in share to increment
                source = share with value to increment by
                sourceField = field in share with value to increment by

        """
        try:
            data = odict()
            for dstField, srcField in izip(destinationFields, sourceFields):
                data[dstField] = destination[dstField] + source[srcField]
            destination.update(data) #update so time stamp updated, use dict
        except TypeError as ex:
            console.terse("Error in Inc: {0}\n".format(ex1))
        else:
            console.profuse("Inc {0} in {1} from {2} in {3} to {4}\n".format(
                destinationFields, destination.name, sourceFields, source.name, data.values))
