------------------
CHANGE LOG
-------------------

--------
20191028
--------
 2.0.0

Python 3.7.4 or later from now on latest version of python


--------
20191028
--------

1.7.7

Fixed TLS certs in tests
Fixed up as version to split to Python3. Python2 is now deprecated ioflo1 is the
  version to support python2  so 1.X.X
  ioflo  version 2.X.X will require python 3.7+


--------
20190820
--------

1.7.6

Some bug fixes



--------
20180915
--------

1.7.5

Some refactoring
The ioflo project will have two version branches. The version 1.X.X  branch
will maintain  compatibility with Python 2.7.X and Python 3.5.  But this will be mainly
maintenance and backport of some new features

New development and features will by in large be done in the 2.X.X version branch
which will require Python 3.6.X and will follow updates to Python without
maintaining backwards compatibility to old versions of Python. There are too
many innovative features in Python 3.6 that Ioflo wants to exploit.


--------
20170913
--------

1.7.4

Use unquote_plus for query args
Fixed bug in Valet erroneously unquoting query_string for environ
Added python3.6 condition to exclude test from python2
Patron.response now returns namedtuple to make it more convenient to access fields
Improved stability of Patron parsing responses from slow servers
Some refactoring of Patron and Valet
Fixed windows bug in serialing
change Share so .update or .create when passed in another Share works
Fixed issue with using transmit with Patron if waiting on request/response.
Refactored to add Patron.request method that uses existing parameters to generate
   a new request and append  to .requests. This honors .waiting flag

--------
20170830
--------

1.7.3

Move classing import of Generator for python2

--------
20170829
--------

1.7.2

Fixed bug not clearing .data in Respondent
Added some support for Falcon HTTPErrors in WSGI Responder

Added HTTPError class for errors raised while iterating WSGI app

Changed aio.http.serving.Responder to use HTTPError

Now handles return values from new style generators in WSGI respondent

Now Patron connector.accept will reopen as needed makes it easier to send requests

Some refactoring

Added codesponsor

Some refactoring of Patron and support classes

Added attributize decorator of generator functions or methods that supports attributed
assignment Decorator also injects ref to wrapper into arg list of generator function
method


Added support via ."_status" and ."_headers" to allow AttributiveGenerator
in WSGI response to update status and headers after start but before first
non-empty write as attributes on decorated generator.

Fixed patron trasnmit so can be used for first time request

Added utility function parseQuery

fixed bugs in lodict

Added .respond convenience method to Patron

--------
20170814
--------

1.7.1

Fixed python2 support in new functions in timing module


--------
20170808
--------

1.7.0

Fixed but in tcp/serving on test for incoming socket formation

--------
20170720
--------

1.6.9

Refreshed ssl certs for unit tests


--------
201702XX
--------

1.6.8

Added more point in polygon functions in vectoring
Fixed tests to reference TLS certs in test directory not in /etc/pki/..
Added posix timestamp that works for both python 2.7+ and is aware
Added optilnal aware keyword parameter to iso8601
Fixed tuuid so includes microseconds


--------
20170110
--------

1.6.7

changed setup.py to use setuptools_git so create full sdist will all git files
Changes debugging



--------
20161212
--------
1.6.6

Bugfixes

Added fix for IPV6  replaced socket.gethostbyname with new function
aioing.normalizeHost that uses socket.getaddrinfo that supports ipv6


--------
20161013
--------
1.6.5

Support for named nested cloned auxiliaries. Each framer now has an .auxes odict
that keeps track of clones per framer. This allows refrencing aux clone by its
tag name instead of full name.

New syntax and semantics for if aux name is done  when aux the name resolution
looks in the framer.auxes instead of the global Framer.Names
This new syntax will break FloScripts that reference cloned auxilaries.


Changed default case for actor inode when act.inode empty and frame inode context
empty and framer inode context empty

Simplified semantics of aux as mine clause

Changed default marker format from framername.framename to framername<framename
to avoid confusion with data store path naming conventions.

--------
20161007
--------
1.6.4

Fixed bug in how local ioinit inode path was computed.

--------
20161006
--------
1.6.3

Added support for nested frame inode contexts using new via clause on frame
declaration.  frame name via inode

Fix bugs

--------
20161002
--------
1.6.2

Aux via now supports nested auxes and will walk up the main framer outline
prepending any main, me, or relative addressed via clauses.
If main or me skip to the main framer via of the current framer.
If relative prepend the framer via. If absolute or starts with framer then
terminate prepend at that point.

Refactored algorithm and added tests for correctness. handles main and not main
and relative nested.

Refactored the initio processing and resolvePaths to support multi level via
Also normalized syntax of framer inode relative "me." Store paths.
me means prepend the framer inode if any and also keep walking up aux.main.framer
links to successively prepend inodes until either absolute or framer relative


Changed ._initio signature to odict or item list so order is preserved
Do verb per clause now overrides for clause
        with clause now overrides from clause
        cum clause now overrides qual clause

For clause now correctly interprets indirec starting with "me"
Some refactoring of .resolve

Some more tests flos

--------
20160924
--------
1.6.1

added by marker clause. Change syntax and semantics of if updated/changed need

Added special transit sub-context of precur when segue is successful. This
sub-context is used by the if updated and if changed to insert special transit act
(tract) resets mark when the transition holding the need succeeds. This prevents
holes in detecting updates or changes.

Removed the aft clause on the if updated need

Added .datetime and .time to store default contents so all have access to current
real date time current relative time in addition to .realtime


Added reuse option to the logger declaration to reuse log files on reruns. This
is most useful when rotation is enabled.

Added minimum size option to logger declaration for log rotation to occur

--------
20160910
--------
1.6.0

Added log file rotation support via new options keep copies and cycle term
to logger declaration


Changed default logger base prefix directory to be in users home folder
~/.ioflo/log/

Breaking changes to FloScript syntax for Log and Loggee. This allows for more
flexible specification of fields to be logged. The defualt shorthand is now
more compact to write. Also supports logging of dicts stored in a Share's deck
deque. there are three forms based on the log rule

log test on (once, never, always, update, change)
  loggee source [as tag] [source [as tag]] ...

source:
    [(value, fields) in] (path, dotpath)

log test on streak
  loggee [(value, fields) in] (path, dotpath) [as tag]

log test on deck
  loggee fields in (path, dotpath) [as tag]


Removed FIFO and LIFO log rules and replaced with streak log rule which is fifo.

Fixed log so does not store last values unles rule on change is used

Fixed log so that only the fields present in share when log prepare (during startup)
is called are logged by default. This prevents inadvertent additon of fields to share
from messing up log columns


Added syntax to FloScript for setting field values to namedtuple Point type classes.
6 classes supported for three 2D and three 3D for the XY, XYZ, NE, NED, FS, and
FSB coordinate systems.  Syntax is to include letters with the axis as in
10x5y3z



Added "aft" connective to is updated need so can change the comparison to > instead
of default >=

Added aid.quaternioning module with some simple quaternion operations

Added aid.vectoring module with some simple operations on vectors:
  mag, mag2, norm, dot

Some refactoring of aid.navigating module


Made some breaking changes to the Need Floscript syntax. This code was getting
cumbersome and difficult to augment/enhance so needed refinement in the syntax

This may break some floscripts. Hopefully this will solidify the syntax going
forward and allow for easier enhancement of new needs

Added 're' as connective 're' means about or in regard or in reference to
Used for framer state and frame goal references in Needs and 'set' verb we
we can disambiguate

Expanded use of 'is' as a connective to also be a comparison like connective
Added it to reserved connectives list (bug not to be there already)

Conditionals (Need) are used in the following verbs

go target [if conditional [and conditional ...]]
let target [if conditional [and conditional ...]]
aux target [if conditional [and conditional ...]]


Old Syntax:
    always
    done tasker
    done (any, all) [in frame [(me, framename)][of framer [(me, framername)]]]
    status (me, tasker) is (readied, started, running, stopped, aborted)
    update [in frame (me, framename)] indirect
    change [in frame (me, framename)] indirect
    elapsed comparison framergoal [+- tolerance]
    recurred comparison framergoal [+- tolerance]
    state [comparison goal [+- tolerance]]

    [(value, field) in] indirect [comparison goal [+- tolerance]]

New Syntax:
    state [comparison goal [+- tolerance]]

    (elapsed, recurred) [re [me]] comparison framergoal
        [+- tolerance]

    indirect is (updated, changed) [in frame (me, framename)]

    tasker is done

    (auxname, any, all)
        [in frame [(me, framename)]
        [in framer [(me,framername)]]] is done

    (me, tasker) is (readied, started, running, stopped, aborted)

    state:
        [(value, field) in] indirect

    goal:
        value
        [(value, field) in] indirect

    comparison:
        (==, !=, <, <=, >=, >)

    tolerance:
        number (the absolute value is used)

    framergoal:
        goal
        value
        [(value, field) in] indirect

--------
20160528
--------
1.5.5

Bug fixes

Refactor classes in Stacking and Devicing
Added TCPStack

Added more exception handling to tcp client and server

FloScript Breaking Changes
   Reducing some redundancy and normalizing connective use across verbs

These may break some floscripts
Removed "if always" need form since its never needed anymore

Dropped 'by' connective from 'inc' verb syntax
as redundant with 'from'  connective

Deprecated 'to' connective of 'inc' verb syntax
as redundant with 'with'  connective

Dropped 'to' and 'by' connectives from 'set' verb syntax
as redundant to "with" and 'from'

Dropped 'to' and 'by' connectives from 'do' verb syntax
as redundant to "with" and 'from'

Added "frame" modifier to if update/change need syntax to be consistent with
rear raze

--------
20160506
--------
1.5.4

Fix some bugs

Added reverse parameter to (un)bytify (un)packify packifyinto to make is easier
to deal with little endian

---
20160504
--------
1.5.3


Added support in floscript parsing for verb statement continuation with
connective prepositional clauses. So if a subsequent line starts with a connective
it is appended to the preceeding verb declaration statement.
Also blank and comment lines between clauses are skipped
This allows more flexible formatting of long statements by putting clauses/phrases
on new lines as long as the line starts with the connective. Also allows interspesing
comments.

Added constraint that Tasker, Framer, Frame names can not be Reserved words
this is to make syntax highlighting easier in the future. Reserved words (connectives
and comparisons) act like keyworks for that purpose and verbs act like built ins

--------
20160503
--------
1.5.2

packifyInto now extends b to be long enough if too short

Added Stamper class to provide Store like protocol interface for managing
relative time stamp

Added aio.proto package with base classes for creating async packetized protocols
using aio

Refreshed TLS certs for unittests

Refactord floscript field parsing to ensure field names cannot be reserved connectives
unless quoted

--------
20160311
--------
1.5.1

Refactored so load dump are for the generic json or msgpack

Added buffer flushes to pyserial (requires pyserial 3.0)

Added size parameter to unpackify so can unpack just part of input

Added packifyInto function

Added signExtend function

---------
20151221
---------
1.5.0

Fixed Incomer TCP connection to have refreshable attribute to refresh connection
timeout whenever there is activity on the connection.

---------
20151208
---------
1.4.9

Fixed http server to handle HTTPError like exceptions when not caught by wsgi app


---------
20151208
---------
1.4.8

Fixed bug http server wsgi environment variable type for content-length


---------
20151207
---------
1.4.7

Fixe bug in http server handling of chunked not sending empty terminating chunk

---------
20151127
---------
1.4.6

Fixed bugs in http server handling of empty request bodies


---------
20151124
---------
1.4.5

Added exports of Patron and Valet classes to aio.http package

---------
20151124
---------
1.4.4

Updated storing module classes properties to use decorator syntax
Refactored aid package into smaller sub modules for better future proofing
Refactored async io modules to be in new aio package with finer granularity for
future proofing
Minor bug fixes and improvements
More unittests

---------
20151018
---------
1.4.3

Fixed typo

---------
20151018
---------
1.4.2

Refactored consoling package location still supports old location
As ioflo helper libraries are growing in size, refactoring now to make it less
likely to need change in future as other projects become dependant.


---------
20151016
---------
1.4.1

Refactored the httping.py module into a package http with submodules as the
the size of the module was getting unwieldy

Refactored naming of Deed. Now alised with Doer. Preferred it Doer.
Deedify now aliased with preferred Doify
Actorify not alised with preferred Actify




---------
20151015
---------
1.4.0

Added Valet a WSGI server class that works within Ioflo

Changed interface to packify unpackify

Some refactoring of nonblocking tcp classes to remove unneeded extra deque
stage on input

Refactor header parsing of http responses

Requestant and respondant are now subclass of Parsent
Added .error and .errored attributes of Parsent so can report errors in processing
or waiting

Parsent close method now being called if connection closed prematurely


---------
20150819
---------
v1.3.9

Added support for serial driver stack for higher level serial protocol nonblocking
on top of raw nonblocking serial port

Added some utility functions



---------
20150715
---------
v1.3.8

Refactored base.aiding to aid.aiding and then split out groups of utility
functions into metaing, navigating, timing, blending

use sixing for 2to3 in more places
Some other refactoring

Use of ioflo.base.aiding is deprecated. Use ioflo.aid.aiding. In the future
base.aiding will be removed.

Move odicting and osetting to aid.  base.odicting base.osetting references still
exist by are deprecated use aid.odicting aid.osetting

added modict (multiple valued odict) class to odicting


---------
20150708
---------
v1.3.7


Fixed bug in httping processing chunked encoded responses
Changed default encoding for x-www-form-urlencoded to utf-8
Support for multipart/form-data for POST request forms with utf-8



---------
20150624
---------
v1.3.6

changed parameter to fargs for form args from form to be consistent with qargs

---------
20150623
---------
v1.3.5

added support for http url encoded form data in Requester and Patron

---------
20150623
---------
v1.3.4

fixed bug in http copy

---------
20150623
---------
v1.3.3

Added redirects field to response returned when request is redirected in Patron
Some bug fixes and minor changes to httping


---------
20150610
---------
v1.3.2

Fixed bug in value parsing due to new None as valid value

---------
20150610
---------
v1.3.1

Added framer inode relative 'me' to path resolution so put set etc can use framer inode relative addressing as per ionints
Added 'of me' relation clause so can perform inode relative addessing

---------
20150609
---------
v1.3.0

Refactoring of httping classes to normalize interfaces
Requester now accepts data dictionary that it automatically jsonifies on build


---------
20150608
---------
v1.2.9

Patron now passes through copy of request odict to reponses copy so that requester
can add tracking and return information to request that shows up in response

---------
20150604
---------
v1.2.8

Fixed bug with Nact   go .. if not ... in Need expression


---------
20150604
---------
v1.2.7

do verb via connective now supports paths that end with dot or not

do verb by/from, for, qua, now all use all the fields in the source if a field
   list is not provided

values of field value expressions can now be unquoted path strings

Support for optional via inode clause in framer verb to provide framer wide
   prefix for ioinit inodes

Support for optional via inode clause in aux verb for cloned aux framers to
   provide override of aux framer via clause on invocation of aux verb

Semantics of aux via inode is to prepend main framer via inode unless
   the aux via inode is absolute or main or mine. if main then use main framer's
   via inode if mine then ignore main framer's via inode


---------
20150603
---------
v1.2.6

FloScript now supports single quoted values in addition to doubled quoted

Exchanged 'qua' and 'via' connective semantics in 'do' verb because via is more commmon


---------
20150601
---------
v1.2.5

Added aid.httping with classes for nonblocking http client
See class aid.httping.Patron

Added 'qua' connective to 'do' verb to allow easier setting of inode

---------
20150515
---------
v1.2.4

renamed python 2 to 3 compat module


---------
20150515
---------
v1.2.3

Some refactoring of repository directory structure. Added ioflo.aid as
sub-package for utility modules. Started moving some stuff out of .base
into .aid. Left reference in .base for now but deprecated in future.

ioflo.base.nonblocking is deprecated use ioflo.aid.nonblocking instead

Added support for nonblocking tcp/ip and tcp/ip + tls client and server classes
in aid.nonblocking

Added support for nonblocking http client in aid.httping


---------
201503XX
---------
v1.2.2

Updated docs



---------
20150305
---------
v1.2.1

Moved nonblocking io classes to ioflo.base.nonblocking from ioflo.base.aiding



---------
20150305
---------
v1.2.0

Added script alises ioflo3 for ioflo on python3 and ioflo2 for ioflo on python2

Changed syntax of "bid" verb: Now supports optional "at period" clause that
allows changing the iteration period of framer

Added retrograde and parsemode options to ioflo script

Changed syntax of "do" verb:  Made with and from connectives aliases for to and by
repectively to be consistent with other verbs. Replaced with and from in do verb
with cum and via respectively

Changed interface for Actor Class (Deed subclass)
.postinitio is no longer supported. It was deprecated in version 1.1.5.
The correct one to use is ._prepare

---------
20150213
---------
v1.1.9

More Skeddar timer fixes

---------
20150213
---------
v1.1.8

Added MonoTimer to Skeddar that detects if system clock is retrograded.

---------
20150204
---------
v1.1.7

Added binary create mode for OCFN utility function. Needed for P3 support
if using msgpack.

---------
20150129
---------
v1.1.6

Renamed Registry class to Registrar class to avoid confusion with .Registry
in RegisterType metaclass

Added Ordered Set class called oset or OSet in base.osetting.py


---------
20150120
---------
v1.1.5

Changed interface for Actor Class (Deed subclass)
.postinitio is not ._prepare
for backwards compatibility .postinitio  is still supported but is deprecated
and will no longer be supported in a future version.

Changed Actor .act to ._act



---------
20150113
---------
v1.1.4


Add scaffolding for unit tests of Deeds (behaviors) inside House, Framer, Frame
contexts in file ioflo.test.testing



---------
20150109
---------
v1.1.3

More consistent usage of resolveFrameOfFramer

Added Deck class to storing.py


## Deck for streaming data

Added .deck attribute to share that is the dual of .data but for streams.
A share now has both .data and .deck so it can have both streams and other data.

Deck Object is subclass of python deque but with convenience methods
to avoid ambiguity about which side of deque to use.
these are .push .pull  which are aliases for
.append .popleft
Also convenience methods .gulp .spew. .gulp will ignore non None elements
and .spew will return None when empty instead of raising IndexError

Decks are not time stamped.  The philosophy is that the elements
on a deck are dicts or objects that encapsulate their time stamps.
The use case is to flush a deck when processing so time stamps are not
meaningful


This means that Shares who's main purpose is to hold a  message queue
don't have to assign a deque to their .value
but can just use their .deck attribute.
This supports the alternate but important use case
where a share is used to hold a buffer of messages or events (stream) and not a
single value or multivalued fields of values (data)




---------
20150107
---------
v1.1.2

Added support for rear and raze verbs.
the rear verb enables runtime as opposed to resolve time creation of insular auxiliary clones
These reared auxes can be destroyed at runtime using the raze verb
This enables the creation of temporary insular auxiliary clones. When razed
the memory for the clone is released.

rear original [as mine] [be aux] in frame framename

raze (all, last, first) [in frame [(me, framename)]]

---------
20150105
---------
v1.1.1

Added preliminary support for insular clones
Added if done (any, all) [in frame [framename] [of framer [framername]]]
Added support for
   aux framer as mine
   aux framer as mine if ...

Where mine specifies an insular aux clone framer whose name is auto generated
at resolve time and is not available to floscript verbs


---------
20141209
---------
v1.1

Added improvements to done verb and bid verb

Fixed related bugs

Added support for cloning auxiliary framers. This is provided via the
      aux framer as clonename
   form of the aux verb
   Only framers whose schedule kind is moot may be cloned.

Added support for inline relative addressing syntax and removed goal and state
   varients of relative addressing as these are imcompatible
   special cases of recurred and elapsed still supported

Support for ioflo has test run using reporting via house metas

Added framer schedule type of moot, when moot, house builder does not call
   resolveLinks on the framer. When moot the framer
   is meant to be cloned. ResolveLinks will be called on the clones

Added actor, main, and me relative addressing in "of" clauses
Refactored so all share resolution happens at resolve time not parse time
Refactored so all frame and framer resolution happens at resolve time not parse time
Deprecated current server command as will be changing syntax significantly
Got rid of tasker command as only use subclasses Framer, Logger, Server
Refactor and clean up code
Change default inode path in resolvePath to "framer.me.frame.me.actor.me"
Raises error if duplicate unders
Refactor so resolving Tasker links uses utility function more DRY
Refactor so resolving Framer and Frame links uses utility function to be more DRY
Replaced Restarter Actor with SideAct restart

---------
20141027
---------

Changed how version author metadata is handled to fix import problem with
Python 2.6



---------
20141002
---------
v1.0.0

Changed license to Apache 2.0
1.0 release

---------
20140923
---------

v0.9.40

Added WinMailslotNb  Class for non blocking comms on windows to replace SocketUxdNb

Added better support for Python3



---------
20140724
---------

v0.9.39

Cleanup some non python3 compatible print statement in tests
Lint cleanup

---------
20140630
---------

v0.9.38

change console log file cli parameter to not be required


---------
20140630
---------

v0.9.37

change console log file to append mode so multiple can write to it without
overwiting




---------
20140630
---------

v0.9.36

Added console log file path capability
app.run.run now has parameter consolepath that specifies files path to log
console messages instead of stdout

ioflo script now has command line parameter -c --console for same



---------
20140605
---------

v0.9.35

fixed command line version
ioflo -V
to work properly



---------
20140605
---------

v0.9.32

Added exitAll() to framer microthread abort

More verbose socket error messages for servers

Some lint like cleanup of parameters


---------
20140416
---------

v0.9.30

Changed Class naming convention for Actors/Deed Registery to get rid of
reverse camel convention. This was causing confusion to new users and it was the
result of a now obsolete historical convention in the way IoFlo managed behavior
registration for FloScript.

Unfortunately this change breaks any FloScripts/behaviors (sub classes of Actor or Deed)
that were created using the old convention. The FloScripts do not need to be changed
but the ClassNames need to be changed so they will be found.

The new Convention is to use Cap Camel Case for the Class Name but the order
of the camel case segments is not reversed to generate the FloScript do verb name
as previously.  Also when using .__register__ the name parameter argument value
should be captital camel case not lower camel case.

So everything is consistent now


---------
20140415
---------

v0.9.21

Refactored ioflo.app.run.run profiling and parameters
Now ioflo.app.run.start is just and alias for ioflo.app.run.run


---------
201404XX
---------

v0.9.20

Everything seems to be running in Python3


---------
20140401
---------

v0.9.19

Now running in Python3 basic test missions. Probably some corner conditions


---------
20140401
---------

v0.9.18

Addes preliminary support for Python3 compatibility


---------
20140326
---------

v0.9.17

Resizes socket buffers if too small for non blocking UDP and UXD servers


---------
20140303
----------
v0.9.13

Changed metadata .metas
Added .preloads to Skedder and Builder for one way preload of data store whereas
metas is two way (access back to skedder through house.metas dict)

---------
20140303
----------
v0.9.12

Added umask to aiding.SocketUxdNb
Added check for missing directory path to

-----------
20140227
---------
v0.9.11

Added Non Blocking Unix Domain Socket Datagram class ServerUxdNb to aiding.py


-----------
20140222
---------
v0.9.07

Added StoreTimer utility class to aiding.py.
Timer that keeps time relative to Store.stamp


-----------
20140219
---------
v0.9.06

Minor cleanup
Changed name of Udpserver class


------------
20140205
-----------
v0.9.05

Added parms to metamethod __register__ and also Parms class attribute to Actor
   This allows setting a different set of default arguments to the action method
   parameters. Useful for alternate registrations of a given Actor class
   Updated the decorators to use as well.



------------
20140204
-----------
v0.9.03

Finished refactor of act actor managment and resolution with class based registry
   Added decorators actorify and deedify to make it easier to create custom do behaviors

Added at context clause to do verb to allow specifying context on a do by do basis
Updated documentation to use refined terminology of declarative sentences not commands
Changed builder error messages to use 'verb' not 'command'


-----------
20140125
-----------
v0.9.01

Added SideAct class that  uses .action attribute to call different method
   in its associated actor. This is to support conversion of special Actor on
   other actor/act to be SideAct on same actor but different mthod. So all in one
   place.

Refactored act.inits and act.ioints and registry so do not save empty dicts but
   save None. More memory efficient.
   ioints saved in Act are only the ones from builder not combined
   with registry (change where initio gets called not in resolve but before resolve)
   also change it so Act has by default None for ioints and inits to save space.

Replaced deactivator with new SideAct class and new way to do anciliary actors

do verb now supports with and from clauses to setup inits

-------------
20140124
------------

v0.9.0

This version is incompatible with previous versions.

A major refactor of the "Action" (Actor) Registration method and resolution
for Framers to simplify custom Action programming and also enable easier framer
cloning was added.

Refactor Actor registration internally to use new metaclass and refactor resolution
to that Actor creation is done at resolve time not build time. This gets rid
of need for createIntances for Actors. This also makes it easier to specify new Actions
since all in one place.

Some syntax changes.

Tasker command is broken still

load command file path is now computed relative the the plan file in which the
load appears and not the directory where ioflo executable lives

--------
20140115
--------
v0.8.4

postinitio on Deeds not gets passed in **parms so ParamDeeds can do init on parms

Added console log message when skeddar fails to build

Added default preface to be .__class__.__name__ to Register init  so that any
   Registered subclass gets friendly appropriate name without having to have u
   unique .__init__ method just for the preface.
   removed all superfluous __init__ methods


---------
20140112
------------
v0.8.2

Added limited support for quoted field names in some commands

Removed salting.py ioflo distro to its own distro as it has hard dependency on SaltStack


Refactored how deed iois and ._iois are resolved. This now happens in resolveLinks
not in the builder. So now any parametric deed can be safely cloned if using relative
addressing for ioi and any as kind deed if using relative addressing.

Added support for resolving share refs at resolve time with storing.resolvePath
This supports framer/frame relative main framer/frame relative and actor relative
when using "me" and "main" for names.
Example
   framer.me
   framer.me.frame.me
   framer.name.frame.me
   framer.me.frame.name
   framer.main
   framer.main.frame.main
   framer.me.actor.me
   framer.main.actor.me
   framer.me.frame.me.actor.me
   framer.main.frame.main.actor.me
if actor name is 'me'  then use current actor's camel case name converted to path
Since acts have ref to actor, actor is always available in acts resolve links.


Added .frame, .context, .act (action execution) attributes to each Act instance.
Added _act key parms of each act whose value is self act
These will better support more elegant framer cloning

Added SerialNB class to aiding.py which uses and use termios configuriation
   of the serialport

Refactored aiding.SocketNB receive function to use errno
    import errno
    errno.EAGAIN is correct for the appropriate platform 35 on darwin and 11 on Linux
    also in python2.6 socket.error is a subclass of IOError which has .errno attribute
    so use that instead of first element of tuple and get rid of typeerror exception


-----------
20140103
---------
Version v0.8.0


Support for framer cloning with parametric deeds

Support for frame and framer relative inodes in deeds in with relinitio

Basic support for cloning auxes of clones

Support for markerNeed cloning
Support for doneNeed, statusNeed cloning
Support for bid cloning
Support for fiat (ready start stop abort) cloning

-----------
20131212
-----------

Added Marking (watch)capability to enable
   "if update share"
   and
   "if change share"
   capability

   Added to Share class .marks attribute which is odict of marks by frame
       values are mark objects with attributes that support last data and last stamp
       for share and rules for how to handle .rule see log for example.

       .marks keys are framenames

       The framenames will also be given to the associated
         actions via a parm to resolve to frame references upon resolvelinks

       .marks[frame].data = last copy of data like log does
       .marks[frame].stamp = last stamp

   Add new Need class.
   Add new Marker Actor class

   When encounter Need syntax for mark the following happens
      Adds Mark to .marks of appropriate type to Share
      Inserts marker enter action actor at front of enter actions list for the
            associated frame
      Checks to see if marker of same type for same share already exists so not
            duplicated
      Marker just saves the stamp or data to .mark of share
      Adds MarkNeed to seque
            MarkNeed evaluates mark for share when Need runs
            Frame is framename that get resolved to frame reference so can insert
            marker. if not current frame.

   New syntax

      go frame if update [in frame] sharepath
      go frame if change [in frame] sharepath


---------
20131211
----------

Changed so frame relative is always framer relative as well so can now specify
   which framer so can modify frame relative in a different
   framer. So two of clauses may appear.

       put true into stuff of frame small of framer big

       resolves to

       .framer.big.frame.small


Frame relative is now stored relative to the frame's framer
    .framer.framername.frame.name....
    not
    .frame.name....

    when using frame relative addressing the framer.name is now prepended so
    frame relative is always also framer relative
    since frame names are unique per framer not per store


Added framer.activeShr and framer.humanShr to store the active frame.name and human
   for the framer so can be logged.
   framer.name.state.active
   framer.name.state.human


When verbosity is >= 3 "verbose" print out of data share at start of mission
   now includes the initial values not just the fields so can see what the
   initial values ended up being


---------
20131210
----------

Updated version to 0.7.8

Made executable for ioflo called ioflo that is installed as a script
   that can be run from the command line using setup.py
   default setup.py installs this to
   /Library/Frameworks/Python.framework/Versions/2.7/bin/ioflo



------------
20131125
-------------

Changed 'do' semantics so that if name is not provided but 'as' is then use
   the default generated name for the deed instance.

Standardized connective usage for commands
   to, with are aliases for reference to direct data
   by, from are aliases for reference to indirect source

   The reason for having aliases is that commands may have a meaning that is
   confusion for one of the combinations. The goal is to use the shortest pair
   to/by  to direct by indirect but still allow for removing ambiguity.
   The example is the "inc" command

   inc share to data

   Would imply that the result if the command is that the value of share is data
   not that the value of share is share + data

   so

   inc share with data   could be used to remove ambiguity

   The biggest change is that  inc share by  semantics have changed


   So all the command that use to/from will now
   accept

   (to, with)/(by, from)

   For Deed and Tasker commands that allow initialization of io share at parse time
   the connectives are

   per data
   for source


Added  support for deeds that are to be inited via parameters not at parse
   time.  So if deed has attribute "._parametric" then process initio but instead of
   creating attributes for each init argument key add these keys to the parms
   dict for the Deed. Add check so can't use same key in "with" "per" as
    "to" "from"

   Refactored preinitio, initio and build of do to support.



Fixed ioflo package version author etc with setup.py like bottle

Go ioflo runner now uses argparse


Added capability to use external import to a given ioflo run with the
  -b --behavior  CLI and also behavior parameter which is module/package
  name that is imported and then added to the _Instances in trim/exterior/__init__.py

   Import under
     ioflo/trim/exterior

     Change trim so current are under

     ioflo/trim/interior
        /plain
        /fancy


    Enables import of arbitrary packages to get registered each time a new house is created.
    Pass in list of strings of directory paths to package roots
    Import when building from skedder. Use importlib to add to existing trim path or
    Create own module path.


---------
20131121 v0.7.4
-----------

Changed initio check on attribute so that allows reuse of deed in other frames
   use _iois to store attribute names created with initio. If name in _iois
   then print warning but proceed to init Otherwise raise ValueError as before


Exchanged semantics of 'with' and 'per' as 'with' is more like 'from' so more symmetric


Made nodes objects in Store that are modified odicts that have name property
   which is pathname of node in store. Convenience method byName to allow creating
   and chaining of Node

Refactored salting.py. To use shares instead of fields for status etc
   change status on overload to be a node not share and then the overload, onCount,
   offCount, healthy, deadCode.


Added postInit method to deeds to be called by initio


---------
20131108
---------


Commented out print module and print package lines


Converted existing Deeds to use new ioinit interface so that store shares are not
    created until a deed gets used in a floscript. See the salting.py for an example
    of how this is done. Easy way to convert is not use new interface but use old
    interfaces just .ioinit.update(oldargs)



Added .time share that is the store's time stamp .stamp. This gets reset by the skedder
in its .run method so corresponds to start of mission.



Changed license to MIT

got rid of "debug" variable

Add Log rules 'lifo' and 'fifo' that will log a mutable sequence or dict until empty
   This is useful to flush event deques etc. /This if for read only deques whoes
   purpose is solely to be logged not for consumption by something else.

Updated init protocol
inode instead of proem

Default value for inode is instance name split into path on uppercase

Removed some prints in building not done

---------
20131107
----------




salting.py mostly working

Updated to use new ioinit paradigm.
with this paradigm initializing the ioflo (inputs outputs)
is not performed until the Deed instance is used in a floscript.
There are three places to specify what the initialization of the ioflos will be when the instance is
used (not created)

1) import time in CreateInstances by updating the ioinit attribute of the newly created instance
   at parse time .initio(**.ioinit) is called to initialize in the store

2) Parse time in buildDo using the 'with' and/or 'per' connectives

3) link time (not yet implemented) with the "on link" clause in the do command

ipath instead of path
ival instead of valu
iown instead of iflo
ipri instead of ipri


Changed "with" use "to" for link time parameters to be consistent with "set"
   "inc" Updated do, tasker, server commands. Use "per" for init and "from"
   for link time so now the convention is.
   to data  from source with data per source
   where the with and per are init time and to and from are link time


Refactored so no more mulitple inheritance of Patron and Registry instead
added StoriedRegistry to include .store. and Share has its own .store.
This allows using slots for Actors at least for the first few levels of inheritance.

Added __slots__ for Registry on down to Actors

Changed terminology. Store share path are nodes and tip not group.

Registries now odicts
.

----------
20131024
---------

-- Initial pass at Salt Stack integration. New trim/fancy/salting.py module

-------
20131101
--------

-- meta first node in store
-- addNode createNote methods on store


---------
20131023
----------

-- Bump version to 0.7.0

-- change version tov 0.6.4
-- change indent to 4 from 3
-- change licence to apache2


-- Lots of refactoring of console printout when running Skedder

-- Change Tasker to Skedder and Task to Tasker. Break out skedder into its own module
   refactor Server, Monitor, Tasker Framer

-- Replace verbose with Console object that acts like logger but not threaded
   but writes to file. Default is stdout

   Refactor __init__ Verbose it don't have
   to be redefined in each __init__.py but instead recursively pull the globals
   from each module . That is they define module level globals


    def Verbose(level = 1):
       """Sets the modules' verbose level
          Must redefine this function in each module since the global namespace
          is the namespace of the defining module not the calling module
       """
       global _verbose, __all__
       level = int(level)
       _verbose = level

       #call the Verbose function on all modules named in __all__
       gns = globals() #get global namespace which includes modules
       for m in __all__: #assume module of name == m already imported
          gns[m].Verbose(level)




---------
20131017
--------

-- add line continuation character \ or continue needs if end in 'and'.

-- refactor tasker to be skedder then refactor task to be tasker

-- Refactor CreateActors so it don't have
   to be redefined in each __init__.py but instead recursively pull the globals
   from each module . That is they define module level globals

    def CreateActors(store):
          """Makes new instances of actors. Should have blank registry
             Must redefine this function in each module since the global namespace
             is the namespace of the defining module not the calling module
          """
          global _InstanceModules

          if _verbose: print "Creating actors for package %s" % __name__
          for module in _InstanceModules:
             module.CreateActors(store = store)


-- Add task command and normalize other task commands.
    currently each type of task gets its own command

    framer name options
    server kind name options
    logger name options

    where options are repectively:
    [at period] [first frame][be scheduled] [in order]

    [at pd] [rx h:p] [tx h:p][be sd] [in or] [to px]

    [at pd] [to px] [be sd] [in or]

    But we need generic task
    task name [modifier ...] options

    where name [modifier ...] allows us to name space tasks like we do deeds
    For example server has recon specific defaults in building.py these
    should not be there but should be in task definition specific not in builder.

    so each specific task type would instead be of form

    framer name [modifier ...] options

    createInstances passes in store to all instances in registry are in same
    store. Need to update tasks so get store same way in stead of manually
    pasing in,




---------
20131009
----------


-- refactor resolvLinks so always to checks for type outside of if to convert name
    to object. Some resolveLinks were not right.

-- added **kw to resolveLinks method of actors so that if additional parms passed
   it will not cause reolveLinks to fail

-- fixed status need was not working

-- done need now can be used on any Task not just framers and not just aux and slave

-- Added READY control and READIED status to Tasks so can check if slave task
   can be started independent of actually trying to start
   -- Add ready control to indicate that a task is ready to start
    so can explicity do the checkstart for framers
    and allow other task to indicate if ready to start.


-- Added ready command to send ready control to slave task

-- Change done need so will allow slave framers

-- added .done attribute to Task so all tasks have attribute

-- added READY control else block to all runner methods of all existing task classes

-- Changed Frame.precur so it checks to see if act.actor is an interruptive class
   indicated by it having the attr ._interruptive. This makes it so other actors
   besides needs can be used in beacts in that they return something besides Falsy
   so that the beact semantics work but can also be used in preacts without messing up the
   preact processing for transistions.


   In general the  policy should still be that action methods return None unless
   there is a use case to do otherwise such as would be used in a beact or the actor
   is interruptive such as Transitor and Suspender (transisiton and conditional auxes)

   The ReadyFiat is a use case where it can be used in a beact to determine if
   a slave framer is ready to be run before transitioning to the frame

   ready testslave #benter




-- Get rid of tell command. this allows new tell command (below)
    replace old
    tell task (start stop run abort)
    with new
    (start stop run abort) task  as slave tasks require explicit control this
    makes it more convenient. Only can work with slave framers/tasks.

    operate slave framers/tasks using new (start stop run abort) slave commands
    so activity  is explict runs slave framer/task generator directly and not
    done automatically by Tasker

    use the 'status' need conditions for slave tasks
        if status task is started, running, stopped, aborted


-- names to resolve should be checked by builder for valid "identifier" re
    at parse time not at resolve time
        aux framer
        over frame
        under frame
        first frame
        framer first frame


---------
20131008
--------

-- Add with and from connectives to deed command so can pass in at runtime
   direct and indirect values to deed Actor.action() method.


-- Add support to all actors for run time parameters to action method
   .action(**kw)


-- make deed name spacing generic now its a list of one or more name parts
      genre and kind optional for deed parsing
        do genre kind name

-- repeat command similar to timeout command implicit transact

    repeat 3

    go next if recurred >= 3

    which does it 4 times  0 1 2 3


---------
20131007
--------

-- Fix the timeout command which was using obsolete code before makeDirectNeed and preact

--  replace repeat goal with reccured.
    Although iter is shorter and closer in meaning as repeat is strong verb form
    iter is too much like python iterm built in and would be confusing to python
    programmers while not meaning anything to non python programmers
    so maybe use recurred to be the recur count and is syntactically similar to
    elapsed

-------
20131004
---------

-- Reorder need conditions so target comes first easier to parse and will eventually
    allow multiline conditions

    let [me] if condition (Beact Benter) Other verbs (en, come, allow, admit)
    go target if condition (Transition
    aux target if condition (Conditional Aux)



-------
20131003
---------


-- get rid of behaving directory in haf.base
   move arbiting.py to haf.base
   move rest of the behaviors to the trim directory

-- have tasker inject metadata into build so there is hook back for build task
    to put stuff
   The metadata is not in each House as an odict house.meta of items (name, share)
   When each House is created an image of the metadata shares is created for that house
   The tasker has access to the meta data via its .houses list

-- Change Scaffold terminology to House to avoid meaning collison for testing scaffolds


-- refactor tasker so that tasker does the build, i.e. tasked calls builder
    this will eventually allow
    tasker to run as daemon and autobuild based on config file.

-- Refactor so all imports are relative using from . import syntax so guarantee
   that do not import module from some place else. The old way of doing relative
   imports where a simple
     import mymodule
   would first look in the same directory
   as the importing module and then look in sys.path means there is a chance
   of importing the wrong thing. Using the new relative import
     from . import mymodule
   guarantees the correct thing is imported. (See Beazley)






---------
20130407
---------

Added BENTER benter context and beact support
not tested.

-- Should context commands be verbs or nouns? exit is the same for both noun and verb
    I think verb since precur and recur do not have noun form.
    benter  - beacts (not bentry)

    enter - enacts (not entry)
    renter - renacts (not rentry)

    precur - preacts
    recur - reacts

    rexit - rexacts
    exit - exacts




---------
20130301
---------

Refactor directory layout to use HG mercurial and subprojects get AUV
and WHOI specific actions in separate folder

Put private repo on bitbucket
-- Repository on BitBucket
    https://bitbucket.org/smithsamuelm/HalfScript need to commit setup


-- Fixed circular import
Had some kind of circular import problem that an instance of Store, store
was failing isinstance(store, Store)
I fixed it by replacing absolute imports from haf with the new relative imports
using from . import





-------------
20100211
---------------
   Made it compatible with python 2.6 and python 2.7
   The incompatibility is that starting with pyton2.6 the root object's __init__
   and __new__ methods no longer accept any arguments. this is a problem when
   you have multiple inheritance with one class that accepts arguments.

   the workaround is to define a dummy object that inherits from object
   who's __init__ method throws away any argurments and use this object instead
   of the root object.

   For new just don't pass in the arguments.

   Dummy object defined in registering is Corpus. So Patron and Registry class
   now inhereit from Corpus instead of object and Data objects new method no longer
   calls object new with parameters.


   TypeError: object.__init__() takes no parameters

   DeprecationWarning: object.__new__() takes no parameters
  return object.__new__(cls, uri)


---------
20090611

0.5.5

-- Many changes to the recon interface and the recon associated commanders
and observers and the server. Refactored everything so could track acknowledgments
   and send retries if not acked. Also auto refresh the version and control messages
   so only have to set them once in the haf script.


-- Major change to time stamps in shares. Now during build time the time stamps
are set to None (similar to how logger does it for tracking updates). The
time stamp does not get a real number until somebody updates the share after the mission
has started. This way a commander that is checking a share to see if its been updated
will see the first update even if it occurs on the very first cycle when store.stamp
= 0.0. This means that any time stamp math must account for the time stamp being None
comparisons are OK as any number is > None. No Exceptions. but if do math add or subtract
a number and None then it raises a TypeError exception.  I fixed all the existing
controllers so that this works.


-- Had to change the log behavior as now not only the last update could be None
but the current stamp of the logged share. Now log on update and log on change always
log once to get initial values in the log.





---------
20090530

-- Refactored the directory structure to enable expansion and others to add code
   Also refactored to be able to put all the files that are recon specific in one
   directory. The analogy is base (as in base package or foundation) for the core
      and trim as in (trim package or extras) for application specific

   haf
      base   (these are the base set of files for haf functionality
         behaving  (these are the standard basic actors

      trim
         recon
         front

   to do this had to figure out alot about the import statement
   also laid groundwork to go to version 2.7 where absolute_import is required
   need to scan through files and make all imports absolute

-- Made the importing a function of list __all__

-- CreateActors is now initiated at the module level not from house (scaffold) object

-- Replaced debug with _verbose so can use verbose levels to
   filter what gets printed. _verbose  is a global
   level 0 means no verbose
   level 1 is old verbose
   level 4 is old debug

   go -v 1


--------
20090529

-- Added support for storing modem rx messages in deque in share

-- Added support for Server log files  to log exchanges of packets
   server command now has to prefex option (works like logger)

------------------------
20090527 0.5.3+

-- replaced  ask with  bid command so can use ask for something else

-- added collective "all" to bid command so can stop/start all active/inactive tasks
   to do this added .house attribute to store
   this way have access to store.house.taskables so actions can set the .desire
   of all taskables to stop

   bid stop all

   also made it so bid command can be applied to a list of tasks

   bid stop task1 task2 ...

-- Changed Convert to recognize 80W25.0345 45N36.123 formats for lat lon

-- Changed strings constants in recon interfacing to all be uppercase
   format set is lower case (both VtoR RtoV)

-- Fixed up recon server of pending commands to send from for loop

-- Normalized convention for naming Observer Commander Recon Server shares
   and attributes
   Adopt convention for server Store  all local shares for a server
   can always be found referenced off from

   serverkind.rx.messagename[.messagevariant] for vehicle to remote
   serverkind.tx.messagename[.messagevariant] for remote to vehicle

   recon.rx.depth.depth
   recon.rx.adcp

   recon.tx.depth.depth
   recon.tx.speed.mps

.goal
   .heading
      value
   .depth
      value
   .speed
      value
   .rpm
      value
   .recon
      .override
         value
      .rcp
         value
      .gpsfix
         iridium
      .exitpos
         lat  lon
      .modem
         ack  overwrite  data
   .rudder
      value
   .pitch
      value
   .stern
      value
   .elapsed

   .repeat



.recon
   .tx
      .heading
         .goal
            refresh  acked  headingGoal
      .depth
         .depth
            refresh  acked  depthGoal
      .speed
         .mps
            refresh  acked  speedMPSGoal
         .rpm
            refresh  acked  speedRPMGoal
      .override
         refresh  acked  enable
      .rcp
         refresh  acked  enable  rcp
      .set
         .gpsfix
            refresh  acked  iridium
         .exitpos
            refresh  acked  lat  lon
      .modem
         refresh  acked  ack  overwrite  data
   .rx
      .ctd
         temperature  conductivity  soundspeed  depth  salinity
      .fix
         kind  lat  lon
      .state
         hours  minutes  seconds  lat  lon  depth  depthGoal  altitude  pitch  roll  rpm  rpmGoal  speedMPS  heading  headingRate  headingGoal  mode  leg
      .adcp
         adcpAltitude  adcpHeading  adcpCurrentAhead  adcpSpeedUp  adcpSpeedAhead  adcpDown  adcpCurrentUp  adcpSpeedRight  adcpCurrentRight
      .depth
         .depth
            depthGoal
         .altitude
            altitudeGoal
         .triangle
            depthMin  depthMax  slope
         .unknown
            unknown
      .depth,trianglealt
         depthMin  altMin  slope
      .speed
         .rpmmps
            rpmGoal  speedMSGoal
         .unknown
            unknown
      .heading
         .goal
            headingGoal
         .rate
            headingRateGoal
         .destination
            latGoal  lonGoal
         .unknown
            unknown
      .fluorometer
         fluorometerGain  fluorometerValue
      .battery
         batteryAvailable  batteryCapacity  batteryPercentage
      .error
         errorCode  errorText
      .version
         .response
            versionDay  versionTime  versionMonth  versionYear
         .request
            versionRequest
      .route
         .leg
            leg  objective  latBegin  lonBegin  latEnd  lonEnd  depthAltTag  depthAlt  speed  speedUnits
         .legs
            legs  all
      .anchor
         pump  valve  fill  anchor  state
      .set
         kind  setter  lat  lon
      .mine
         valid  lat  lon  id  score1  score2  score3
      .modem
         .msg
            kind  source  dest  data
         .msgs
            msgs
      .ifla
         slant  altitude  down  range  pitch

.commander
   .recon
      .heading
         .parm

         .elapsed
            value
      .depth
         .parm

         .elapsed
            value
      .speed
         .parm

         .elapsed
            value
      .rpm
         .parm

         .elapsed
            value
      .override
         .parm

         .elapsed
            value
      .rcp
         .parm

         .elapsed
            value
      .gpsfix
         .parm

         .elapsed
            value
      .exitpos
         .parm

         .elapsed
            value
      .modem
         .parm

         .elapsed
            value

.observer
   .recon
      .ctd
         .parm

         .elapsed
            value
      .fix
         .parm

         .elapsed
            value
      .state
         .parm

         .elapsed
            value

-- Changed the convention for state  variables for recon
.state
   .recon
      .fix
         .gps
            value
      .mode
         value
      .mission
         .prelaunch
            value
         .launched
            value
         .suspended
            value
         .complete
            value
      .override
         .enabled
            value
         .depth
            value
         .rcp
            value
         .active
            value
         .forbidden
            value
      .power
         .shore
            value
      .leg
         value



20090526  0.5.2

-- Removed.done as attribute of task. NOw attribute of framer
   Fixed task runners
   Changed done need. and completion action

-- Refactored module and package so that can add deed files without redoing all
   imports pacage Behaving

-- Got rid of Transact and Trunact classes made new actors
   that has needs and far or aux s parms (better)
      Transiter
      Suspender
   used .done as flag to determine if Suspender has beed activated (cond aux)


-- Added a function to recursively set the debug variable
   for nested modules in packages such as behaving.arbiting etc
   new nested deeds breaks testing.Test debug option

-- Removed implicit Framer actions

--------------
20090521  = version 0.5.0+

-- Changed definition of value to be quoted string, boolean, number.
   if want a share field value to be a string string must be in double quotes now
   used regular expression to make chunks so that can chunk line correctly
   so that quoted string can include spaces, ', or # characters but not "
   Changed Convert now have Convert2StrBoolNum Convert2BoolNum and Conver2Num
   depending on usage

-- Changed need goal to reflect fact that strings must be quoted so direct
   goal can be string as long as its quoted  (got rid of value value form)

-- Added exception catcher to Need Check so that if goal is string and there
   there is a tolerance then it ignores the tolerance



--------------
20090516  = version 0.5.0

-- Put  precur and transacts and truncacts all in precur context
      precurs don't return anything and trans act only return something if
      valid tansition so if act does not return anything keep going so
      if doesn't matter mixed types of acts in one list.

-- added in order option (in front mid back) to task commands framer server logger
   This is useful when multiple houses to synchronize sensor state before
   controllers run in case of inter house communication.

-- Added 'me' as  goto target,
   me useful for new reenter context and forced re-entry

--------------
20090516

-- updated documentation and example scripts

--------------
20090515

-- Profiled fastest way to run for loops for iterating and for loop is
   faster than either list comprehension or generator expression
   for either actions or need actions (see speedIter.py  in sandbox)

-- Got rid of update method for LapseDeed folded it back into action()
   action() now calls updateLapse()

-- Change convention in framer.
   .elapsed is attribute instead of elapsedTime
   .elapsedShr is ref to share

   .repeat is attribute instead of repeatCount
   .repeatShr is ref to share

   The actors deeds use .elapsed as share reference
   framer is not action so its normal reference is to itself not the shares
   whereas actions primarily modify shares not self


-- framer.stamp is now the time of the last outline change used to compute
   .elapsed time

-- Now uses framer.stamp to replace startTime for starting elapsed time

-- logger and server uses task.stamp as time last ran successfully


-- replaced  if registry.Names.has_key(name)  with name in registry.Names

-- Got rid of framework command now only framer

-- got rid of "on need" form now only "if need"

-- Added Framer specific Frame Name Spaces
   This prevents problem of inadvertently having two framers run the same frame
   It also makes it easier to code auxiliaries since one can now reuse frame names
   in different framers.

-- Added framer.human and frame.headHuman so print out correct human active outline
   when a conditional auxiliary is active (truncated outline)--

-- Changed reenter to renter and reeexit to rexit contexts also changed
   reenacts to renacts and reexacts to rexacts and reenter() reexit() to renter() rexit()
   etc

-- Changed Registry.clear() .Clear() since subclasses
   might have alternate meaning for clear().
   Also since clear() is a class function it should be capitalized


--------------
20090514

-- Changed back scheduling of segueAuxes (see design notes)
   segueAuxes is its own context

-- Changed Auxact class to Truncact class

-- Added forced reentry (see design notes) so that can do counters of aux iterations
   all in one frame see mission counter4.tx also counter3.txt
   This actually implements what the reenter reexit done the day before was
   supposed todo but didn't see design notes

--------------
20090513

--  added support for [not] in need make it be at connective level
      [not] need inverts logic

   made a new Nact(Act) class that negates its actor() call
   if not need then replaces act with nact


-- Added reenter and reexit contexts for retrans = targeted unconditional reentry
   so can do counters that increment on entry not on recur.

   A targeted re-entry occurs when an already active frame (that is any frame
   in the active outline) is the explicit target of a successful transition.

   In a targeted re-entry,
      entry condition checks are not performed on the reentered frames
      standard enter actions and exit actions are not fired (as is the current policy)
      but reenter actions and reexit actions are fired

   renacts
   rexacts

   reenter actions are  performed on every targeted re-entry but not on initial entry
   avoids conflict and deciding  which one has priority (reenter vs enter)

   reexit actions are performed on every targeted re-exit  but not on final exit
   avoids conflict and deciding  which one has priority (reexit vs exit)


      enter (initial)

      trans
         exit
         enter

      retrans
         reexit
         reenter

      trans
         exit
         enter

      exit (final)


   But since rexit and reenter happen for the same frames at the same time
   there is no difference except that reexit is bottom up order and reenter
   is top down so reexit at higher level can override reexit at lower level
   Odd that reexit before reenter since no initial reenter and no final reexit
   So maybe should be reenter then reexit on retrans need use case to figure out.

   See Design Notes for more discussion



--------------
20090512

-- added as  scheduled (be inactive, active, slave) option to server, logger, task commands

-- Refactored tasker and house task lists
   house now has tasks, framers, slaves, auxes
   framers is all framers so can do resolve links

   tasks has all tasks that are taskable (active, inactive) including loggers servers framers
   slaves has all slave tasks including framers loggers servers
   auxes has all aux framers

   Put all .tasks from house into  ready list.
   when put active task in ready list set .desire to start
   when put inactive task in ready list set .desire to stop

   Got rid of stopped list

   advantage of this is that execution order does not change if a task is stopped
   and started

   Modified runners so that .desire works

-- Changed go script to support -d debug option

-- made done command only apply to auxiliary framers. also on done need

-- added flush interval to logger command
            default minimum is 1 second
   logger basic at 0.0 flush 60.0

-- Added try finally to logger generator to make sure log files get closed if exception

-- Changed log command parms to
   log name  [to path] [as (text, binary)] [on rule]
   default file name is log name and path is default
   default is text
   default is update
   rule: (once, never, always, update, change) automatically log on rule condition
   for manual forced logging use once or never as the auto condition and then tally
   for forced logging

-- Added checks in builder to prevent adding server, logger, log, or loggee of
   same name as existing one


-- Changed log files etc so house_date_time is directory holding files

   open(filename, 'a+') won't create a directory or path that does not already
      exist. will only create a file if the file does not already exit

   use os.makedirs(path, mode = 0777)




----------------
20090511

-- Added print command to print to console the rest of the arguments
      print Hello big buddy

-- tested conditional aux mission file test1.txt


--  Added conditional auxiliary as "interrupt" like mechanism where higher level framecan suspend
   lower level frame actions that then resume where they were once the high level
   suspension is over. If the condition is met the auxiliary becomes
   active and the active outline is truncated at the main frame of the conditional auxiliary.
   This effectively suspends the lower level frames (since outline truncated).
   Complication is if even higher level frame performs a transition what happens
   to truncated outline? Decided that it just becomes the new transition so not
   truncated anymore unless the higher level frame is also doing a conditional
   auxilary. So if want to stay within truncated outline then use
   yet another conditional auxiliary at a higher level.
   The purpose of this feature is to provide event driven exception handling or
   safety jackets that attempt to repair a situation and then allow the mission
   to resume. The conditional auxiliaries do the repair.
   Another issue is the conditional auxiliary run until done always or only run
   while the condition is still true? Or do we allow both?

   Implemented run until done.  run while A is the logical inverse
   of run until not A. Once done if the condition needing repair is not repaired it
   will try again. The drawback is the repair aux doesn't know apriori what the
   repair condition was that activated it so it can't be done
   as soon as the repair condition is satisfied.
   It could have a different done condition than the originating condition

   Syntax choices
   if/on needs go aux

   Like "go" one better as it matches more the truncated outline
   you are going to the aux and running it ans pausing the existing outline

   alternate is if needs run aux (not implemeted)

-----------------
20090507

-- Put back in framer.actives attribute and use it so can prepare for conditional
   auxiliaries

-- Moved transition logic into Transact call method so can have different types of
    transacts. Preparatory to conditional auxes

-- Got rid of Frame.marker and associated mark path methods not used anymore

-- HAF frame outline names for human display should use something else maybe
         Also have issue of showing complete path but also indicating which frame
         is the active frame
      Want different from Data Store Share path names which use dot '.' separateor

         group.group.share

      With framer
      framer<<superframe<superframe<activeframe>subframe>subframe

      human without framer
      superframe<superframe<activeframe>subframe>subframe

-- Added frame.traceHuman and .human to hold this human friengly string represention
   of frame hierarchy


-----------------
20090506

-- Made it so if and on can be used for either entry conditions or transitions
   figures out which by presence of goto

-- Added DynTransact (Transact) class. This has a new call method that
   gets the far frame by looking for an attribute of the framer given by the
   string for target    goto last  looks for framer.last getattr(frame.framer, 'last')
    Needed new type of transact object that has dynamic far link that when
   called looks up value in framer.last instead of resolving at parse build time.
   if make attribute reference dynamic (getattr) then could do goto last goto first
   any attribute of framer that pointed to frame
   After testing this decided it didn't work because the elapsed time and repeat
   gets reset when go back to last frame. So not really provide an 'Interrupt"
   like capability Deciced to do something else. So took out the last support.

-- got rid of .last support


-- Added to goto target where target can be 'last' this creates a DynTransact
   framer.last is the last frame before the current active frame. It is initialized and
   changed by framer.activate

   This is by default the last frame executed before the current frame
   This is set to the near frame at the end of a transition from near to far  before executing the entry actions
   in the far frame. This reference  maybe used as the target of a goto last

   This enables returning from a transition to handle an error condition
   like an interrupt. If the "interrupt handing takes more that one frame then the first frame has to run an aux
   otherwise each subsequent frame with change last and there will be no way to return to the very first. without some
   other mechanism.
   (already did framer.last attribute and its gets set in .activate)


------------
20090502

-- Changed preacts to beacts

-- added preacts as prior transition actions to frame

--  eval preacts in framer just prior to transition trans

-- add precur command context to builder and add deed to this context when overridden


-- got rid of context command

-- Refactored Framer transition made trans for a frame something that is done from Frame not framer
   so trans in Framer just iterates through list
   -- Consider Refactor trans method of framer so can be encapsulated as Frame method
   Idea is to refactor framer so that all Framer methods iterate over outline of frames
   but work is done by associated Frame method (checkEnter, enter recur exit trans etc)

   Problems are:
      trans method which calls Framer methods.
      implicit entry exit recur actions. These are stored in Framer
   Added framer link to frame help overcome these problems.

   Framer attributes .entries and .exits don't need to be globals but
   can be parameters passed into associated methods that use them.
   only need .actives
   runner method no longer accesses .entries .exits or .actives all
   handled with method calls.

   Replaced self.actives with self.active.outline


-- replaced trans methods of framer and frame with segue

-- Replaced start command for framer with first command and
   replaced start option in framer command with first option

-- temporary activation no longer done in checkStart

-- Added .last attribute of Framer to save last active frame before current active

-- Added deactivate method to framer

-- Got rid of reactivate method of framer

-----------------
20090429

   interfacing.remusformatter.checksum did not pring leading zeros
       changed %2X to %02X to fix

-----------
20090220

Fixed problem where if exception occurred in server recon remus that the socket
   would not be closed and on next run the socket would be "in use"
   added try finally to runner method of generator so finally would close
   the socket in the event of an exception causing the generator to close.



---------------
20081112

-- added warnings at parse time if share or field does not exist
   when created dynically for put, inc, copy, set, if, on

-- new addressing syntax in init put inc copy set if on commands

-- init command replaces share command

-- except for special goals and needs all basic goals and needs dynamic

-- added boolean need

-- added logic in init put inc copy set if on commands
   to enforce that if data field is value then only one field is allowed
   this will make it hard to inadvertently have a share with a value field and non
   value fields



-----------
20081110

-- fixed store code to:
   strip leading '.' on paths when adding
   raise exception for  blank groups a..b
   make sure that Store.create(path) .add only allows one to create shares without
   clobbering existing shares or groups when path collisions or overlap
   example:

   path1  a.b.c.d   d is share
   path2  a.b.c.d.e e is share

   *creating path2  if path1 already exists will clobber share d of path1
      so while descending path check that intermediate level is not a preexisting
      share (since share acts like dictionary it will not cause error)

   *creating path1 if path2 already exists will orphan share e of path2
      so while descending path check that tail is not a preexisting group
         group (part of preexisting path to lower level)

-- added copy command and IndirectPoke implements new format for
   moving data between shares and HAFScript syntax



------------
20081024

-- completely redid need syntax and need parsing
   need = (state comparison goal) c

   added relative addressing
   can now be framer  or frame or house relative

   redefined absolute addressing for state and goal
   ie indirect goals allowed not just direct

   added boolean need (no comparison or goal implicit comparison to True
   if state
   on state

   changed where goals and state stored
   goal.name
   state.name
   framer.framername.state.name
   framer.framername.goal.name
   frame.framename.state.name
   frame.framename.goal.name

   state is now thename for need not pose
   changed behaviors to use state.xxx instead of pose.xxx

-- added dynamic goal creation if goal by name does not exist make new goal with name
   what about value vs data goals?
   change parse logic if one one more token after to connective then value goal
   if two or more then data goal

   Change syntax
      make consistent so know if value or data goal based on if there is a field named value
      already?


-- add dynamic need creation if need by name does not exit make new need with name
   actially now all need specific info is in need parms so only need three basic types
   boolean need, direct need, and indirect need, also have simple needs for elapsed and repeat
   and special needs for done status always


----------
20081018

-- added context commands without context word
      native enter recur exit

-- changed syntax of framework command
   added be scheduled option   aux and slaves must be explicitly defined
   added start frame option
   start frame is first lexical frame if not otherwise declared

-- added global ScheduleValues ScheduleNames and global constants
   INACTIVE, ACTIVE, AUX, SLAVE

-- added  task.schedule and removed .active .aux and .slave fixed up related
   code.


----------
20081017
-- share (added from) so can initialize a given share from the value or data
         in another share

   share path as field value field value
   share path as value value
   share path as value
   share path from path
   (potentially ambiguous could be single or multiple and could change later)
   so understand that only initializing share to preexisting share

   share path from path value
   share path from path field [field]

-- fixed bug in transition logic Framer staticmethod Uncommon would return as uncommon
    the last frame as uncommon exit and entry if the outlines were equal fixed this

-- changed check enter logic so that entry fails if entries empty ie transition
   from same outline to same outline. This would occur any time upper frame had
   transition to a lower frame  in outline but active frame was already the lower frame
   Implications for mplicit entry actions

-- added framer link to frame so can refactor execution order code. Also makes
   it so can't inadvertently assign frame to more than one framer at build time.

-- fixed problem with arbiter definition where truth was in data not share attribute

-- added  framer command same as framework




-------------
20080605
-- change goal duration to goal elapsed so consistent goal and need same name

--  added support for counter per framer outline like elapsed so can count
   times framer has run in a given state and then can do trans on count like
   on elapsed  This was done using the repeat need and the framer.repeatCount
   also for logging see pose.repeat.framer.value




------------
20080602
   -- added Flush time for logger default  60 seconds to flush logs

-------------
20080527

--  set convention scenario.onset for starting position north east relative to origin.
   fscenario.origin lat lon for origin of flat earth coordinates

   changed uuv and usv simulators to use scenario.onset instead of scenario.origin
   origin is now lat lon of origin of coordinate system whereas onset is initial
   position of the vehicle north east relative to origin.


-- Got rid of the first field mapping for value. In other words
   mapping the first field created to value seems like a stupid idea since
   never use it and even if did can't think of good use case where you would want
   to. It was merely to prevent crashing if inadvertently used value when there
   was none. Only use case would be if shares had only one field in data but
   wanted that field to be something other than value like pose.heading.heading
   but never did it that way always used value.
   in hindsight may want to detect such inadvertant use as error.
   still have share.value as property to get field named value if exits
   Did this because as implemented, updating a share with share.update(value = xxx)
   can mess up the way value works
   since update() doesn't check to see if there is already a field in the data that
   may not be named 'value'
   to ensure that update(value = ) gets mapped to the first field
   instead it will create another field named value. So instead of adding
   yet more checks in change and create just got rid of it

-- Did a lot of HAFScript syntax refinements. See the haftscript manual
-- added from syntax for needs and goals to allow comparing need from explicit
   share and setting goal from explicit share



----------------
20080429
   made it so optional parameters on commands ; server, framework, and logger have
   connectives

   need to check all commands so that optional parameters have connectives
   then order options appear doesn't matter

----------------
20080331

Changed algorithm for marking outline exit enty. Since execution speed is more
   of a bottleneck than memory we can reduce execution speed by storing outline
   as list for each frame and then get differences between outline lists
   get exit and entry list on a transition.
   Will need to regenerate outline every time a new frame  is
   added or link made if update outline at run time.


Simplified runner generator allowed by new execution ordering

.done is not set to False on framer enter not checkStart


------------------
20080327

supported timeouts:
   hafscript
      timeout value

   add implict transact
      on elapsed >= timeout goto next

   what if want to go to someplace else on timeout? then use duration not timeout





fixed bug in building.Convert() where integer strings were getting converted
to base 8 or base 16 (need to check base 10 first)


Add support for next frame
   Explicit
      next frameName
      next
   Implicit lexical next

   transitions

   on xxx goto next

   need to make next frame link and resolve it
   Either with explicit
      next frame
      or implicit next is next lexical frame
      so when creating a new frame before reassign current frame
         check of next of current is empty and if so then put in new as next.

added context to mission script since no act is naturally an exit act except give
   hafscript
   context entry
   context recur
   context exit
   context native

   currentContext reset to native with new frame
   some acts can have different context besides native
   some only allow native and ignore current context



added hooks to support slave framers.
   .slaves list in house
   .auxes list in house
   .slave flag in framer

tell now restricted to slave framers


Made it so ask not work on aux or slave framers.


initializing data shares. removed cases where created value in shared then updated it.
But update does a create if not already exist so
only need to do update when forcing and create when not forcing the value.


instead of enneeds use preacts  for pre-entry actions frame
   replace .enneeds and .addEnneed with .preacts .addPreact


Changed tasker
   no more waiting list. all actives and tasks (loggers etc) go into ready list
   regardless of period. This way order preserved for different periods no apparent
   speed hit may even be faster
   Task lists deques now have tuples (task, retime, period) instead of just tasks
      Tasker responsible for updating retime not task. Removed .retime attribute
      from tasks

   Did speed tests and confirmed that tuple packing and unpacking is faster than
   object attribute access.

------------------
20080326

Changed Framer and Frame
   Fixed frame and aux framer execution order

   -- fix exec order again. start cycle with trans so trans/enter/recur same cycle

   start framer
   enter initial outline
   recur
   time step

   if trans
      exit
      enter
   recur
   time step

   if trans
      exit
      enter
   recur
   timestep

   Frames call trans which can call enter on auxes before lower level frames
   so that lower level frames trans -> enter
   can still override anything a higher level aux frame does



-----------------
20071115

added support for "ask" task control for loggers
added support for need done for loggers
added tasker
added real time to tasker
testing module now functional
added house.inactives

------------------------------------------
20071102


1)  Done:
   Revised Share and Data objects.
   Revised odict so can be pickled
      old Data can't be copied since its a dict without iteritems
      old Data can't be pickled since it uses slots without __getstate__
      oldalso anywhere use odict() can't be pickled since no __getstate__.

2) last no longer in share. each log makes own last copy for ifchanged


3) time creep fixed.
** basically this change means logger doesn't see the last value of elapsed on  a state
change since it gets reset to zero on state entry before logger gets to run. Only way to
see it is to log it within state machine as recurring action do log deed.

fixed by having entry run on same time as exit but recur waits till next cycle.
This prevents infinite chaining of transitions and since most controllers run in different
framer there is no gap when setpoint changes. If controller runs in same framer then
last control action will apply. Since transitions are checked after all other recurring actions
all controllers in that frame will have run. This however leaves the case where a controller
runs in a lower frame. In this case the control action will not be updated on that cycle and
will be stale by one cycle.  A way to fix this is have all recur actions in all frames in the outline
run before any of the transitions are checked! then transitions become their own stage.
Did this

next frame entry executes on same time step as transition
check transition
check entry
exit
enter
time step
recur
   recur actions top to bottom
   trans checks top to bottom



