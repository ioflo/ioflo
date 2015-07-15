"""
aiding.py

"""
#print("module {0}".format(__name__))

from __future__ import division

# Backwards compatibility for now
# In future users should import from ioflo.aid.aiding not here
from ..aid.aiding import  reverseCamel,  \
     nameToPath, Repack, just, IsPath, IsIdentifier, IsIdentPub, Sign, Delta, Wrap2, \
     MoveByHSD, MoveToHSD, RotateFSToNE, RotateNEToFS, AlongCrossTrack, CrabSpeed, \
     CrossProduct3D, DotProduct, PerpProduct2D, DistancePointToTrack2D, SpheroidLLLLToDNDE,  \
     SphereLLLLToDNDE, SphereLLByDNDEToLL, SphereLLbyRBtoLL, SphereLLLLToRB, \
     RBToDNDE, DNDEToRB, DegMinToFracDeg, FracDegToDegMin, FracDegToHuman,  \
     HumanLatToFracDeg, HumanLonToFracDeg, HumanToFracDeg, HumanLLToFracDeg, \
     Midpoint, Endpoint, Blend0, Blend1, Blend2, Blend3, packByte, unpackByte,  \
     Hexize, Binize, Denary2BinaryStr, Dec2BinStr, PrintHex, PrintDecimal, CRC16, \
     CRC64, ocfn, Load, Dump, DumpJson, LoadJson

# In future users should import from ioflo.aid.timing not here
from ..aid.timing import Timer, MonoTimer, StoreTimer, totalSeconds

# In future users should import from ioflo.aid.metaing not here
from ..aid.metaing import metaclassify, NonStringIterable, NonStringSequence, nonStringIterable, \
     nonStringSequence

# In future users should import from ioflo.aid.nonblocking not here
from .nonblocking import SerialNb, ConsoleNb, SocketUdpNb, SocketUxdNb, WinMailslotNb

