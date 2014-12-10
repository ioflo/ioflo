""" cloning.py framer cloning behaviors


"""
#print("module {0}".format(__name__))

from collections import deque
from ....base.globaling import *

from ....base import aiding
from ....base import storing
from ....base import deeding
from ....base import framing

from ....base.consoling import getConsole
console = getConsole()

class FramerCloner(deeding.DeedParam):
    """ CloneDeed creates a new aux framer as clone of given framer and adds
        it to the auxes of a given frame. Default is current frame.

        Since it is a ParamDeed is does not create instance variables for its
        ioinits

        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinits is dict of io init data for initio
            ._parametric is flag for initio to not create attributes

    """
    def __init__(self, **kwa):
        """Initialize Instance """
        if 'preface' not in kwa:
            kwa['preface'] = 'FramerCloner'

        #call super class method
        super(FramerCloner,self).__init__(**kwa)

    def resolve(self, parms, **kwa):
        """ Resolves value (tasker) link that is passed in as parm
            resolved link is passed back to act to store in parms
            since framer may not be current framer at build time
        """
        parms.update(super(FramerCloner,self).resolveLinks(_act, **kwa))

        parms['framer'] = framing.resolveFramer(framer, who=self.name)
        parms['frame'] = framing.resolveFrame(frame, who=self.name)

        return parms

    def action(self, framer, frame, index=None, **kwa):
        """ Clone framer onto new aux framer and assign to frame frame
            The index is used to compute the new cloned framer name
        """
        clone = self.store.house.cloneFramer(framer, index.value)
        frame.addAux(clone)
        index.value += 1

        return None
