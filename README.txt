
![Logo](docs/images/ioflo_logo.png?raw=true)

#Ioflo

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
```
```text

usage: ioflo [-h] [-V] [-v VERBOSE] [-c CONSOLE] [-p PERIOD] [-r] [-R]
             [-n NAME] -f FILENAME [-b [BEHAVIORS [BEHAVIORS ...]]]
             [-m PARSEMODE] [-U USERNAME] [-P PASSWORD] [-S [STATISTICS]]

Runs ioflo. Example: ioflo -f filename -p period -v level -r -h -b
'mybehaviors.py'

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         Prints out version of ioflo.
  -v VERBOSE, --verbose VERBOSE
                        Verbosity level.
  -c CONSOLE, --console CONSOLE
                        File path name to console log file.
  -p PERIOD, --period PERIOD
                        Period per skedder run in seconds.
  -r, --realtime        Run skedder at realtime.
  -R, --retrograde      Shift skedder timers when retrograde clock detected.
  -n NAME, --name NAME  Skedder name.
  -f FILENAME, --filename FILENAME
                        File path to FloScript file.
  -b [BEHAVIORS [BEHAVIORS ...]], --behaviors [BEHAVIORS [BEHAVIORS ...]]
                        Module name strings to external behavior packages.
  -m PARSEMODE, --parsemode PARSEMODE
                        FloScript parsing mode.
  -U USERNAME, --username USERNAME
                        Username.
  -P PASSWORD, --password PASSWORD
                        Password.
  -S [STATISTICS], --statistics [STATISTICS]
                        Profile and compute performance statistics. Put
                        statistics into file path given by optional argument.
                        Default statistics file path is
                        /tmp/ioflo/profile/NAME.
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
         set elapsed with 20.0
         set heading with 0.0
         set depth with 5.0
         set speed with 2.5
         go next if elapsed >= goal

      frame eastleg
         set heading with 90.0
         go next if elapsed >= goal

      frame southleg
         set heading with 180.0
         go next if elapsed >= goal

      frame westleg
         set heading with 270.0
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

### Documentation

github

https://github.com/ioflo/ioflo_manuals

#### License
APACHE 2.0

#### Supported Python Versions
Python 2.6

Python 2.7

Python 3.4
