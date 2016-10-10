"""detecting.py detector deed module

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

from ....aid import aiding, navigating
from ....base import doing

from ....aid.consoling import getConsole
console = getConsole()

class DetectorBase(doing.Doer):
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

class DetectorPositionBox(DetectorBase):
    """
    Detects if vehicle position is in box or out
    output share indicates which side in or out
    """
    Ioinits = odict(
        group = 'detector.position.box',
        output = 'box', input = 'state.position',
        parms = dict(track = 0.0, north = 0.0, east = 0.0,
                     length = 10000, width = 2000, turn = 45.0))

    def __init__(self, **kw):
        """Initialize instance.
           group is path name of group in store, group has following subgroups or shares:
           local outputs


           inherited instance attributes
           .name
           .store

        """
        #call super class method
        super(DetectorPositionBox,self).__init__(**kw)

    def _prepio(self, group, output, input, parms = None, **kw):
        """ Override since uses legacy interface

            output
              inside   = vehicle is inside box (Booleans True (False))
              outtop  = vehicle is outside box above top highest priority
              outbottom = vehicle is outside box below bottom next priority
              outleft  = vehicle is outside to the left
              outright  = vehicle is outside to the right
              turnleft = heading for left turn
              turnright = heading for right turn

           inputs
           input = share path name to input vehicle position (north, east)

           parms = dictionary to initialize group.parm fields
              parm.track  = azimuth of track in (degrees)
              parm.width  = width of box  (meters)
              parm.length = length of box (meters)
              parm.north  = north value for center bottom of box (meters)
              parm.east  = east value for center bottom of box (meters)
              parm.turn = degrees to left or right of track for zig zags (0 - 90)

           instance attributes

           .group = copy of group name

           .output = ref to output
              side state with boolean data fields
              .inside, .outtop, .outbottom, .outleft, .outright
              turn headings with data fields
              .turnleft
              .turnright

           .input = ref to vehicle position external input

           .parm = ref to input parameter share group.parm

        """
        self.group = group

        #local outputs
        self.output = self.store.create(output)#create if not exist
        #order important for display purposes
        fields = odict(inside = False)
        fields['outtop'] = False
        fields['outbottom'] = False
        fields['outleft'] = False
        fields['outright'] = False
        fields['turnleft'] = 0.0
        fields['turnright'] = 0.0
        self.output.update(fields)

        #inputs position
        self.input = self.store.create(input)
        self.input.create(north = 0.0)
        self.input.create(east = 0.0)

        #parms
        self.parm = self.store.create(group + '.parm') #create if not exist
        if not parms:
            parms = dict(track = 0.0, width = 1000, length = 10000,
                         north = 0.0, east = 0.0, turn = 45.0)

        parms['turn'] = abs(navigating.wrap2(parms['turn']))
        self.parm.create(**parms)

        turnleft = self.parm.data.track - self.parm.data.turn
        turnright = self.parm.data.track + self.parm.data.turn

        self.output.update(turnleft = turnleft, turnright = turnright)


    def action(self, **kw):
        """computes box detector output

           treat center bottom as origin
           inside outside as delta position relative to center bottom
           and rotated about center bottom by -track
        """
        #compute turns
        turnleft = navigating.wrap2(self.parm.data.track - self.parm.data.turn)
        turnright = navigating.wrap2(self.parm.data.track + self.parm.data.turn)

        self.output.update(turnleft = turnleft, turnright = turnright)

        #get input vehicle position
        pn = self.input.data.north
        pe = self.input.data.east

        #get parameters
        cbn = self.parm.data.north
        cbe = self.parm.data.east
        track = self.parm.data.track
        length = self.parm.data.length
        width = self.parm.data.width

        #get offset of vehicle position relative to center bottom
        pn = pn - cbn
        pe = pe - cbe
        #rotate vehicle position to box by - track
        pn, pe = navigating.RotateFSToNE(heading = -track, forward = pn, starboard = pe)

        #compute side tests
        self.output.update(inside = True)  #default inside until shown outside

        #topright to topleft
        cn = length #top left corner
        ce = - width/2.0
        sn = 0.0 #top side from top left to top right
        se = width
        rn = pn - cn #vehicle position relative to top left corner
        re = pe - ce
        #print(cn,ce,sn,se,pn,pe,rn,re)
        side = se * rn - sn * re #2d perp product
        if side >= 0.0:
            self.output.update(outtop = True, inside = False)
        else:
            self.output.update(outtop = False)

        #bottomright to bottomleft
        cn = 0.0 #bottom right corner
        ce = width/2.0
        sn = 0.0 #bottom side from bottom right to bottom left
        se = - width
        rn = pn - cn #vehicle position relative to top left corner
        re = pe - ce
        side = se * rn - sn * re #2d perp product
        if side >= 0.0:
            self.output.update(outbottom = True, inside = False)
        else:
            self.output.update(outbottom = False)

        #bottomleft to topleft
        cn = 0.0  #bottom left corner
        ce = - width/2.0
        sn = length #left side from bottom left to top left
        se = 0.0
        rn = pn - cn #vehicle position relative to top left corner
        re = pe - ce
        side = se * rn - sn * re #2d perp product
        if side >= 0.0:
            self.output.update(outleft = True, inside = False)
        else:
            self.output.update(outleft = False)

        #topright to bottomright
        cn = length  #top right corner
        ce = width/2.0
        sn = - length #right side from top right to bottom right
        se = 0.0
        rn = pn - cn #vehicle position relative to top left corner
        re = pe - ce
        side = se * rn - sn * re #2d perp product
        if side >= 0.0:
            self.output.update(outright = True, inside = False)
        else:
            self.output.update(outright = False)

        #print("cn = %0.3f ce = %0.3f sn = %0.3f se = %0.3f rn = %0.3f re = %0.3f side = %0.3f" %\
        #   (cn,ce,sn,se,rn,re,side))

        if console._verbosity >= console.Wordage.profuse:
            self._expose()
            console.profuse("doing {0} with output (itblf) = {1}\n".format(self.name, self.output))

    def _expose(self):
        """
           prints out detector state

        """
        print("Detector %s" % (self.name))
        format = "box center bottom north = %0.3f east = %0.3f"
        print(format % (self.parm.data.north, self.parm.data.east))
        format = "box track = %0.3f length = %0.3f width = %0.3f turn = %0.3f"
        print(format % (self.parm.data.track, self.parm.data.length,
                        self.parm.data.width, self.parm.data.turn))
        format = "turn left = %0.3f turn right  = %0.3f "
        print(format % (self.output.data.turnleft, self.output.data.turnright))
        format = "position north = %0.3f east = %0.3f"
        print(format % (self.input.data.north, self.input.data.east))
        format = "box inside = %s outside top = %s bottom = %s left = %s right = %s"
        print(format % (self.output.data.inside,
                        self.output.data.outtop, self.output.data.outbottom,
                        self.output.data.outleft, self.output.data.outright))


