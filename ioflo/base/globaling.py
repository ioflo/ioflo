"""globaling.py module with global constants

"""


import sys
import math
import re
from collections import namedtuple

from ..aid.sixing import *  # Python2to3 support

#Globals
#Constant Definitions

#FlowScript build reporting indentations
INDENT_ADD = '      '
INDENT_CREATE = '     '

#Task generator control values
STOP = 0
START = 1
RUN = 2
ABORT = 3
READY =  4
ControlNames = { STOP : 'Stop', START : 'Start', RUN : 'Run', ABORT : 'Abort', READY : 'Ready',}

#Task generator operational status
STOPPED = STOP
STARTED = START
RUNNING = RUN
ABORTED = ABORT
READIED = READY
StatusNames = { STOPPED : 'Stopped', STARTED : 'Started', RUNNING : 'Running', ABORTED : 'Aborted', READIED : 'Readied', }
StatusValues = { 'Stopped' : STOPPED, 'Started' :  STARTED, 'Running' : RUNNING, 'Aborted' : ABORTED, 'Readied' : READIED,}

#log rule values
NEVER = 0
ONCE = 1
ALWAYS = 2
UPDATE = 3
CHANGE = 4
STREAK = 5
DECK = 6
LogRuleNames = {NEVER : 'Never', ONCE : 'Once', ALWAYS : 'Always',
                UPDATE : 'Update', CHANGE : 'Change', STREAK : 'Streak', DECK: 'Deck',}
LogRuleValues = {'Never' : NEVER, 'Once' : ONCE,  'Always' : ALWAYS,
                 'Update' : UPDATE, 'Change' : CHANGE, 'Streak' : STREAK, 'Deck' : DECK,}

#Task schedule context
INACTIVE = 0
ACTIVE = 1
AUX = 2
SLAVE = 3
MOOT = 4
ScheduleNames = { INACTIVE : 'inactive',
                  ACTIVE : 'active',
                  AUX : 'aux',
                  SLAVE : 'slave',
                  MOOT : 'moot'}
ScheduleValues = { 'inactive': INACTIVE ,
                   'active':  ACTIVE,
                   'aux': AUX,
                   'slave': SLAVE,
                   'moot': MOOT}

#Task ordering
MID = 0
FRONT = 1
BACK = 2

OrderNames = { MID : 'mid', FRONT : 'front', BACK : 'back'}
OrderValues = { 'mid': MID , 'front':  FRONT, 'back': BACK}

# Frame action contexts  should change these to enums
NATIVE = 0
ENTER = 1
RECUR = 2
PRECUR = 3
EXIT = 4
RENTER = 5
REXIT = 6
BENTER = 7
TRANSIT = 8

ActionContextValues = { 'native': NATIVE , 'enter':  ENTER, 'recur': RECUR,
                        'precur': PRECUR, 'exit': EXIT, 'renter': RENTER,
                        'rexit': REXIT, 'benter': BENTER}
ActionContextNames = { NATIVE : 'native', ENTER : 'enter', RECUR : 'recur',
                       PRECUR : 'precur', EXIT : 'exit', RENTER : 'renter',
                       REXIT : 'rexit', BENTER : 'benter'}

ActionSubContextValues = {'transit': TRANSIT}
ActionSubContextNames = { TRANSIT : 'transit'}



#Precompile re match objects

#regular expression objects to quickly determine if string is valid python identifier
#Usage: REO_Identifier.match('Hello') returns match object if match otherwise None
REO_Identifier = re.compile(r'^[a-zA-Z_]\w*$') #valid python identifier
REO_IdentPub = re.compile(r'^[a-zA-Z]\w*$') #valid python public identifier ie no leading underscore

# regex objects to determine if string is valid store path
# to use
#if REO_Path.match(s):
#  then s is valid path

REO_RelPath = re.compile(r'^([a-zA-Z_]\w*)+([.][a-zA-Z_]\w*)*$')  # not start with dot
REO_DotPath = re.compile(r'^([.][a-zA-Z_]\w*)+$')  # starts with dot
REO_Path = re.compile(r'^([a-zA-Z_]\w*)+([.][a-zA-Z_]\w*)*$|^([.][a-zA-Z_]\w*)+$')  # dotpath or relpath
REO_PathDotPath = re.compile(r'^([a-zA-Z_]\w*)+([.][a-zA-Z_]\w*)+$|^([.][a-zA-Z_]\w*)+$') # at least one dot

# allows path to end in dot or not for node paths
REO_RelPathNode = re.compile(r'^([a-zA-Z_]\w*)+(([.][a-zA-Z_]\w*)*$|([.][a-zA-Z_]\w*)*[.]$)')  # not start with dot
REO_DotPathNode = re.compile(r'^([.][a-zA-Z_]\w*)+$|^([.][a-zA-Z_]\w*)+[.]$')  # starts with dot
REO_PathNode = re.compile(r'^([a-zA-Z_]\w*)+(([.][a-zA-Z_]\w*)*$|([.][a-zA-Z_]\w*)*[.]$)|^([.][a-zA-Z_]\w*)+$|^([.][a-zA-Z_]\w*)+[.]$')

#regex object to split hafscript command line
#REO_Chunks = re.compile(r'#.*|[^ "]+|"[^"]*"')
REO_Chunks = re.compile(r"""#.*|[^ "']+|"[^"]*"|'[^']*'""")
# Usage
# chunks = REO_Chunks.findall(s)

# to match each part
REO_Quoted = re.compile(r'^"[^"]*"$')
REO_QuotedSingle = re.compile(r"^'[^']*'$")
REO_Comment = re.compile(r'^#.*$')
REO_Plain = re.compile(r'^[^ "]+$')
#Usage
# if REO_Quoted.match(s):
#    s.strip('"')

#regex object determine if lat or lon is in human readable form
#REO_LATLONPOS = re.compile(r'^([0-9]+)[N,E,n,e]([0-9]+\.[0-9]+)$')
REO_LatLonNE = re.compile(r'^(\d+)[N,E,n,e](\d+\.\d+)$')
REO_LatLonSW = re.compile(r'^(\d+)[S,W,s,w](\d+\.\d+)$')
#Usage
# ll = REO_LatLonNE.findall(s) #returns list of tuples of groups [(deg,min)]
# if ll:
#   deg = float(ll[0][0])
#   min = float(ll[0][1])
#   fracdeg = deg + min/60.0


#  Various Point namedtuple objects
Pxy = namedtuple('Pxy', 'x y')  # Cartesian
Pxyz = namedtuple('Pxyz', 'x y z')  # Cartesian right hand order
Pne = namedtuple('Pne', 'n e')  # World mapping North East
Pned = namedtuple('Pned', 'n e d')  # World mapping North East Down right hand order
Pfs = namedtuple('Pfs', 'f s')  # Body Forward Starboard
Pfsb = namedtuple('Pfsb', 'f s b')  # Body Forward Starboard Below right hand order

REO_PointXY = re.compile(r'^([-+]?\d+\.\d*|[-+]?\d+)?[X,x]([-+]?\d+\.\d*|[-+]?\d+)[Y,y]$')
REO_PointXYZ = re.compile(r'^([-+]?\d+\.\d*|[-+]?\d+)[X,x]([-+]?\d+\.\d*|[-+]?\d+)[Y,y]([-+]?\d+\.\d*|[-+]?\d+)[Z,z]$')

REO_PointNE = re.compile(r'^([-+]?\d+\.\d*|[-+]?\d+)[N,n]([-+]?\d+\.\d*|[-+]?\d+)[E,e]$')
REO_PointNED = re.compile(r'^([-+]?\d+\.\d*|[-+]?\d+)[N,n]([-+]?\d+\.\d*|[-+]?\d+)[E,e]([-+]?\d+\.\d*|[-+]?\d+)[D,d]$')

REO_PointFS = re.compile(r'^([-+]?\d+\.\d*|[-+]?\d+)[F,f]([-+]?\d+\.\d*|[-+]?\d+)[S,s]$')
REO_PointFSB = re.compile(r'^([-+]?\d+\.\d*|[-+]?\d+)[F,f]([-+]?\d+\.\d*|[-+]?\d+)[S,s]([-+]?\d+\.\d*|[-+]?\d+)[B,b]$')
