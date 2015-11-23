"""monitoring.py monitoring communications etc


"""
#print("module {0}".format(__name__))

from ..aid.sixing import *
from .globaling import *

from ..aio.udp import PeerUdp
from . import excepting
from . import tasking

from ..aid.consoling import getConsole
console = getConsole()


#Class definitions
class Monitor(tasking.Tasker):
    """Monitor Task Patron Registry Class for monitoring IP host port

       Usage:
    """
    #Counter = 0
    #Names = {}

    def __init__(self, host = '', port = 23456, dhost = '10.0.2.162', dport = 23456, **kw):
        """Initialize instance.

           iherited instance attributes
           .name = unique name for machine
           .store = data store

           .period = desired time in seconds between runs must be non negative, zero means asap
           .stamp = time when tasker last ran,
           .status = operational status of tasker
           .desire = desired control asked by this or other taskers
           .done = tasker completion state True or False
           .runner = generator to run tasker

           instance attributes
           .console = nonblocking io console object
           .host = host
           .port = port
           .ha = host port tuple
           .server = non blocking udp socket server object
           .dha = destination address (host, port)
        """
        super(Monitor,self).__init__(**kw) #status = STOPPED  make runner advance so can send cmd


        self.console = aiding.ConsoleNb()  #create console object for Non Blocking IO

        #create socket server
        self.host = host
        self.port = port
        self.ha = (self.host, self.port)
        self.server = PeerUdp(host = self.host,port = self.port, path = '')

        self.dha = (dhost, dport) #set up destination address

    def reopen(self):
        """Closes if open then opens    """
        if not self.console.open():
            return False

        if not self.server.reopen():
            return False

        return True

    def close(self):
        """Close open connections"""
        self.server.close()
        self.console.close() #close file descriptor to console

    def makeRunner(self):
        """generator factory function to create generator to run this monitor
        """
        #do any on creation initialization here
        console.profuse("     Making Monitor Task Runner {0}\n".format(self.name))

        self.status = STOPPED #operational status of tasker

        try:
            while (True):
                control = (yield (self.status )) #accept control and yield status
                console.profuse("\n     Iterate Monitor {0} with control = {1} status = {2}\n".format(
                    self.name,
                    ControlNames.get(control, 'Unknown'),
                    StatusNames.get(self.status, 'Unknown')))

                self.desire = RUN #default what to do next time, override in frame

                if control == RUN:
                    if self.status == STARTED or self.status == RUNNING:
                        self.status = RUNNING
                        console.profuse("     Running Monitor {0} ...\n".format(self.name))

                        data, sa = self.server.receive() #result tuple (data, sourceaddress)

                        # server.receive always returns a two element tuple.
                        #if no data the tuple is ('',None)
                        if sa:
                            shost, sport = sa
                            #self.console.put(shost + ': ' + data + '\n') #put on console

                            self.console.put(shost + ': ' + data) #put on console

                        line = self.console.getLine()

                        if line:
                            if line[0].lower() == 's':
                                self.status = STOPPED
                                console.profuse("     Stopping Monitor {0} ...\n".format(self.name))
                                self.close()
                                self.done = True
                            else:
                                self.done = False
                                result = self.server.send(line, self.dha)
                                self.console.put(str(result) + '\n')

                    else:
                        console.profuse("     Need to Start Monitor {0}\n".format(self.name))
                        self.desire = START

                elif control == READY:
                    self.status = READIED
                    console.profuse("     Readying Monitor {0} ...\n".format(self.name))

                elif control == START:
                    self.status = STARTED
                    console.terse("     Starting Monitor {0} ...\n".format(self.name))

                    self.reopen()
                    self.done = False

                elif control == STOP:
                    if self.status == RUNNING or self.status == STARTED:
                        self.status = STOPPED
                        self.desire = STOP
                        console.terse("     Stopping Monitor {0} ...\n".format(self.name))
                        self.close()
                        self.done = True #only done if complete successfully
                    else:
                        console.terse("     Monitor {0} not started or running.\n".format(self.name))

                elif control == ABORT:
                    self.status = ABORTED
                    console.profuse("     Aborting Monitor {0} ...\n".format(self.name))

                    self.close()
                    break #break out of while loop. this will cause stopIteration

                else: #control == unknown error condition bad control
                    self.desire = ABORT
                    self.status = ABORTED
                    console.profuse("     Aborting Monitor {0}, bad control = {1}\n".format(
                        self.name,  CommandNames[control]))

                    self.close()
                    break #break out of while loop. this will cause stopIteration

                self.stamp = self.store.stamp

        finally:
            console.profuse("     Exception causing Abort Monitor {0} ...\n".format(self.name))
            self.desire = ABORT
            self.status = ABORTED
            self.close()

class MonitorOut(Monitor):
    """MonitorOut Monitor Task Patron Registry Class for sending to ip host port

       Usage:
    """

    def __init__(self, host = '', port = 60000, dhost = '10.0.2.162', dport = 23456, **kw):
        """Initialize instance.

           iherited instance attributes
           .name = unique name for machine
           .store = data store

           .period = desired time in seconds between runs must be non negative, zero means asap
           .stamp = time when tasker last ran,
           .status = operational status of tasker
           .done = tasker completions state True or False
           .desire = desired control asked by this or other taskers
           .runner = generator to run tasker

           .console = nonblocking io console object
           .host = host
           .port = port
           .ha = host port tuple
           .server = non blocking udp socket server object
           .dha = destination address (host, port)
        """
        super(MonitorOut,self).__init__(host = host, port = port, dhost = dhost, dport = dport, **kw)

    def makeRunner(self):
        """generator factory function to create generator to run this monitor
        """
        #do any on creation initialization here
        console.profuse("     Making Monitor Task Runner {0}\n".format(self.name))

        self.status = STOPPED #operational status of tasker

        while (True):
            control = (yield (self.status )) #accept control and yield status
            console.profuse("Iterate Monitor {0} with control = {1} status = {2}\n".format(
                self.name,
                ControlNames.get(control, 'Unknown'),
                StatusNames.get(self.status, 'Unknown')))

            self.desire = RUN #default what to do next time, override in frame
            self.stamp = self.store.stamp

            if control == RUN:
                self.status = RUNNING
                console.profuse("Running Monitor {0} ...\n".format(self.name))

                #line = self.console.getLine().strip()
                line = self.console.getLine()

                if line:
                    if line[0].lower() == 's':
                        self.status = STOPPED
                        console.profuse("Stopping Monitor {0} ...\n".format(self.name))

                        self.server.close()
                        self.console.close() #close file descriptor to console
                        self.done = True
                    else:
                        self.done = False
                        result = self.server.send(line, self.dha)
                        self.console.put(str(result) + '\n')

            elif control == READY:
                self.status = READIED
                console.profuse("Readying Monitor {0} ...\n".format(self.name))

            elif control == START:
                self.status = STARTED
                console.profuse("Starting Monitor {0} ...\n".format(self.name))

                self.console.open() #reopen file descriptor to console
                self.server.open() #open socket server
                self.done = False

            elif control == STOP:
                self.status = STOPPED
                console.profuse("Stopping Monitor {0} ...\n".format(self.name))

                self.server.close()
                self.console.close() #close file descriptor to console
                self.done = True

            elif control == ABORT:
                self.status = ABORTED
                console.profuse("Aborting Monitor {0} ...\n".format(self.name))

                self.server.close()
                self.console.close() #close file descriptor to console
                self.done = True
                break #break out of while loop. this will cause stopIteration

            else: #control == unknown error condition bad control
                self.status = ABORTED
                console.profuse("Aborting Monitor {0}, bad control = {1}\n".format(
                    self.name,  CommandNames[control]))

                self.server.close()
                self.console.close() #close file descriptor to console
                self.done = True
                break #break out of while loop. this will cause stopIteration


