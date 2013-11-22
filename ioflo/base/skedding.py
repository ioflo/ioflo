"""skedding.py weightless thread scheduling


"""
#print "module %s" % __name__

import time
from collections import deque

from .consoling import getConsole
console = getConsole()


from .odicting import odict
from .globaling import *

from . import aiding
from . import excepting
from . import registering
from . import storing
from . import tasking
from . import building

from .consoling import getConsole
console = getConsole()


class Skedder(object):
    """Schedules weightless tasker objects based on generators.

       run method runs the skedder main loop until interrupted or all taskers 
       completed

       taskers is a dictionary of taskers indexed by tasker name

       The skedder maintains lists of taskers in various execution states
          Each list determines what the skedder does with the tasker.
          The skedder has methods that move taskers between the lists and
              also notifies taskers of their control

          Skedder runs tasker and sends it a control
          Tasker runs using control and yields its status

          Each tasker as a .desire attribute that indicates what the next
          desired control should be.

          Each tasker as a .period attribute that indicates how ofter the tasker
          should be run

          There are three deques the skedder maintains. Each entry in each deque
          is a tuple (tasker, retime, period) 
             tasker is reference to tasker object
             retime is time that the tasker should next be run
                a retime of zero means runs asap or always
             period is the time period between runs

          ready = deque of tuples where taskers are ready to be run
             If need different priorities then need to add a 
                ready list for each priority

          stopped = deque of tuples where taskers stopped awaiting start

          aborted = deque of tuples where taskers aborted can't be restarted

          addStoppedTask(tasker) adds tasker to stopped list
          addReadyTask(tasker) adds tasker to ready list

       Everytime a tasker runs it yields a status that the skedder uses to determine
       what to do with the tasker

       instance attributes:
       .name = skedder name string
       .period = time seconds between iterations of skedder
       .stamp = current iteration time of skedder
       .real = real time IF True ELSE simulated time
       .timer = timer to time loops in real time
       .elapsed = timer to time elapsed in mission

       .houses = list of houses to be scheduled

       .ready = deque of tasker  tuples ready to run
       .aborted = deque of tasker tuples aborted


    """

    def __init__(  self,
                   name="Skedder",
                   period=0.125,
                   stamp=0.0, 
                   real=False,
                   houses=None,
                   filePath='',
                   mode=None,
                   behavior='',
                   username='',
                   password='', 
                   metaData=None):
        """Initialize Skedder instance.
           parameters:
           name = name string
           period = iteration period
           stamp = initial time stamp value
           real = time mode real time True or simulated time False
           houses = list of houses
           filePath = filePath to build file
           mode = parsing mode
           behavior = pathname to package with external behavior modules
           username = username
           password = password
           metaData = list of triples of (name, path, data) where
                        name = name string, path = path string, data = odict

        """
        self.name = name
        self.period = float(abs(period))
        self.stamp = float(abs(stamp))
        #real time or sim time mode
        self.real = True if real else False
        self.timer = aiding.Timer(duration = self.period)
        self.elapsed = aiding.Timer()
        self.house = houses or []
        self.filePath = filePath
        self.mode = mode or []
        self.behavior = behavior
        self.username = username
        self.password = password
        if metaData:
            self.metaData = metaData
        else:
            self.metaData = [
                ("plan", "meta.plan", odict(value="Test")),
                ("version", "meta.version", odict(value="0.7.2")),
                ("platform", "meta.platform",
                     odict([("os", "unix"), ("processor", "intel"), ])),
                ("period", "meta.period", odict(value=self.period)),
                ("real", "meta.real", odict(value=self.real)),
                ("filepath", "meta.filepath", odict(value=self.filePath)),
                ("mode", "meta.mode", odict(value=self.mode)), #applied mode logging only
                ("behavior", "meta.behavior", odict(value=self.behavior)), 
                ("credentials", "meta.credentials",
                     odict([('username', self.username), ('password', self.password)])), 
            ] 

        self.ready = deque() #deque of taskers in run order
        self.aborted = deque() #deque of aborted taskers


    def addReadyTask(self,tasker):
        """Prepare tasker to be started"""    
        if tasker.schedule == ACTIVE:
            tasker.desire = START
        else:
            tasker.desire = STOP

        tasker.status = STOPPED
        retime = tasker.store.stamp
        period = tasker.period
        trp = (tasker, retime, period) #make tuple
        self.ready.append(trp)
        console.profuse("     Add ready: {0} retime: {1} period: {2} desire {3}\n".format(
            tasker.name, retime, period, ControlNames[tasker.desire]))

    def build(self, filePath='', mode=None, metaData=None):
        """ Build houses from file given by filePath """

        console.terse("Building Houses for Skedder {0} ...\n".format(self.name))
        #use parameter otherwise use inited value
        if filePath: 
            self.filePath = filePath
        if mode:
            self.mode =  mode
        if metaData: 
            self.metaData = metaData

        b = building.Builder(fileName = self.filePath,
                             mode=self.mode,
                             metaData = self.metaData,
                             behavior=self.behavior)

        if not b.build():
            return False

        self.houses = b.houses

        for house in self.houses:
            meta = house.meta
            console.profuse("Meta Data for House {0}:\n{1}\n".format(house.name, house.meta))

        return True   

    def run(self):
        """runs all generator taskers in running list by calling next() method.

           Keyboard interrupt (cntl-c) to end forever loop
           Since finally clause closes taskers they must be restarted before
           run can be executed again
        """

        console.concise("Starting Skedder {0} ...\n".format(self.name))

        stamp = self.stamp
        for house in self.houses:
            house.store.changeStamp(stamp)
            ("Initialized store {0}:  stamp = {1} with {2}\n".format(
                house.store.name,  house.store.stamp, stamp))

            for tasker in house.taskables:
                self.addReadyTask(tasker)

        console.profuse("Ready taskers: {0}\n".format(
            ', '.join([tasker.name for tasker,r,p in self.ready])))
        console.profuse("Aborted taskers: {0}\n".format(
            ', '.join([tasker.name for tasker,r,p in self.aborted])))


        self.timer.restart()
        self.elapsed.restart()

        #make local reference for speed put out side loop?
        ready = self.ready
        #stopped = self.stopped
        aborted = self.aborted

        try: #so always clean up resources if exception   
            while True:
                try: #CNTL-C generates keyboardInterrupt to break out of while loop
                    console.profuse("\nRunning Skedder {0} at stamp = {1} real elapsed = {2:0.4f}\n".format(
                        self.name, self.stamp,  self.elapsed.elapsed))

                    more = False #are any taskers RUNNING or STARTED

                    for i in xrange(len(ready)): #attempt to run each ready tasker
                        tasker,retime,period = ready.popleft() #pop it off

                        if retime > stamp: #not time yet
                            ready.append((tasker,retime,period)) #reappend it
                            status = tasker.status

                        else: #run it
                            try:
                                status = tasker.runner.send(tasker.desire)  
                                if status == ABORTED: #aborted so abort tasker
                                    aborted.append((tasker,stamp,period))
                                    console.profuse("     Tasker Self Aborted: {0}\n".format(tasker.name))
                                else:
                                    ready.append((tasker,retime + period, period)) #append

                            except StopIteration: #generator returned instead of yielded
                                aborted.append((tasker,stamp,period))
                                console.profuse("     Tasker Aborted due to StopIteration: {0}\n".format(tasker.name))

                        if status == RUNNING or status == STARTED:
                            more = True

                    if not ready: #no pending taskers so done
                        print "     No ready taskers. Shutting down skedder ..."
                        break

                    if not more: #all taskers stopped or aborted
                        print "     No running or started taskers. Shutting down skedder ..."
                        break

                    #update time stamps
                    if self.real:
                        ("     Time remaining skedder = {0:0.4f}\n".format(self.timer.remaining))
                        while not self.timer.expired:
                            time.sleep(self.timer.remaining)
                        self.timer.repeat()

                    self.stamp += self.period
                    stamp = self.stamp
                    for house in self.houses:
                        house.store.changeStamp(stamp)

                except KeyboardInterrupt: #CNTL-C shutdown skedder
                    print "    KeyboardInterrupt forcing shutdown of skedder ..."

                    break

                except SystemExit: #User know why shutting down
                    print "    SystemExit forcing shutdown of skedder ..."
                    raise

                except Exception: #Let user know what exception caused shutdoen
                    print "    Surprise exception forcing shutdown of skedder ..." 
                    raise

            print "Total elapsed real time = %0.4f" % self.elapsed.elapsed

        finally: #finally clause always runs regardless of exception or not
            #Abort any running taskers to reclaim resources
            #Stopped or aborted taskers should have already released resources
            #if last run tasker exited due to exception then try finally clause in
            #its generator is responsible for releasing resources

            print "    Aborting all ready taskers ..."
            for i in xrange(len(ready)): #run each ready tasker once
                tasker,retime,period = ready.popleft() #pop it off

                try:
                    status = tasker.runner.send(ABORT)  
                    print "       Tasker '%s' aborted" % tasker.name
                except StopIteration: #generator returned instead of yielded
                    print "       Tasker '%s' generator already exited" % tasker.name

                #tasker.runner.close() #kill generator



def Test(real = False, verbose = False):
    """Module Common self test

    """
    import housing
    reload(housing)

    housing.ClearRegistries()

    print housing.Registries
    print
    print housing.Registries["tasker"].Names
    print housing.Registries["tasker"].Counter
    print

    house = housing.House()

    t1 = tasking.Tasker(name = 't1', store = house.store)
    t2 = tasking.Tasker(name = 't2', store = house.store)
    t3 = tasking.Tasker(name = 't3', store = house.store, period = 0.125)
    t4 = tasking.Tasker(name = 't4', store = house.store, period = 0.125)
    t5 = tasking.Tasker(name = 't5', store = house.store, period = 0.5)
    t6 = tasking.Tasker(name = 't6', store = house.store, period = 1.0)

    house.actives = [t1,t6,t2,t5,t3,t4]

    skedder = Skedder(name = "TestTasker", period = 0.125, real = real, houses = [house])
    skedder.run()


def TestProfile(real = False, verbose = False):
    """Module Common self test



    """
    import cProfile
    import pstats

    import housing
    reload(housing)

    housing.ClearRegistries()

    print housing.Registries
    print
    print housing.Registries["tasker"].Names
    print housing.Registries["tasker"].Counter
    print

    house = housing.House()

    t1 = Tasker(name = 't1', store = house.store)
    t2 = Tasker(name = 't2', store = house.store)
    t3 = Tasker(name = 't3', store = house.store, period = 0.125)
    t4 = Tasker(name = 't4', store = house.store, period = 0.125)
    t5 = Tasker(name = 't5', store = house.store, period = 0.5)
    t6 = Tasker(name = 't6', store = house.store, period = 1.0)

    house.actives = [t1,t6,t2,t5,t3,t4]

    skedder = Skedder(name = "TestSkedder", period = 0.125, real = real, houses = [house])
    #skedder.run()
    cProfile.runctx('skedder.run()',globals(),locals(), './test/profiles/skeddertest')

    p = pstats.Stats('./test/profiles/skeddertest')
    p.sort_stats('time').print_stats()
    p.print_callers()
    p.print_callees()

if __name__ == "__main__":
    Test()

