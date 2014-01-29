
![Logo](docs/images/ioflo_logo.png?raw=true)

#ioflo

##Enabling The Programmable World

http://ioflo.com

## Getting Started

### Installation

``` bash

$ pip install ioflo


```

on OS X

``` bash
$ sudo pip install ioflo

```

### Command Line

``` bash
$ ioflo -h
usage: ioflo [-h] [-v VERBOSE] [-p PERIOD] [-r] [-V] [-n NAME] [-f FILENAME]
             [-b [BEHAVIORS [BEHAVIORS ...]]] [-U USERNAME] [-P PASSWORD]

Runs ioflo. Example: python go -f filename -p period -v level -r -h -b 'mybehaviors.py'

optional arguments:
  -h, --help            show this help message and exit
  -v VERBOSE, --verbose VERBOSE
                        Verbosity level.
  -p PERIOD, --period PERIOD
                        Period per skedder run in seconds.
  -r, --realtime        Run skedder at realtime.
  -V, --version         Prints out version of ioflo.
  -n NAME, --name NAME  Skedder name.
  -f FILENAME, --filename FILENAME
                        File path to FloScript file.
  -b [BEHAVIORS [BEHAVIORS ...]], --behaviors [BEHAVIORS [BEHAVIORS ...]]
                        Module name strings to external behavior packages.
  -U USERNAME, --username USERNAME
                        Username.
  -P PASSWORD, --password PASSWORD
                        Password.

```

Example:

Put the following  into the file box1.flo

``` text

#example mission box1.flo

house box1

   framer vehiclesim be active first vehicle_run
      frame vehicle_run
         do simulator motion uuv
   
   framer mission be active first northleg
      frame northleg
         set elapsed to 20.0
         set heading to 0.0
         set depth to 5.0
         set speed to 2.5
         go next if elapsed >= goal
      
      frame eastleg
         set heading to 90.0
         go next if elapsed >= goal
      
      frame southleg
         set heading to 180.0
         go next if elapsed >= goal
      
      frame westleg
         set heading to 270.0
         go next if elapsed >= goal
      
      frame mission_stop  
         bid stop vehiclesim
         bid stop autopilot
         bid stop me
   
   framer autopilot be active first autopilot_run
      frame autopilot_run
         do controller pid speed
         do controller pid heading
         do controller pid depth
         do controller pid pitch

```

To run

```bash
$ ioflo -v terse -f box1.flo

```

Something like this should print on the console.

```text
----------------------
Building ...
Building Houses for Skedder Skedder ...
   Created house box1. Assigning registries, creating instances ...
   Built house box1 with meta:
       plan: Share {'value': 'Test'}
       version: Share {'value': '0.7.2'}
       platform: Share {'os': 'unix', 'processor': 'intel'}
       period: Share {'value': 0.125}
       real: Share {'value': False}
       filepath: Share {'value': 'box1.flo'}
       mode: Share {'value': []}
       behaviors: Share {'value': []}
       credentials: Share {'username': '', 'password': ''}
       name: Share {'value': 'box1'}
     Warning: Nonexistent goal share goal.heading ... creating anyway
     Warning: Transfer into non-existent field 'value' in share goal.heading ... creating anyway
     Warning: Nonexistent goal share goal.depth ... creating anyway
     Warning: Transfer into non-existent field 'value' in share goal.depth ... creating anyway
     Warning: Nonexistent goal share goal.speed ... creating anyway
     Warning: Transfer into non-existent field 'value' in share goal.speed ... creating anyway
   Ordering taskable taskers for house box1
   Resolving house box1
     Resolving framer vehiclesim
     Resolving framer mission
     Resolving framer autopilot
   Tracing outlines for house box1
     Tracing outlines for framer vehiclesim
     Tracing outlines for framer mission
     Tracing outlines for framer autopilot


Starting mission from file box1.flo...
   Starting Framer vehiclesim ...
To: vehiclesim<<vehicle_run> at 0.0
   Starting Framer mission ...
To: mission<<northleg> at 0.0
   Starting Framer autopilot ...
To: autopilot<<autopilot_run> at 0.0
To: mission<<eastleg> at 20.0 Via: northleg (go next if elapsed >= goal) From: <northleg> after 20.000
To: mission<<southleg> at 40.0 Via: eastleg (go next if elapsed >= goal) From: <eastleg> after 20.000
To: mission<<westleg> at 60.0 Via: southleg (go next if elapsed >= goal) From: <southleg> after 20.000
To: mission<<mission_stop> at 80.0 Via: westleg (go next if elapsed >= goal) From: <westleg> after 20.000
   Stopping autopilot in autopilot_run at 80.000
   Stopping vehiclesim in vehicle_run at 80.125
   Stopping mission in mission_stop at 80.125
No running or started taskers. Shutting down skedder ...
Total elapsed real time = 0.2099
Aborting all ready taskers ...
   Aborting vehiclesim at 80.125
       Tasker 'vehiclesim' aborted
   Aborting mission at 80.125
       Tasker 'mission' aborted
   Aborting autopilot at 80.125
       Tasker 'autopilot' aborted

----------------------


```


* Automated reasoning engine

* Automation operating system

* Flow based component programming frameowork

* Hierarchical action framework

* Concurrent micro-threading framework

* Comprehensive pub/sub framework

* Dependency injection framework

* Contectual Computation Engine




![FloScript](docs/images/floscript_logo.png?raw=true)

# FloScript

* Convenient, user friedly configuration language for ioflo

* Hierachical

* Expressive

* Extensible

* Scalable

* Practicle


### Apache v2 license

# Quick Start


# Introduction


![SysArch](docs/images/IofloSysArch.png?raw=true)

![ArchParts](docs/images/IofloArchParts.png?raw=true)

![Contexts](docs/images/IofloContexts.png?raw=true)

![Envelope](docs/images/IofloReliableEnvelope.png?raw=true)





![ORecurse](docs/images/ioflo_o_recurse.png?raw=true)

