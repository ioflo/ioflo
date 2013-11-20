"""framing.py hierarchical action framework module

"""
#print "module %s" % __name__

import copy
from collections import deque
from itertools import izip


from .globaling import *
from . import excepting
from . import registering
from . import storing 
from . import tasking

from .consoling import getConsole
console = getConsole()


#Class definitions

class Framer(tasking.Tasker):
    """Framer Task Patron Registry Class for running hierarchical action framework

       inherited instance attributes
          .name = unique name for machine
          .store = data store

          .period = desired time in seconds between runs must be non negative, zero means asap
          .stamp = time of last outline change beginning time to compute elapsed time
          .status = operational status of tasker
          .desire = desired control asked by this or other taskers
          .done = tasker completion state True or False
          .schedule = scheduling context of this Task for Skedder
          .runner = generator to run tasker

       instance attributes
          .main = main frame when this framer is an auxiliary
          .done = auxiliary completion state True or False when an auxiliary
          .elapsed = elapsed time from outline change
          .elapsedShr = share where .elapsed is stored for logging and need checks

          .recurred = number of completed recurrences of the current outline
                   recurred is zeroed upon entry
                   during first iteration recurred is 0 
                   during second iteration (before trans evaluated) recurred is 1
                   so a trans check on recurred == 2 means its already iterated twice
          .recurredShr = share where recurred is stored for logging and need checks

          .first = first frame (default frame to start at)
          .active = active frame
          .actives = active outline list of frames
          .human = human readable version of active outline

          .frameNames = frame name registry , name space of frame names
          .frameCounter = frame name registry counter 
    """
    #Counter = 0  
    #Names = {}

    def __init__(self, **kw):
        """Initialize instance.


        """
        if 'preface' not in kw:
            kw['preface'] = 'Framer'

        super(Framer,self).__init__(**kw) #status = STOPPED  make runner advance so can send cmd

        self.main = None  #when aux framer, frame that is running this aux
        self.done = True #when aux or slave framer, completion state, set to False on enterAll

        self.stamp = 0.0 #beginning time to compute elapsed time since last outline change
        self.elapsed = 0.0 #elapsed time from outline change
        path = 'framer.' + self.name + '.state.elapsed'
        self.elapsedShr = self.store.create(path)
        self.elapsedShr.update(value = self.elapsed)

        self.recurred = 0
        path = 'framer.' + self.name + '.state.recurred'
        self.recurredShr = self.store.create(path)
        self.recurredShr.update(value = self.recurred)

        self.first = None #default starting frame
        self.active = None #active frame
        self.actives = [] #list of frames  in active outline in framework
        self.human = '' #human readable version of actives outline

        self.frameNames = {} #frame name registry for framer. name space of frame names
        self.frameCounter = 0 #frame name registry counter for framer

    def assignFrameRegistry(self):
        """Point Frame class name registry dict and counter to .frameNames
           and .frameCounter.

           Subsequent Frame instance creation with then be registered locally
        """
        Frame.Names = self.frameNames
        Frame.Counter = self.frameCounter


    def restartTimer(self):
        """reset the start time and elapsed time of framer for changed outline

        """
        self.stamp = self.store.stamp
        self.elapsed = 0.0
        self.updateElapsed()


    def updateTimer(self):
        """update the elapsed time of framer in  current outline
           use store.stamp for current time reference
        """
        try:
            self.elapsed = self.store.stamp - self.stamp
        except TypeError: #one or both stamps are not numbers
            self.stamp = self.store.stamp #makes self.stamp a number once store.stamp is
            self.elapsed = 0.0 #elapsed zero until both numbers

        self.updateElapsed()

    def updateElapsed(self):
        """update store value of the elapsed time of framer in  current outline

        """
        console.profuse("Updating {0} from {1:0.4f} to {2:0.4f}\n".format(
            self.elapsedShr.name, self.elapsedShr.value, self.elapsed))
        self.elapsedShr.update(value = self.elapsed)

    def restartCounter(self):
        """restart at 0 the recurred counter and share of framer in current outline

        """
        self.recurred = 0
        self.updateRecurred()


    def updateCounter(self):
        """update the recurred counter and share of framer in current outline

        """
        self.recurred += 1 
        self.updateRecurred()

    def updateRecurred(self):
        """update store value of the recurred count of framer in  current outline

        """
        console.profuse("Updating {0} from {1:0.4f} to {2:0.4f}\n".format(
            self.recurredShr.name, self.recurredShr.value, self.recurred))
        self.recurredShr.update(value = self.recurred)


    def resolveLinks(self):
        """Convert all the name strings for links to references to instance
           by that name
        """
        print "Resolving links for framer %s" % (self.name)

        self.assignFrameRegistry() #needed by act links below

        for frame in Frame.Names.values(): #all frames in this framer's name space
            frame.resolveLinks()

        #Resolve first frame link
        if self.first:
            if not isinstance(self.first, Frame):
                if self.first not in Frame.Names:
                    raise excepting.ResolveError("Bad first frame link", self.name, self.first)

                self.first = Frame.Names[self.first] #replace link name with link
        else:
            raise excepting.ResolveError("No first frame link", self.name, self.first)


    def traceOutlines(self):
        """Trace and assign outlines for each frame in framework
        """
        print "Tracing outlines for framer %s" % (self.name)

        self.assignFrameRegistry() 

        for frame in Frame.Names.values(): #all frames in this framer's name space
            frame.traceOutline()
            frame.traceHead()
            frame.traceHuman()
            frame.traceHeadHuman()

    def change(self, actives, human = ''):
        """set .actives and .human to new outline actives
           and human readable version human
           Used by conditional aux to truncate actives
        """
        self.actives = actives
        self.human = human

    def activate(self, active):
        """make parm active the active starting point for framework.
           used to activate far frame to complete transition
           assumes frame exits handled before this
           generates outline. does not change default = first
        """
        self.active = active
        self.reactivate()

    def reactivate(self):
        """set .actives to the .active.outline
           used to restore full outline after conditional aux truncates it
        """
        self.change(self.active.outline, self.active.human)

    def deactivate(self):
        """clear .active .actives
        """
        self.actives = []
        self.human = ''
        self.active = None

    def checkStart(self):
        """checks if framer can be started from first frame
           checking entry needs for first frame's outline
           returns result of checkEnter()

        """
        return self.checkEnter(self.first.outline)

    def checkEnter(self, enters = []):
        """checks entryNeeds for frames in enters list
           return on first failure do not keep testing
           assumes enters outline in top down order


        """
        console.profuse("{0}Check enters of {1} Framer {2}\n".format(
            '    ' if self.schedule == AUX or self.schedule == SLAVE else '',
            ScheduleNames[self.schedule],
            self.name))

        if not enters:  #don't want to make transition if no change in outline
            console.profuse("    False, empty enters\n")
            return False

        for frame in enters:
            if not frame.checkEnter():
                return False
        console.profuse("    True all {0}\n".format(self.name))
        return True

    def enterAll(self):
        """sets .done to False
           activates first frame
           calls enterActions for frames in active outline

        """
        console.profuse("{0}Enter All {1} Framer {2}\n".format(
            '    ' if self.schedule == AUX or self.schedule == SLAVE else '',
            ScheduleNames[self.schedule],
            self.name))      

        self.done = False #reset done state
        self.activate(self.first)
        self.enter(self.actives)

    def enter(self, enters = []):
        """calls entryActions for frames in enters list
           assumes enters outline is in top down order

        """
        if enters: #only enter  if there are explicit enters
            self.restartTimer() #this also updates share
            self.restartCounter() #this also updates share

        for frame in enters:
            frame.enter()

    def renter(self, renters = []):
        """calls entryActions for frames in renters list
           assumes renters outline is in top down order

        """
        for frame in renters:
            frame.renter()

    def recur(self):
        """calls recurActions for frames in active outline
           assumes actives outline is in top down order

        """
        console.profuse("{0}Recur {1} Framer {2}\n".format(
            '    ' if self.schedule == AUX or self.schedule == SLAVE else '',
            ScheduleNames[self.schedule],
            self.name))      

        for frame in self.actives:  #recur actions top to bottom so all actions get run before trans
            frame.recur()


    def segue(self):
        """Uses stored outline comparison to find exit enter outlines
           Update Elapsed timer and Recurred counter
           Perform transitions for auxiliaries in active outline top down
           Start performing transitions for frames in active outline top down until
             find successful transition or complete without finding
        """
        console.profuse("{0}Segue {1} Framer {2}\n".format(
            '    ' if self.schedule == AUX or self.schedule == SLAVE else '',
            ScheduleNames[self.schedule],
            self.name))      

        self.updateTimer() #this also updates share
        self.updateCounter() #this also updates share

        #Want to make all 'state' changes of auxes from top down so that higher
        # level frame transitions see the state at the cycle that it changed
        # so that higher level transitions have priority over lower level frame
        # transitions
        # so aux segue is in effect its own context
        for frame in self.actives:  #start at top and find transitions
            frame.segueAuxes() #eval and perform transitions for all auxes of frame

        for frame in self.actives:  #start at top and find transitions
            #Eval preacts and attempt transitions for the near frame
            if frame.precur(): #transition or cond aux was successful so stop evaluating
                return True

    def exitAll(self):
        """sets exits to .actives and reverses so in bottom up order
           calls exitActions for frames in exits list

           sets .done to True
           deactivates so restart required to run again
        """
        console.profuse("{0}Exit All {1} Framer {2}\n".format(
            '    ' if self.schedule == AUX or self.schedule == SLAVE else '',
            ScheduleNames[self.schedule],
            self.name))      

        exits = self.actives[:]  #make copy of self.actives so can reverse it
        #exits.reverse() #reverse (in place)  so in bottom up order
        self.exit(exits) #exits is reversed in place in exit()
        self.deactivate()
        self.done = True

    def exit(self, exits = []):
        """calls exitActions for frames in exits list
           assumes exits outline is in top down order 
           so reverses it to bottom up
        """
        exits.reverse()
        for frame in exits:
            frame.exit()

    def rexit(self, rexits = []):
        """calls exitActions for frames in rexits list
           assumes rexits outline is in top down order 
           so reverses it to bottom up
        """
        rexits.reverse()
        for frame in rexits:
            frame.rexit()

    def showHierarchy(self):
        """Prints out Framework Hierachy for this framer
        """
        print "\nFramework Hierarchy for %s:" % self.name
        names = self.frameNames

        #top layer are nodes with no over but a unders
        tops = [ x for x in names.itervalues() if ((not x.over) and x.unders)]
        print "Tops: ",
        for x in tops:
            print "%s " % x.name,

        # bottom nodes with over but no unders
        bottoms = [x for x in names.itervalues() if ((x.over) and (not x.unders))]
        print "\nBottoms: ",
        for x in bottoms:
            print "%s " % x.name,

        # loose node have no over and no unders
        loose = [x for x in names.itervalues() if ((not x.over) and (not x.unders))]
        print "\nLoose: ",
        for x in loose:
            print "%s " % x.name,

        print "\nHierarchy: ",
        upper = tops
        lower = []
        count = 0
        while upper:
            print "\nLevel %d: " % count,
            for u in upper: #
                path = u.name
                over = u.over
                while (over):
                    path = over.name + ">" + path
                    over = over.over

                print "%s " % (path),

            lower = []
            for u in upper: # get next level
                for b in u.unders:
                    lower.append(b)
            upper = lower
            count += 1

        print ""


    def makeRunner(self):
        """generator factory function to create generator to run this framer

           yield self if no trans(ition)
           yields next frame on a trans(ition)
        """
        #do any on creation initialization here
        console.profuse("     Making Framer Runner {0}\n".format(self.name))

        self.status = STOPPED #operational status of framer
        self.desire = STOP
        self.done = True

        try:
            while (True):
                control = (yield (self.status)) #accept control and yield status

                status = self.status #for speed

                console.profuse("\n     Iterate Framer {0} with control = {1} status = {2}\n".format(
                    self.name,
                    ControlNames.get(control, 'Unknown'),
                    StatusNames.get(status, 'Unknown')))

                if control == RUN:
                    if status == RUNNING or status == STARTED:
                        #self.desire = RUN
                        self.segue()
                        self.recur() #.desire may change here
                        console.profuse("     Ran Framer {0}\n".format(self.name))
                        self.status = RUNNING

                    elif status == STOPPED or status == READIED:
                        console.profuse("     Need to Start Framer {0}\n".format(self.name))
                        self.desire = START

                    else: # self.status == ABORTED or unknown:
                        console.profuse("     Aborting Framer {0}, bad status = {1} control = {2}\n".format(
                            self.name,
                            StatusNames.get(status, "Unknown"),
                            ControlNames.get(control, "Unknown")))
                        self.desire = ABORT
                        self.status = ABORTED

                elif control == READY:
                    if status == STOPPED or status == READIED:
                        console.profuse("     Attempting Ready Framer {0}\n".format(self.name))

                        if self.checkStart(): #checks enters
                            console.profuse("     Readied Framer {0} ...\n".format(self.name))
                            self.status = READIED
                        else:  #checkStart failed
                            console.profuse("     Failed Ready Framer {0}\n".format(self.name))
                            self.desire = STOP
                            self.status = STOPPED

                    elif status == RUNNING or status == STARTED:
                        console.profuse("     Framer {0}, aleady Started\n".format(self.name))         

                    else: # self.status == ABORTED or unknown:
                        console.profuse("     Aborting Framer {0}, bad status = {1} control = {2}\n".format(
                            self.name,
                            StatusNames.get(status, "Unknown"),
                            ControlNames.get(control, "Unknown")))
                        self.desire = ABORT
                        self.status = ABORTED            

                elif control == START:
                    if status == STOPPED or status == READIED:
                        console.profuse("     Attempting Start Framer {0}\n".format(self.name))

                        if self.checkStart(): #checks enters
                            console.terse("     Starting Framer {0} ...\n".format(self.name))
                            msg = "To: %s<%s at %s" % (self.name, self.first.human, self.store.stamp)
                            print msg
                            self.desire = RUN
                            self.enterAll() #activates, resets .done state also .desire may change here
                            self.recur() #.desire may change here
                            self.status = STARTED
                        else:  #checkStart failed
                            console.profuse("     Failed Start Framer {0}\n".format(self.name))
                            self.desire = STOP
                            self.status = STOPPED

                    elif status == RUNNING or status == STARTED:
                        console.profuse("     Framer {0}, aleady Started\n".format(self.name)) 
                        self.desire = RUN

                    else: # self.status == ABORTED or unknown:
                        console.profuse("     Aborting Framer {0}, bad status = {1} control = {2}\n".format(
                            self.name,
                            StatusNames.get(status, "Unknown"),
                            ControlNames.get(control, "Unknown")))
                        self.desire = ABORT
                        self.status = ABORTED

                elif control == STOP:
                    if status == RUNNING or status == STARTED:
                        msg = "     Stopping {0} in {1} at {2:0.3f}\n".format(
                            self.name,self.active.name,self.store.stamp)
                        self.desire = STOP
                        console.terse( msg)
                        self.exitAll()  #self.desire may change, self.done = True set in exitAll()
                        console.profuse("     Stopped Framer {0}\n".format(self.name))
                        self.status = STOPPED

                    elif status == STOPPED or status == READIED:
                        console.profuse("     Framer {0}, aleady Stopped\n".format(self.name)) 
                        #self.desire = STOP

                    else: # self.status == ABORTED or unknown:
                        console.profuse("     Aborting Framer {0}, bad status = {1} control = {2}\n".format(
                            self.name,
                            StatusNames.get(status, "Unknown"),
                            ControlNames.get(control, "Unknown")))
                        self.desire = ABORT
                        self.status = ABORTED

                else: #control == ABORT or unknown
                    console.profuse("     Framer {0} aborting with control = {1}\n".format(
                        self.name, ControlNames.get(control, "Unknown")))

                    if status == RUNNING or status == STARTED:
                        msg = "     Aborting %s in %s at %0.3f" %\
                            (self.name, self.active.name, self.store.stamp)
                        print msg
                    elif status == STOPPED or status == READIED:
                        msg = "     Aborting %s at %0.3f" %\
                            (self.name, self.store.stamp)
                        print msg
                    elif status == ABORTED:
                        console.profuse("     Framer {0}, aleady Aborted\n".format(self.name)) 

                    self.desire = ABORT
                    self.status = ABORTED

        finally: #in case uncaught exception
            console.profuse("     Exception causing Abort Framer {0} ...\n".format(self.name))
            self.desire = ABORT
            self.status = ABORTED

    @staticmethod
    def ExEn(nears,far):
        """Computes the relative differences (uncommon  and common parts) between 
           the outline lists nears and fars. 
           Assumes outlines are in top down order
           Supports forced transition when far is in nears 
              in this case 
                 the common part of nears from far down is exited and
                 the common part of fars from far down is entered

           returns tuple (exits, enters, reexens):
              the exits as list of frames to be exited from near (uncommon)
              the enters as list of frame to be entered in far (uncommon) 
              the reexens as list of frames for reexit reenter from near (common) 
        """
        fars = far.outline
        l = min(len(nears), len(fars))
        for i in xrange(l):
            if (nears[i] is far) or (nears[i] is not fars[i]): #first effective uncommon member
                #print "Found it at nears[%d] = %s" % (i, nears[i])
                #(exits, enters, reexens)
                return (nears[i:], fars[i:], nears[:i])

        #should never get here since far is in far.outline
        # so if nears == fars then for some i  nears[i] == far
        #(exits, enters, reexits, reenters)
        return ([], [], nears[:])

    @staticmethod
    def Uncommon(near,far):
        """Computes the relative differences (uncommon part) between 
           the outline lists near and far. 
           Assumes outlines are in top down order
           returns tuple (exits, enters):
              the exits as list of frames to be exited from near bottom up
              the enters as list of frame to be entered in far top down
        """
        n = near
        f = far
        l = min(len(n), len(f))
        for i in xrange(l):
            if n[i] is not f[i]: #first uncommon member
                exits = n[i:]
                #exits.reverse() #bottom up order
                enters = f[i:]
                return (exits, enters)

        #near and far are the same so no uncommons
        exits = []
        enters = []
        return (exits, enters)


class Frame(registering.StoriedRegistry):
    """Frame Class for hierarchical action framework object

       inherited instance attributes
          .name = unique name for frame
          .store = data store

       instance attributes
          .framer = link to framer that executes this frame
          .over = link to frame immediately above this one in hierarchy
          .under = property link to primary frame immediately below this one in hierarchy 
          .unders = list of all frames immediately below this one
          .outline = list of frames in outline for this frame top down order 
          .head = list of frames from top down to self
          .human = string of names of frames in outline top down '>' separated
          .headHuman = string of names of frames in head top down '>' separated
          .next = next frame used by builder for transitions to next

          .beacts = before entry action (need) acts or entry checks
          .preacts = precur action acts (prior to transition recurrent actions)
          #.transacts = trans action acts
          .enacts = enter action acts
          .renacts = renter action acts
          .reacts = recur action acts
          .exacts = exit action acts
          .rexacts = rexit action acts

          .auxes = auxiliary framers
          .specs = specs for auxilary framers

    """
    Counter = 0  
    Names = {}

    def __init__(self, framer = None, **kw):
        """Initialize instance.

        """
        if 'preface' not in kw:
            kw['preface'] = 'Frame'

        super(Frame,self).__init__(**kw)

        self.framer = framer #link to framer that executes this frame
        self.over = None # link to frame above this one, None if no frame above
        self.unders = [] #list of frames below this one, first one is primary under
        self.outline = [] #list of frames in outline top down order.
        self.head = [] #list of frames from top down to self
        self.human = '' #string of names of frames in outline '>' separated
        self.headHuman = '' #string of names of frames in head '>' separated
        self.next = None #next frame used by builder for transitions to next

        self.beacts = [] #list of enter need acts callables that return True or False
        self.preacts = [] #list of prior trans recurring acts  callables upon pre recurrence
        #self.transacts = [] #list of transact callables that return None or far frame if trans needs
        self.enacts = [] #list of enter acts callables upon entry
        self.renacts = [] #list of re-enter acts callables upon re-entry
        self.reacts = [] #list of recurring acts  callables upon recurrence
        self.exacts = [] #list of exit acts callables upon exit
        self.rexacts = [] #list of re-exit acts callables upon re-exit

        self.auxes = [] #list of auxilary framers for this frame
        self.specs = {} #dictionary of parameters for auxilary framers

    def expose(self):
        """Prints out instance variables.

        """   
        if self.framer:
            framername = self.framer.name
        else:
            framername = ''

        print "name = %s, framer = %s, over = %s, under = %s" % \
              (self.name, framername, self.over, self.under)


    def getUnder(self):
        """getter for under property

        """
        if self.unders:
            return self.unders[0]
        else:
            None

    def setUnder(self, under):
        """setter for under property
           changes primary under frame and fixes links
        """
        if under not in self.unders: #not already attached
            under.attach(over = self) #this also detaches if under attached to someone else

        index = self.unders.index(under) #find position of under in unders
        if index != 0: #not already primary
            self.unders.remove(under) #remove
            self.unders.insert(0, under) #insert as primary

    under = property(fget = getUnder, fset = setUnder, doc = "Primary under frame")


    def detach(self):
        """detach self from .over. Fix under links in .over

        """
        if self.over:
            while (self in self.over.unders): #In case multiple copies remove all
                self.over.unders.remove(self)
            self.over = None


    def attach(self, over):
        """attaches self to over frame if attaching would not create loop

           detach from existing over
           setting self.over to over 
           adding self to over.unders and 
           if no primary under for over make self overs's primary under

        """
        if self.over == over: #already attached to over
            return

        if self.checkLoop(over): 
            raise excepting.ParameterError("Attaching would create loop", "frame", frame)
        else:
            self.detach()
            over.unders.append(self) #add to unders
            self.over = over #set  over link to over

    def checkLoop(self, over):
        """Check if attachment to over param would create loop
        """
        frame = over
        while frame: #while not beyond top
            if frame is self:
                return True #loop found
            else:
                frame = frame.over #keep going up outline
        return False #no loop


    def resolveNextLink(self):
        """Resolve next link

        """
        if self.next:
            if not isinstance(self.next, Frame): #over is name not ref so resolve
                try:
                    next = Frame.Names[self.next] #get reference from Frame name registry
                except KeyError:
                    raise excepting.ResolveError("Bad next link in outline", self.name, self.next)

                self.next = next

    def resolveOverLinks(self):
        """Starting with self climb over links resolving the links as needed along the way

        """
        over = self.over
        under = self

        while over: #not beyond top
            if not isinstance(over, Frame): #over is name of frame not ref so resolve
                name = over #make copy for later
                try:
                    over = Frame.Names[name] #get reference from Frame name registry
                except KeyError:
                    raise excepting.ResolveError("Bad over link in outline", self.name, name)

                if over == self: #check for loop
                    raise excepting.ResolveError("Outline overs create loop", self.name, under.name)

                #attach under to over
                if under.name in over.unders: #under name in unders as a result of script under cmd
                    index = over.unders.index(under.name) #index = position in list
                    over.unders[index] = under #replace under at position index
                else: #otherwise append
                    over.unders.append(under) #add to unders

                #maybe should error check for duplicates in unders here

                under.over = over #assign valid over ref

            else: #over is valid frame reference so don't need to resolve
                if over == self: #check for loop
                    raise excepting.ResolveError("Outline overs create loop", self.name, under.name)

            under = over
            over = over.over #rise one level

    def resolveUnderLinks(self):
        """Resolve under links

        """
        for i, under in enumerate(self.unders):
            if not isinstance(under, Frame):
                try:
                    self.unders[i] = Frame.Names[under] #replace link name with link
                except KeyError:
                    raise excepting.ResolveError("Bad link in unders", self.name, under)

        #maybe should as precaution check for and remove duplicate unders
        #with right most removed
        #or at least check for duplicates and flag error


    def resolveAuxLinks(self):
        """Resolve aux links

        """
        for i, aux in enumerate(self.auxes):
            if not isinstance(aux, Framer): # link is name not object
                if aux not in Framer.Names:
                    raise excepting.ResolveError("ResolveError: Bad aux(s) link name", self.name, aux)
                aux = Framer.Names[aux] #replace link name with link
                if not isinstance(aux, Framer): #maker sure framer not just tasker since tasker framer share registry
                    raise excepting.ResolveError("ResolveError: Bad aux(s) name, tasker not framer", self.name, aux.name)
                self.auxes[i] = aux #replace link name with link

            if aux.schedule != AUX:
                raise excepting.ResolveError("ResolveError: Scheduling context not aux", aux.name, aux.schedule)

            #aux.main  is set upon frame.enter before aux.enterAll() so can reuse aux in other frames

    def resolveFramerLink(self):
        """Resolve framer link

        """

        if self.framer:
            if not isinstance(self.framer, Framer):
                if self.framer not in Framer.Names:
                    raise excepting.ResolveError("ResolveError: Bad framer link name", self.name, self.framer)
                framer = Framer.Names[self.framer] #replace link name with link
                if not isinstance(framer, Framer):  #maker sure framer not tasker since tasker framer share registry
                    raise excepting.ResolveError("ResolveError: Bad framer name, tasker not framer", self.name, framer.name)
                self.framer = framer #replace link name with link



    def resolveLinks(self):
        """Resolve links where links are instance name strings assigned during building
           need to be converted to object references using instance name registry

        """
        console.profuse("Resolving links for frame {0}\n".format(self.name))

        self.resolveFramerLink()

        self.resolveNextLink()
        self.resolveOverLinks()
        self.resolveUnderLinks()

        for act in self.beacts:
            act.resolveLinks()

        for act in self.enacts:
            act.resolveLinks()

        for act in self.reacts:
            act.resolveLinks()

        for act in self.preacts:
            act.resolveLinks()
            #act.resolveLinks(frame = self) #pass in frame

        for act in self.exacts:
            act.resolveLinks()

        for act in self.rexacts:
            act.resolveLinks()

        for act in self.renacts:
            act.resolveLinks()

        self.resolveAuxLinks()

    def findBottom(self):
        """Finds the bottom most frame for outline that this frame lives in

        """
        bottom = self #initialize iterative descent
        while(bottom.under): #while not at bottom
            bottom = bottom.under #descend one more level

        return bottom #this is the bottom

    def findTop(self):
        """Finds the top most frame for outline that this frame lives in

        """
        top = self #initialize iterative ascent
        while (top.over): #while not at top
            top = top.over #ascend one more level

        return top #this is the top

    def traceOutline(self):
        """traces outline

           called by framer.traceOutlines near end of build
        """
        outline = []

        frame = self #trace up
        while (frame): #while not above top
            outline.append(frame)
            frame = frame.over #ascend one more level
        outline.reverse() #reverse so top  is left-most in list

        frame = self.under #trace down
        while(frame): #while not below bottom
            outline.append(frame)
            frame = frame.under

        self.outline = outline
        return outline 

    def traceHead(self):
        """traces head portion of outline.
           top down to this frame inclusive
           Useful for truncated outline for conditional aux

           called by framer.traceOutlines near end of build
        """
        head = []
        frame = self
        while (frame): #while not beyond top
            head.append(frame)
            frame = frame.over #ascend one more level

        head.reverse() #reverse so top  is left-most in list
        self.head = head
        return head 

    def traceHuman(self):
        """traces human readable version of outline as '> <'separated string
           where this frame has '<>'

           called by framer.traceOutlines near end of build
        """
        names = []

        frame = self #trace up
        while (frame): #while not above top
            names.append(frame.name)
            frame = frame.over #ascend one more level

        names.reverse()
        human =  '<' + '<'.join(names)

        names = []
        frame = self.under #trace down
        while(frame): #while not below bottom
            names.append(frame.name)
            frame = frame.under

        human += '>' +  '>'.join(names)

        self.human = human
        return human 

    def traceHeadHuman(self):
        """traces human readable version of head as '<'separated string
           where this frame has  '<>'

           called by framer.traceOutlines near end of build
        """
        names = []

        frame = self #trace up
        while (frame): #while not above top
            names.append(frame.name)
            frame = frame.over #ascend one more level

        names.reverse()
        human =  '<' + '<'.join(names) + '>'

        self.headHuman = human
        return human 

    def checkEnter(self):
        """Check Entry Needs for self  and auxes
        """
        console.profuse("    Check enter into {0}\n".format(self.name))

        for need in self.beacts:  #could use generator expression and all()
            if not need(): #evaluate need Act if failed
                return False #return False on first failure

        for aux in self.auxes:
            #if aux.main is not None then it has not been released and so 
            #we can't enter unless its ourself for forced re-entry
            if aux.main and (aux.main is not self): #see if aux still belongs to another frame
                console.profuse("    False aux {0}.main in use".format(aux.name))
                return False

            if not aux.checkStart(): #performs entry checks
                return False

        console.profuse("    True all {0}".format(self.name))

        return True #since no failues return True

    def enter(self):
        """calls enacts enter  acts for self and auxes
        """
        console.profuse("    Enter {0}\n".format(self.name))

        for act in self.enacts: #could use generator expression
            act() #call entryAction

        for aux in self.auxes:
            msg = "To: %s<%s at %s" % (aux.name, aux.first.human, aux.store.stamp)
            print msg

            aux.main = self  #assign aux's main to this frame
            aux.enterAll() #starts at aux.first frame

    def renter(self):
        """calls  renacts renter acts for self
        """
        console.profuse("    Renter {0}\n".format(self.name))
        for act in self.renacts: #could use generator expression
            act() #call renter actions

    def recur(self): 
        """calls reacts recurring acts for self and runs auxes
        """
        console.profuse("    Recur {0}\n".format(self.name))

        for act in self.reacts:
            act()

        for aux in self.auxes:
            aux.recur()

    def segueAuxes(self): 
        """performs transitions for auxes
           called by self.framer.segue()
           segue Auxes is its own context
        """
        console.profuse("    Seque auxes of {0}\n".format(self.name))

        for aux in self.auxes:
            aux.segue()


    def precur(self): 
        """Calls preacts (prior to recu) pre-recurring acts for self
           Preacts are used for:
              1) Setting up conditions for transitions and conditional auxes 
              2) Interrupting the frame flow such as
                 a) transitions
                 b) conditional auxiliaries
                 or other actor subclasses of Interrupter

              setup is considered part of the transition evaluation process.

              When the act.actor is of Interruptor (sub)class indicated by having
                 the attribute _interruptive the the action returns truthy
                 return then preact execution is aborte as per a sucessful
                 transition or conditional aux

           called by self.framer.segue()
        """
        console.profuse("    Precur {0}\n".format(self.name))

        for act in self.preacts:
            if act() and hasattr(act.actor, '_interruptive'):
                return True

        return False

    def exit(self):
        """calls exacts exit acts for self 
        """
        console.profuse("    Exit {0}\n".format(self.name))

        for aux in self.auxes: #since auxes entered last must be exited first
            aux.exitAll()
            aux.main = None #release aux to be used by another frame

        for act in self.exacts:
            act() #call Exit Action

    def rexit(self):
        """calls  rexacts rexit acts for self 
        """
        console.profuse("    Rexit {0}\n".format(self.name))

        for act in self.rexacts:
            act() #call rexit Action

    def addBeact(self, act):
        """        """
        self.beacts.append(act)

    def addEnact(self, act):
        """         """
        self.enacts.append(act)

    def addRenact(self, act):
        """         """
        self.renacts.append(act)

    def addReact(self, act):
        """         """
        self.reacts.append(act)

    def addPreact(self, act):
        """         """
        self.preacts.append(act)

    def addTransact(self, act):
        """         """
        self.transacts.append(act)

    def addExact(self, act):
        """         """
        self.exacts.append(act)

    def addRexact(self, act):
        """         """
        self.rexacts.append(act)

    def addAux(self, aux):
        """         """
        self.auxes.append(aux)

    def addByContext(self, act, context):
        """Add act to appropriate list given context
           called by builder
        """

        if context == ENTER:
            self.addEnact(act)
        elif context == RECUR:
            self.addReact(act)
        elif context == PRECUR:
            self.addPreact(act)
        elif context == EXIT:
            self.addExact(act)
        elif context == RENTER:
            self.addRenact(act)
        elif context == REXIT:
            self.addRexact(act)
        elif context == BENTER:
            self.addBeact(act)      
        else:
            return False

        return True #needed since builder uses it



def TestFrame():
    """Module Common self test


    """
    import acting
    import poking
    import needing
    import goaling
    import deeding
    import traiting
    import fiating
    import wanting


    try:
        Frame.Clear() #clear registry

        #set up main framework
        f1 = Frame(name = 'Primero')
        f2 = Frame()
        f3 = Frame()
        f1.attach(f2)
        f1.attach(f3)
        f4 = Frame()
        f5 = Frame()
        #f2.attach(Frame())
        f2.attach(f4)
        f3.attach(f5)


        #Frame.ShowHierarchy()

        #Act class Transact class
        Act = acting.Act
        Transact = acting.Transact

        #Action instances
        need = acting.need
        goal = acting.goal
        deed = acting.deed
        trait = acting.trait
        spec = acting.spec
        fiat = acting.fiat

        #a() #t()
        a = Act(action = need, act = need.checkDepth, parms = dict(depth = 5.0))
        f2.beacts.append(a)

        a = Act(action = goal, act = goal.setDepth, parms = dict(depth = 2.0))
        f2.enacts.append(a)

        a = Act(action = trait, act = trait.useDepth, parms = dict(depth = 3.0))
        f2.reacts.append(a)
        a = Act(action = deed, act = deed.doDepth, parms = dict(depth = 1.0))
        f2.reacts.append(a)

        a = Act(action = trait, act = trait.useDepth, parms = dict(depth = 6.0))
        f2.exacts.append(a)

        t = Transact()
        a = Act(action = need, act = need.checkDepth, parms = dict(depth = 4.0))
        t.needs.append(a)
        t.far = f5
        f2.transacts.append(t)

        a = Act(action = deed, act = deed.doDepth, parms = dict(depth = 1.0))
        f2.preacts.append(a)

        t = Transact()
        a = Act(action = need, act = need.checkDepth, parms = dict(depth = 1.5))
        t.needs.append(a)
        t.far = f4
        f5.transacts.append(t)

        #setup auxiliary framework
        f6 = Frame()
        a = Act(action = trait, act = trait.useDepth, parms = dict(depth = 10.0))
        f6.reacts.append(a)
        #setup aux framer
        fr1 = Framer()
        fr1.first = f6
        f3.auxes.append(fr1)

        #a = Act(action = fiat, act = fiat.tellStart, parms = dict(framer = fr1))


        #set up main framer
        fr2 = Framer()
        fr2.first = f1

        fr2.runner.send(START)

        for i in xrange(3):
            print ""
            status = fr2.runner.send(RUN)


    except excepting.ParameterError, ex1:
        print ex1
        raise

    return f1

def Test():
    """Module Common self test



    """
    TestFrame()


if __name__ == "__main__":
    Test()

