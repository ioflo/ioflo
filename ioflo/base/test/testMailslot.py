import sys
if sys.version > '3':
    xrange = range

import ioflo
from ioflo.base import aiding

if sys.platform == 'win32':
    import win32file

from ioflo.base.consoling import getConsole
console = getConsole()


def TestWinmailslotNB():
    """Class WinMailslotNB self test """
    console.reinit(verbosity=console.Wordage.verbose)
    try:
        print("Testing WinmailslotNb")
        serverA = aiding.WinmailslotNb(ha = '\\\\.\\mailslot\\uxdA', umask=0o077)
        serverA.reopen()
        serverB = aiding.WinmailslotNb(ha = '\\\\.\\mailslot\\uxdB', umask=0o077)
        serverB.reopen()
        serverC = aiding.WinmailslotNb(ha = '\\\\.\\mailslot\\uxdC', umask=0o077)
        serverC.reopen()

        serverA.send("A sends to B",serverB.ha)
        print(serverB.receive())
        serverA.send("A sends to C",serverC.ha)
        print(serverC.receive())
        serverA.send("A sends to A",serverA.ha)
        print(serverA.receive())
        serverB.send("B sends to A",serverA.ha)
        print(serverA.receive())
        serverC.send("C sends to A",serverA.ha)
        print(serverA.receive())
        serverB.send("B sends to B",serverB.ha)
        print(serverB.receive())
        serverC.send("C sends to C",serverC.ha)
        print(serverC.receive())

        serverA.send("A sends to B again",serverB.ha)
        print(serverB.receive())
        serverA.send("A sends to C again",serverC.ha)
        print(serverC.receive())
        serverA.send("A sends to A again",serverA.ha)
        print(serverA.receive())
        serverB.send("B sends to A again",serverA.ha)
        print(serverA.receive())
        serverC.send("C sends to A again",serverA.ha)
        print(serverA.receive())
        serverB.send("B sends to B again",serverB.ha)
        print(serverB.receive())
        serverC.send("C sends to C again",serverC.ha)
        print(serverC.receive())

        print(serverA.receive())
        print(serverB.receive())
        print(serverC.receive())


    finally:
        serverA.close()
        serverB.close()
        serverC.close()

def Test():
    """Module self test



    """
    pass

if __name__ == "__main__" and sys.platform == 'win32':
    #Test()
    TestWinmailslotNB()
