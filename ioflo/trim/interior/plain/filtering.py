"""filtering.py filter deed module

"""
#print("module {0}".format(__name__))

import math
import time
import struct
from collections import deque
import inspect

from ....aid.sixing import *
from ....aid.odicting import odict
from ....base.globaling import *

from ....aid import aiding
from ....aid.navigating import DEGTORAD, RADTODEG
from ....base import doing

from ....aid.consoling import getConsole
console = getConsole()


class FilterBase(doing.DoerLapse):
    """
    Base class to provide backwards compatible ._initio interface
    """
    def _initio(self, ioinits):
        """
        Initialize Actor data store interface from ioinits odict
        Wrapper for backwards compatibility to new ._initio signature
        """
        self._prepio(**ioinits)
        return odict()


class FilterSensorHeading(FilterBase):
    """Class """
    Ioinits = odict(
        group = 'filter.sensor.heading',
        output = 'heading.output',
        input = 'compass',
        scenario = 'scenario.magnetic',
        parms = dict(phase = 0.0, amp = 0.0))

    def __init__(self, **kw):
        """Initialize instance.


           inherited instance attributes
           .stamp = time stamp
           .lapse = time lapse between updates of controller
           .name
           .store

        """
        #call super class method
        super(FilterSensorHeading,self).__init__(**kw)

    def _prepio(self, group, output, input, scenario, parms = None, **kw):
        """ Override since legacy init interface

            group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    phase
                    amp

              group.elapsed = share copy of time lapse for logging

           output = share path name output true heading estimate degrees
           input = share path name to input raw heading degrees

           scenario = share path name input scenario (for declination)

           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share

           .output = ref to output heading share

           .input = ref to input raw heading
           .scenario = ref to input scenario declination
        """
        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(phase = 45.0, amp = 1.0)

        self.parm.create(**parms)
        #phase can be negative
        self.parm.data.amp = abs(self.parm.data.amp)

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs
        self.output = self.store.create(output).update(value = 0.0)
        #inputs
        self.input = self.store.create(input).create(value = 0.0)
        self.scenario = self.store.create(scenario).create(declination = 0.0)

    def restart(self):
        """Restart

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

    def action(self, **kw):
        """Updates
        """
        super(FilterSensorHeading,self).action(**kw) #.lapse & .stamp updated here
        #.lapse is time since last run
        #.stamp is current time

        self.elapsed.value = self.lapse #store lapse for logging

        #check here because rate calc divide by lapse
        #only finish update if lapse positive
        if self.lapse <= 0.0: #lapse non positive so return
            return

        rawHeading = self.input.value
        declination =  self.scenario.data.declination

        heading = rawHeading + declination #true heading

        phase = self.parm.data.phase
        amp = self.parm.data.amp

        error = amp * math.cos(DEGTORAD * (heading + phase))

        heading -= error #reverse error introduced by compass

        heading %= 360.0 #mod 360 in case wrapped around
        if (heading < 0.0): #if negative make equiv positive
            heading += 360.0

        self.output.value = heading

    def _expose(self):
        """
           prints out sensor state

        """
        print("Filter %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp, self.lapse))
        format = "heading = %0.3f phase = %0.3f amp = %0.3f"
        print(format %\
              (self.output.value, self.parm.data.phase, self.parm.data.amp))

class FilterWindowed(FilterBase):
    """Class """
    Ioinits = odict(
        group = 'filter.sensor.generic', output = 'state.generic',
        input = 'ctd', field = 'generic', depth = 'state.depth',
        parms = dict(window = 60.0, frac = 0.9, preload = 30.0,
                     layer = 40.0, tolerance = 5.0))

    def __init__(self,  **kw):
        """Initialize instance.

           inherited instance attributes
           .stamp = time stamp
           .lapse = time lapse between updates of controller
           .name
           .store

        """
        #call super class method
        super(FilterWindowed,self).__init__(**kw)

    def _prepio(self, group, output, input, field, depth, parms = None, **kw):
        """ Override since legacy init interface

            group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    window = effective time window for averaging in seconds
                    frac = ratio of window at which equivalence is computed
                    preload = initial value of filter so don't trigger threshold
                    layer = depth in meters of layer to ave input field, when not in layer ignore
                    tolerance = depth selection is depth +- tolerance

              group.elapsed = share copy of time lapse for logging

           output = share path name output filtered input field
           input = share path name to input data from sensor
           field = field name string of field in input data from sensor
           depth = share path name to input vehicle depth meters

           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share

           .output = ref to output share

           .input = ref to input share
           .field = input field name
           .depth = ref to input depth

        """
        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(window = 60.0, frac = 0.9, layer = 40.0, tolerance = 5.0, preload = 30.0)

        parms['window'] = abs(parms['window']) #make sure non negative
        parms['frac'] = max(0.0, min(1.0, parms['frac']))
        parms['tolerance'] = abs(parms['tolerance']) #make sure non negative

        self.parm.create(**parms)

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs
        preload = self.parm.data.preload #set initial output to preload
        self.output = self.store.create(output).update(value = preload)
        #inputs
        self.input = self.store.create(input)
        self.field = field
        self.input.create({self.field : 0.0})

        self.depth = self.store.create(depth).create(value = 0.0)

    def restart(self):
        """Restart

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

        if self.output.stamp is None: #first run in case preload changed in init
            preload = self.parm.data.preload #set initial output to preload
            self.output.value = preload

    def action(self, **kw):
        """Updates filter
        """
        depth = self.depth.value
        layer = self.parm.data.layer
        tolerance = self.parm.data.tolerance

        #if depth not in layer, don't filter use preload
        if (depth < (layer - tolerance)) or (depth > (layer + tolerance)):
            preload = self.parm.data.preload
            if self.output.value != preload:
                self.output.value = preload
            return

        #.lapse is time since last run and .stamp is current time
        super(FilterWindowed,self).action(**kw) #.lapse & .stamp updated here
        self.elapsed.value = self.lapse #store lapse for logging

        raw = self.input[self.field] #new raw sensor salinity

        #check here because window calc divide by lapse
        if self.lapse <= 0.0: #lapse non positive so just use raw value
            self.output.value = raw
            return

        old = self.output.value #old salinity
        window = self.parm.data.window
        frac = self.parm.data.frac

        w = max( 1.0, window / self.lapse) #get window size in samples
        equiv = min(1.0, w * frac) #get equivalence time = sample k at which iir = ma filter
        g = 1.0 - (1.0 - frac) ** (1.0/equiv) #get gain for equivalence
        #print("w = %0.4f equiv = %0.4f g = %0.4f" % (w,equiv,g))

        new = (1.0 - g) * old + g * raw
        #print("sNew = %0.4f sOld = %0.4f sRaw = %0.4f" % (sNew,sOld,sRaw))

        self.output.value = new

    def _expose(self):
        """
           prints out sensor state

        """
        print("FilterWindowed %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        format = "output = %0.3f window = %0.3f frac = %0.3f"
        print(format % (self.output.value, self.parm.data.window, self.parm.data.frac))


FilterWindowed.__register__('FilterSensorSalinity', ioinits=odict(
    group = 'filter.sensor.salinity', output = 'state.salinity',
    input = 'ctd', field = 'salinity', depth = 'state.depth',
    parms = dict(window = 60.0, frac = 0.9, preload = 30.0,
                 layer = 40.0, tolerance = 5.0)) )

FilterWindowed.__register__('FilterSensorSalinitysim', ioinits=odict(
    group = 'filter.sensor.salinitysim', output = 'state.salinity',
    input = 'ctdsim', field = 'salinity', depth = 'state.depth',
    parms = dict(window = 60.0, frac = 0.9, preload = 30.0,
                 layer = 40.0, tolerance = 5.0)) )

FilterWindowed.__register__('FilterSensorTemperature', ioinits=odict(
    group = 'filter.sensor.temperature', output = 'state.temperature',
    input = 'ctd', field = 'temperature', depth = 'state.depth',
    parms = dict(window = 60.0, frac = 0.9, preload = 10.0,
                 layer = 40.0, tolerance = 5.0)) )


class FilterCtdMin(FilterBase):
    """Filter Ctd Minimum temperature
    """
    Ioinits = odict(
        group = 'filter.min.temperature', outputs = 'state.mintemps',
        output = 'state.mintemp',
        input = 'ctd', field = 'temperature',
        depth = 'state.depth', position = 'state.position',
        parms = dict(preload = 100.0))

    def __init__(self, **kw):
        """Initialize instance.


           inherited instance attributes
           .stamp = time stamp
           .lapse = time lapse between updates of controller
           .name
           .store

        """
        #call super class method
        super(FilterCtdMin,self).__init__(**kw)

    def _prepio(self, group, outputs, output, input, field, depth, position, parms = None, **kw):
        """ Override since legacy init interface

            group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    preload = initial value of filter should be max value


              group.elapsed = share copy of time lapse for logging

           outputs = share path name of list of min outputs dicts
           output = share path name of copy of current output

           input = share path name to input data from sensor
           field = field name string of field in input data from sensor
           depth = vehicle depth
           position = vehicle position

           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share

           .outputs = ref to outputs list of dicts share
           .output = ref to output share

           .input = ref to input share
           .field = input field name
           .inlast = last input used for computing slope
           .depth = ref to vehicle depth
           .position = ref to vehicle position
        """
        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(window = 60.0, frac = 0.9, layer = 40.0, tolerance = 5.0, preload = 30.0)

        parms['preload'] = abs(parms['preload']) #make sure non negative

        self.parm.create(**parms)

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        self.field = field


        #inputs
        self.input = self.store.create(input)
        self.input.create({self.field : 0.0})
        self.depth = self.store.create(depth).create(value = 0.0)
        self.lastInval = self.input[self.field]
        self.lastDepth = self.depth.value
        self.position = self.store.create(position)
        self.position.create(north = 0.0)
        self.position.create(east = 0.0)

        #outputs
        self.outputs = self.store.create(outputs)
        self.outputs.update(value = [])
        out = odict()
        self.outputs.value.append(out)

        out[self.field] = self.parm.data.preload #set initial output to preload
        out.update(depth = 0.0)
        out.update(slope = 0.0) #delta field / delta depth
        out.update(north = 0.0)
        out.update(east = 0.0)

        self.output = self.store.create(output)
        self.output.update(out)


    def restart(self):
        """Restart
           assumes one will restart in a frame while at appropriate depth
           and position so first output after restart is at a max and then move
           to find minimum
        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

        if self.outputs.stamp is None: #first run in case preload changed in init
            out = self.outputs.value[:-1] #get last output

        else:  #append a new one
            out = odict()
            self.outputs.value.append(out)

        out[self.field] = self.parm.data.preload #set initial output to preload
        out.update(depth = 0.0)
        out.update(slope = 0.0) #delta field / delta depth
        out.update(north = 0.0)
        out.update(east = 0.0)
        self.output.update(out)

        if self.input.stamp is not None: # reload with current input
            inval = self.input[self.field]
            depth = self.depth.value

            try:
                slope = (inval - self.lastInval) / (depth - self.lastDepth)
            except ZeroDivisionError:
                slope = 0.0

            self.lastInval = inval
            self.lastDepth = depth

            out[self.field] = inval
            out.update(depth = depth)
            out.update(slope = slope) #delta field / delta depth

            out.update(north = self.position.data.north)
            out.update(east = self.position.data.east)

            self.output.update(out)

    def action(self, **kw):
        """Updates filter
        """

        #.lapse is time since last run and .stamp is current time
        super(FilterCtdMin,self).action(**kw) #.lapse & .stamp updated here
        self.elapsed.value = self.lapse #store lapse for logging

        if self.input.stamp is None:
            return

        out = self.outputs.value[:-1] #get last output
        inval = self.input[self.field]

        if inval < out[self.field]:
            depth = self.depth.value

            try:
                slope = (inval - self.lastInval) / (indepth - self.lastDepth)
            except ZeroDivisionError:
                slope = 0.0

            self.lastInval = inval
            self.lastDepth = depth

            out[self.field] = inval
            out.update(depth = depth)
            out.update(slope = slope) #delta field / delta depth

            out.update(north = self.position.data.north)
            out.update(east = self.position.data.east)

            self.output.update(out)

    def _expose(self):
        """
           prints out sensor state

        """
        print("MinCTDFilter %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        format = "output = %0.3f depth = %0.3f slope = %0.3f north = %0.3f east = %0.3f "
        print(format % (self.output[self.field], self.output.data.depth, self.output.data.slope,
                        self.output.data.north, self.output.data.east))

