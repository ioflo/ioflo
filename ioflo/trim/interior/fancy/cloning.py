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
    CloneFramer(name='cloneFramer', store=store).ioinit.update()
    
    CloneFramer(name='framerClone', store=store).ioinit.update()
    
class CloneFramer(deeding.ParamDeed):
    """ CloneDeed creates a new aux framer as clone of given framer and adds
        it to the auxes of a given frame. Default is current frame.
        
        Since it is a ParamDeed is does not create instance variables for its
        ioinits
        
        inherited attributes
            .name is actor name string
            .store is data store ref
            .ioinit is dict of ioinit data for initio
            ._parametric is flag for initio to not create attributes

    """
    def __init__(self, **kw):
        """Initialize Instance """
        if 'preface' not in kw:
            kw['preface'] = 'CloneFramer'

        #call super class method
        super(CloneFramer,self).__init__(**kw)
    
    def revertLinks(self, framer, name, frame, **kw):
        """ Reverts links to name in support of framer cloning """
        parms = {}
        
        if isinstance(framer, framing.Framer):
            parms['framer'] = framer.name # revert to name
            
        if isinstance(frame, framing.Frame):
            parms['frame'] = frame.name # revert to name        
        
        return parms
           
    def resolveLinks(self, framer, name, frame, **kw):
        """ Resolves value (tasker) link that is passed in as parm
            resolved link is passed back to act to store in parms
            since framer may not be current framer at build time
        """
        parms = {}
        parms['framer'] = framing.resolveFramer(framer, who=self.name)
        parms['frame'] = framing.resolveFrame(frame, who=self.name)

        return parms
        
    def action(self, framer, name, frame, **kw):
        """ Clone framer onto new aux framer named name and assign to frame frame
            
        """
        clone = self.store.house.cloneFramer(framer, name)
        frame.addAux(clone)
        
        return None    



def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    Test()
