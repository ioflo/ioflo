"""needing.py need action module

"""
#print("module {0}".format(__name__))

import time
import struct
from collections import deque
import inspect

from ..aid.sixing import *
from .globaling import *
from ..aid.odicting import odict
from ..aid import aiding
from ..aid.timing import tuuid
from . import excepting
from . import registering
from . import storing
from . import acting
from . import tasking
from . import framing

from ..aid.consoling import getConsole
console = getConsole()

class Need(acting.Actor):
    """Need Class for conditions  such as entry or trans
    """
    Registry = odict()

    def __init__(self, **kwa):
        """
        Initialize Instance

        Inherited Attributes:
            .name = name string for Actor variant in class Registry
            .store = reference to shared data Store
            ._act = reference to containing Act

        Attributes:
            ._tracts = list of references to transition acts for this need
                transit sub-context of precur context during segue

        """
        super(Need, self).__init__(**kwa)
        self._tracts = []

    def _expose(self):
        """
        """
        print("Need %s " % (self.name))

    @staticmethod
    def Check(state, comparison, goal, tolerance):
        """Check state compared to goal with tolerance
           tolerance ignored unless comparison == or !=
        """
        if comparison == '==':
            try: #in case goal is string
                result = ( (goal - abs(tolerance)) <= state <= (goal + abs(tolerance)))
            except TypeError:
                result = (goal == state)
        elif comparison == '<':
            result = ( state < goal)
        elif comparison == '<=':
            result = ( state <= goal)
        elif comparison == '>=':
            result = ( state >= goal)
        elif comparison == '>':
            result = ( state > goal)
        elif comparison == '!=':
            try: #in case goal is string
                result = not ( (goal - abs(tolerance)) <= state <= (goal + abs(tolerance)) )
            except TypeError:
                result = (goal != state)
        else:
            result = False

        return result

    def addTract(self, act):
        """
        Add act to ._tracts list
        """
        self._tracts.append(act)
        act.frame = self._act.frame.name  # resolve later
        act.context = ActionSubContextNames[TRANSIT]


class NeedAlways(Need):
    """NeedAlways Need  Special Need"""
    def action(self, **kw):
        """Always return true"""
        result = True
        console.profuse("Need Always = {0}\n".format(result))
        return result

class NeedDone(Need):
    """NeedDone Need Special Need"""
    def _resolve(self, tasker, framer, frame, **kwa):
        """Resolves value (tasker) link that is passed in as tasker parm
           resolved link is passed back to container ._act to update in act's parms
        """
        parms = super(NeedDone, self)._resolve( **kwa)
        if framer:
            if framer == 'me':
                framer = self._act.frame.framer
            parms['framer'] = framer = framing.resolveFramer(framer,
                                                            who=self._act.frame.name,
                                                            desc='need done',
                                                            contexts=[],
                                                            human=self._act.human,
                                                            count=self._act.count)

        if frame: # framer required
            if frame == 'me':
                frame = self._act.frame
            parms['frame'] = frame = framing.resolveFrameOfFramer(frame,
                                                                  framer,
                                                                  who=self._act.frame.name,
                                                                  desc='need done',
                                                                  human=self._act.human,
                                                                  count=self._act.count)


        if tasker not in ['any', 'all']:
            parms['tasker'] = tasker = tasking.resolveTasker(tasker,
                                                             who=self._act.frame.name,
                                                             desc='need done',
                                                             contexts=[],
                                                             human=self._act.human,
                                                             count=self._act.count)


        return parms #return items are updated in original ._act parms

    def action(self, tasker, framer, frame, **kw):
        """
        Check if  tasker done
        parameters:
            tasker
        """
        if frame:
            if tasker == 'any':
                result = any([aux.done for aux in frame.auxes ])
            elif tasker == 'all':
                result = frame.auxes and all([aux.done for aux in frame.auxes])
            elif tasker in frame.auxes:
                result = tasker.done
            else:
                result = False
            name = tasker if tasker in ('any', 'all') else tasker.name
            console.profuse("Need Aux {0} done = {1}\n".format(name, result))

        else:
            result = tasker.done
            console.profuse("Need Tasker {0} done = {1}\n".format(tasker.name, result))

        return result

class NeedStatus(Need):
    """NeedStatus Need Special Need """

    def _resolve(self, tasker, **kwa):
        """Resolves value (tasker) link that is passed in as parm
           resolved link is passed back to container ._act to update in act's parms
        """
        parms = super(NeedStatus, self)._resolve( **kwa)
        if tasker == 'me':
            tasker = self._act.frame.framer

        parms['tasker'] = tasker = tasking.resolveTasker(tasker,
                                                         who=self.name,
                                                         desc='need status tasker',
                                                         contexts=[],
                                                         human=self._act.human,
                                                         count=self._act.count)
        return parms #return items are updated in original ._act parms

    def action(self, tasker, status, **kw):
        """
        Check if  tasker done
        parameters:
          tasker
          status
        """
        # maybe should add check for auxiliary since status never changes for auxiliary

        result = (tasker.status == status)
        console.profuse("Need Tasker {0} status is {1} = {2}\n".format(
            tasker.name, StatusNames[status], result))

        return result


class NeedState(Need):
    """
    NeedState is a base class for Needs that must resolve a state share ref
    """
    def _resolve(self, state, stateField, **kwa):
        """
        Resolves state share

        parms:
            state       share path of state
            stateField  state share field name
        """
        parms = super(NeedState, self)._resolve( **kwa)

        #convert state path to share and create field if necessary
        parms['state'] = state = self._resolvePath(ipath=state,
                                                  warn=True) # now a share

        if not stateField: #default rules for field
            if state: #state has fields
                if 'value' in state:
                    stateField = 'value'

                else: #ambiguous
                    msg = ("ResolveError: Can't determine field for state"
                          " '{0}'".format(state.name))
                    raise excepting.ResolveError(msg, 'state', self.name,
                                            self._act.human, self._act.count)
            else:
                stateField = 'value'

        if stateField not in state:
            console.profuse("     Warning: Non-existent field '{0}' in state {1}"
                            " ... creating anyway".format(stateField, state.name))
            state[stateField] = 0.0 #create

        parms['stateField'] = stateField

        return parms #return items are updated in original ._act parms

class NeedBoolean(NeedState):
    """NeedBoolean Need Special Need

       if state
    """

    def action(self, state, stateField, **kw):
        """ Check if state[stateField] evaluates to True
            parameters:
              state = share of state
              stateField = field key

        """
        if state[stateField]:
            result = True
        else:
            result = False
        console.profuse("Need Boolean, if {0}[{1}]: = {2}\n".format(
            state.name, stateField, result))

        return result

class NeedDirect(NeedState):
    """NeedDirect Need

       if state comparison goal [+- tolerance]
    """

    def action(self, state, stateField, comparison, goal, tolerance, **kw):
        """ Check if state[field] comparison to goal +- tolerance is True
            parameters:
                state = share of state
                stateField = field key
                comparison
                goal
                tolerance

        """
        result = self.Check(state[stateField], comparison, goal, tolerance)
        console.profuse("Need Direct, if {0}[{1}] {2} {3} +- {4}: = {5}\n".format(
            state.name, stateField, comparison, goal, tolerance, result))

        return result

class NeedIndirect(NeedState):
    """NeedIndirect Need

       if state comparison goal [+- tolerance]
    """
    def _resolve(self, goal, goalField, **kwa):
        """
        Resolves state share

        parms:
            comparison  comparison operator string
            goal        share path of goal
            goalField   goal share field name
            tolerance   tolerance value

        """
        parms = super(NeedIndirect, self)._resolve( **kwa)

        #convert goal path to share and create field if necessary
        parms['goal'] = goal = self._resolvePath(ipath=goal,
                                                warn=True) # now a share

        if not goalField: #default rules for field
            if goal: #goal has fields
                if 'value' in goal:
                    goalField = 'value'

                else: #use stateField
                    goalField = stateField
            else:
                goalField = 'value'

        if goalField not in goal:
            console.profuse("     Warning: Non-existent field '{0}' in goal"
                    " {1} ... creating anyway".format(goalField, goal.name))
            goal[goalField] = 0.0 #create

        parms['goalField'] = goalField

        return parms #return items are updated in original ._act parms

    def action(self, state, stateField, comparison, goal, goalField, tolerance, **kwa):
        """ Check if state[field] comparison to goal[goalField] +- tolerance is True
                       parameters:
              state = share of state
              stateField = field key
              comparison
              goal
              goalField
              tolerance

        """

        result = self.Check(state[stateField], comparison, goal[goalField], tolerance)
        console.profuse("Need Indirect, if {0}[{1}] {2} {3}[{4}] +- %s: = {5}\n".format(
            state.name, stateField, comparison, goal, goalField, tolerance, result))

        return result

class NeedMarker(Need):
    """
    NeedMarker is base class for needs that insert markers on resolvelinks
    Special Need

    """
    def _resolve(self, share, frame, kind, **kwa):
        """
        Resolves frame name link and then
           inserts marker as first enact in the resolved frame

        Incoming Parameters:
            share is path or ref of share holding mark
            frame is name or ref of frame where marker is watching
            kind is name of marker actor class for marker act

        Outgoing Parameters:
            share is resolved ref of share holding mark
            marker is unique key for Mark instance in .marks odict in share

        Marker Act Parameters:
            share is resolved ref of share holding mark
            marker is unique key for Mark instance in .marks odict in share

        """
        parms = super(NeedMarker, self)._resolve( **kwa)

        framer = self._act.frame.framer

        if frame == 'me':
            frame = self._act.frame

        frame = framing.resolveFrameOfFramer(frame,
                                                              framer,
                                                              who=self.name,
                                                              desc='need marker',
                                                              human=self._act.human,
                                                              count=self._act.count)

        parms['share'] = share = self._resolvePath(ipath=share,
                                                  warn=True) # now a share

        marker = "{0}.{1}.{2}.{3}".format(framer.name, frame.name, kind, tuuid())
        parms['marker'] = marker

        if not share.marks.get(marker):
            share.marks[marker] = storing.Mark()

        if kind not in acting.Actor.Registry:
            msg = "ResolveError: Bad need marker link"
            raise excepting.ResolveError(msg, kind, self.name,
                            self._act.human, self._act.count)

        markerParms = dict(share=share, marker=marker)
        markerAct = acting.Act(actor=kind,
                                registrar=acting.Actor,
                                parms=markerParms,
                                human=self._act.human,
                                count=self._act.count)

        self.addTract(markerAct)
        console.profuse("     Added {0} {1} with {2} at {3} in {4} of "
                        "framer {5}\n".format(
                                'tract',
                                markerAct,
                                markerAct.parms['share'].name,
                                markerAct.parms['marker'],
                                self._act.frame.name,
                                framer.name))
        markerAct.resolve()

        markerParms = dict(share=share, marker=marker)
        markerAct = acting.Act(actor=kind,
                                                 registrar=acting.Actor,
                                                 parms=markerParms,
                                                 human=self._act.human,
                                                 count=self._act.count)

        frame.insertEnact(markerAct)
        console.profuse("     Added {0} {1} with {2} at {3} in {4} of "
                        "framer {5}\n".format(
                                'enact',
                                markerAct,
                                markerAct.parms['share'].name,
                                markerAct.parms['marker'],
                                frame.name,
                                framer.name))
        markerAct.resolve()  # resolves .actor given by actor kind name into actor class

        return parms #return items are updated in original ._act parms

class NeedUpdate(NeedMarker):
    """ NeedUpdate Need Special Need """
    def action(self, share, frame, **kw):
        """
        Check if share updated since mark in share was updated by marker in
        frame upon frame entry.
            Default is False

        parameters:
            share = resolved share that is marked
            frame = resolved frame where marker is placed
            marker = marker kind name
        """
        result = False
        mark = share.marks.get(frame.name) #get mark from mark frame name key
        if mark and mark.stamp is not None and share.stamp is not None:
            result = share.stamp >= mark.stamp  # >= catches updates on same enter

        console.profuse("Marker update {0} in Frame {1} of Share {2} {3} "
                        " {4} mark {5} at {6}\n".format(result,
                                                     frame.name,
                                                     share.name,
                                                     share.stamp,
                                                     '>=',
                                                     mark.stamp,
                                                     self.store.stamp))

        return result

class NeedChange(NeedMarker):
    """NeedChange Need Special Need"""
    def action(self, share, frame, **kw):
        """
        Check if share data changed while in frame/mark denoted by name key if any
            Default is False
        parameters:
            share
            name
            frame       only used in resolvelinks
            marker      only used in resolvelinks
        """
        result = False
        mark = share.marks.get(frame.name) #get mark from mark frame name key
        if mark and mark.data is not None:
            for field, value in share.items():
                try:
                    if getattr(mark.data, field) != value:
                        result = True

                except AttributeError as ex: # new attribute so changed
                    result = True

                if result: #stop checking on first change
                    break


        console.profuse("Need Share {0} change in Frame {1} = {2}\n".format(
            share.name, frame.name, result))

        return result
