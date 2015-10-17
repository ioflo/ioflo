"""
aiding.py

"""
from __future__ import division

## Backwards compatibility for now
## In future users should import from ioflo.aid.aiding not here
from ..aid.aiding import  reverseCamel,  \
     nameToPath, repack, just, isPath, isIdentifier, isIdentPub, \
     packByte, unpackByte,  \
     hexize, unhexize, Denary2BinaryStr, Dec2BinStr, PrintHex, PrintDecimal, CRC16, \
     CRC64, ocfn, Load, Dump, DumpJson, LoadJson

# In future users should import from ioflo.aid.timing not here
from ..aid.timing import Timer, MonoTimer, StoreTimer, totalSeconds

# In future users should import from ioflo.aid.metaing not here
from ..aid.metaing import metaclassify, NonStringIterable, NonStringSequence, nonStringIterable, \
     nonStringSequence

# In future users should import from ioflo.aid.nonblocking not here
from ..aid.nonblocking import SerialNb, ConsoleNb, SocketUdpNb, SocketUxdNb, WinMailslotNb

# In future users should import from ioflo.aid.navigating not here
from ..aid.navigating import Sign, Delta, Wrap2, \
    MoveByHSD, MoveToHSD, RotateFSToNE, RotateNEToFS, AlongCrossTrack, CrabSpeed, \
    CrossProduct3D, DotProduct, PerpProduct2D, DistancePointToTrack2D, SpheroidLLLLToDNDE,  \
    SphereLLLLToDNDE, SphereLLByDNDEToLL, SphereLLbyRBtoLL, SphereLLLLToRB, \
    RBToDNDE, DNDEToRB, DegMinToFracDeg, FracDegToDegMin, FracDegToHuman,  \
    HumanLatToFracDeg, HumanLonToFracDeg, HumanToFracDeg, HumanLLToFracDeg, \
    Midpoint, Endpoint

# In future users should import from ioflo.aid.blending not here
from ..aid.blending import Blend0, Blend1, Blend2, Blend3
