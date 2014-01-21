""" cloning.py framer cloning behaviors


"""
#print "module %s" % __name__

from collections import deque
from ....base.globaling import *

from ....base import aiding
from ....base import storing 
from ....base import deeding
from ....base import framing

from ....base.consoling import getConsole
console = getConsole()


def CreateInstances(store):
    """ Create action instances. Recreate with each new house after clear registry
        
        init protocol:  inode  and (ipath, ival, iown)
    """
    ClonerFramer(name='clonerFramer', store=store).ioinits.update(
        index=('index', 0, True))
    
    ClonerFramer(name='framerCloner', store=store).ioinits.update(
        index=('index', 0, True))
    
class ClonerFramer(deeding.ParamDeed):
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
            kwa['preface'] = 'ClonerFramer'

        #call super class method
        super(ClonerFramer,self).__init__(**kwa)
    
    def cloneParms(self, parms, clones, **kwa):
        """ Returns parms fixed up for framing cloning. This includes:
            Reverting any Frame links to name strings,
            Reverting non cloned Framer links into name strings
            Replacing any cloned framer links with the cloned name strings from clones
            Replacing any parms that are actswith clones.
            
            clones is dict whose items keys are original framer names
            and values are duples of (original,clone) framer references
        """
        parms = super(ClonerFramer,self).cloneParms(parms, clones, **kwa)
        
        framer = parms.get('framer')
        frame = parms.get('frame')
        
        if isinstance(framer, framing.Framer):
            if framer.name in clones:
                parms['framer'] = clones[framer.name][1].name
            else:
                parms['framer'] = framer.name # revert to name
        elif framer: # assume namestring
            if framer in clones:
                parms['framer'] = clones[framer][1].name

        if isinstance(frame, framing.Frame):
            parms['frame'] = frame.name # revert to name        
        
        return parms
           
    def resolveLinks(self, _act, framer, frame, **kwa):
        """ Resolves value (tasker) link that is passed in as parm
            resolved link is passed back to act to store in parms
            since framer may not be current framer at build time
        """
        parms = {}
        parms.update(super(ClonerFramer,self).resolveLinks(_act, **kwa))
        
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

def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    Test()
