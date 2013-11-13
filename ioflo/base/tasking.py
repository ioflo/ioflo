"""tasking.py weightless thread scheduling


"""
#print "module %s" % __name__


from .globaling import *

from . import registering
from . import storing 

from .consoling import getConsole
console = getConsole()


def CreateInstances(store):
    """Create server instances which automatically get registered on object creation
       must be function so can recreate after clear registry
    """
    tasker = Tasker(name = 'tasker', store = store)

#Class definitions


class Tasker(registering.StoriedRegistry):
    """Task class, Base class for weightless threads

    """
    Counter = 0  
    Names = {}

    def __init__(self, period = 0.0, schedule=INACTIVE, **kw):
        """Initialize instance.

           iherited instance attributes
           .name = unique name for machine
           .store = data store

           instance attributes
           .period = desired time in seconds between runs,non negative, zero means asap
           .stamp = depends on subclass default is time tasker last RUN
           .status = operational status of tasker
           .desire = desired control asked by this or other taskers
           .done = tasker completion state True or False
           .schedule = initial scheduling context for this tasker vis a vis skedder
           .runner = generator to run tasker


        """
        if 'preface' not in kw:
            kw['preface'] = 'Task'

        super(Tasker,self).__init__(**kw)

        self.period = float(abs(period)) #desired time between runs, 0.0 means asap
        self.stamp = 0.0 #time last run
        self.status = STOPPED #operational status of tasker
        self.desire = STOP #desired control next time Task is iterated
        self.done = True # tasker completion state reset on restart
        self.schedule = schedule #initial scheduling context vis a vis skedder

        self.runner = None #reference to runner generator
        self.remake() #make generator assign to .runner and advance to yield

        self.source = None # future reference to share
        self.sourceFields = None #future reference to share fields

    def reinit(self, period=None, schedule=None, **kw):
        if period is not None:
            self.period = period

        if schedule is not None:
            self.schedule = schedule
        

    def remake(self):
        """Re make runner generator

           .send(None) same as .next()
        """
        self.runner = self.makeRunner() #make generator
        status = self.runner.send(None) #advance to first yield to allow send(cmd) on next iteration

        if console._verbosity >= console.Wordage.profuse:
            self.expose()

    def expose(self):
        """

        """
        print "     Task %s status = %s" % (self.name, StatusNames[self.status])

    def resolveLinks(self):
        """Resolves any by name links to other objects   """
        pass

    def start(self):
        """ready runner

        """
        return self.runner.send(READY)   

    def start(self):
        """start runner

        """
        return self.runner.send(START)

    def run(self):
        """run runner

        """
        return self.runner.send(RUN)

    def stop(self):
        """stop runner

        """
        return self.runner.send(STOP)

    def abort(self):
        """abort runner

        """
        return self.runner.send(ABORT)


    def makeRunner(self):
        """generator factory function to create generator to run this tasker

           Should be overridden in sub class
        """
        #do any on creation initialization here
        console.profuse("     Making Task Runner {0}\n".format(self.name))

        self.status = STOPPED #operational status of tasker
        self.desire = STOP #default what to do next time, override below
        self.done = True

        count = 0

        try:
            while (True):
                control = (yield (self.status)) #accept control and yield status
                console.profuse("\n     Iterate Tasker {0} with control = {1} status = {2}\n".format(
                    self.name,
                    ControlNames.get(control, 'Unknown'),
                    StatusNames.get(self.status, 'Unknown')))

                if control == RUN:
                    if self.status == STARTED or self.status == RUNNING:          
                        console.profuse("     Running Tasker {0} ...\n".format(self.name))
                        self.status = RUNNING
                    else:
                        console.profuse("     Need to Start Tasker {0}\n".format(self.name))
                        self.desire = START                     

                elif control == READY:
                    console.profuse("     Readying Tasker {0} ...\n".format(self.name))
                    self.desire = START
                    self.status = READIED

                elif control == START:
                    console.terse("     Starting Tasker {0} ...\n".format(self.name))
                    self.desire = RUN
                    self.status = STARTED
                    self.done = False

                elif control == STOP:
                    if self.status == RUNNING or self.status == STARTED:
                        console.terse("     Stopping Tasker {0} ...\n".format(self.name))
                        self.desire = STOP
                        self.status = STOPPED
                        self.done = True
                    else:
                        console.terse("     Tasker {0} not started or running.\n".format(self.name))

                elif control == ABORT:
                    console.profuse("     Aborting Tasker {0} ...\n".format(self.name))
                    self.desire = ABORT
                    self.status = ABORTED
                    self.done = True #only done if complete successfully

                else: #control == unknown error condition bad control
                    self.desire = ABORT
                    self.status = ABORTED
                    console.profuse("     Aborting Tasker {0}, bad control = {1}\n".format(
                        self.name,  CommandNames[control]))
                    break #break out of while loop. this will cause stopIteration         

                self.stamp = self.store.stamp

        finally: #in case uncaught exception
            console.profuse("     Exception causing Abort Tasker {0} ...\n".format(self.name))
            self.desire = ABORT
            self.status = ABORTED       


def Test(real = False, verbose = False):
    """Module Common self test

    """

    import housing
    reload(housing)
    import skedding

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

    skedder = skedding.Skedder(name = "TestTasker", period = 0.125, real = real, houses = [house])
    skedder.run()


def TestProfile(real = False, verbose = False):
    """Module Common self test



    """
    import cProfile
    import pstats

    import housing
    reload(housing)
    import skedding

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

    skedder = skedding.Skedder(name = "TestSkedder", period = 0.125, real = real, houses = [house])
    #skedder.run()
    cProfile.runctx('skedder.run()',globals(),locals(), './test/profiles/skeddertest')

    p = pstats.Stats('./test/profiles/skeddertest')
    p.sort_stats('time').print_stats()
    p.print_callers()
    p.print_callees()


if __name__ == "__main__":
    Test()
