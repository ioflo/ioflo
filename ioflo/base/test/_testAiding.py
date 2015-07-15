import sys
if sys.version > '3':
    xrange = range

import ioflo
from ioflo.base import aiding

from ioflo.base.consoling import getConsole
console = getConsole()



def TestBlend0(u = .25, s = .75, steps = 10):
    """Test the Blend0 function

    """
    u = abs(u)
    s = abs(s)
    steps = abs(steps)
    span = u + s
    ss = span / steps
    for x in xrange(-(steps + 1), steps + 2, 1):
        d = x * ss
        b = Blend0(d,u,s)
        print(d, b)



def Test():
    """Module self test



    """
    pass

if __name__ == "__main__":
    #Test()
    #TestSocketUxdNB()
    TestNonStringIterableSequence()
