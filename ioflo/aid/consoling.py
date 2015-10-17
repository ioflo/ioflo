"""consoling.py classes for printing out to the console

"""
import sys
import os
import errno
from collections import namedtuple

# named tuple class of verbosity levels
VERBIAGE_NAMES = ['mute', 'terse', 'concise', 'verbose', 'profuse' ]
Verbiage = namedtuple('Verbiage', VERBIAGE_NAMES)
verbiageNames = Verbiage._make(VERBIAGE_NAMES) #values same as keys UI friendly

Consoles = {} #console instances created

class Console(object):
    """Manages output console messages typically stdout with various levels
       of verbosity. Lightweight implementation that does not require threading.
       Optional flushy mode where each write is flushed

       Verbosity Levels

       mute = 0  means do not write
       terse = 1
       concise = 2
       verbose = 3
       profuse = 4

       If the write verbosity is less than or equal the allowed verbosity level
       THEN write

    """
    # Class attribute instance of verbosity levels
    Wordage = Verbiage(mute=0, terse=1, concise=2, verbose=3, profuse=4)

    _Name = 'console'
    _Path =  ''
    _Verbosity = Wordage.concise #current class wide verbosity level
    _Flushy = False

    def __init__(self, name="console", verbosity=None, flushy=None, path=""):
        """Initialize _file object from path, verbosity level, and flushy mode

        """
        self._name = name or self._Name
        self._verbosity = int(verbosity) if verbosity is not None else self._Verbosity
        self._flushy = flushy if flushy is not None else self._Flushy
        self._path = path or self._Path
        self._file = None

        self.reopen()

    def reinit(self, verbosity=None, flushy=None, path=None):
        """ Selectively reinit non None arguments"""

        if verbosity is not None:
            self._verbosity = int(verbosity)

        if flushy is not None:
            self._flushy = flushy

        if path is not None:
            self._path = path
            self.reopen()

    def reopen(self):
        """IF opened close THEN open self._file from self.path
           Otherwise use sys.stdout
        """
        self.close()

        if self._path:
            try:
                self._path = os.path.abspath(os.path.expanduser(self._path))
                dirpath = os.path.dirname(self._path)
                if not os.path.exists(dirpath):
                    try:
                        os.makedirs(dirpath)
                    except OSError as ex:
                        msg = ("Error creating console file directory {0}. "
                               "{1}\n".format(dirpath, ex))
                        sys.stderr.write(msg)
                        return False
                self._file = Console.ocfn(self._path, 'a+') # open or create file
                self._file.seek(0, os.SEEK_END) # append but not forced
            except IOError as ex:
                msg = "Error opening console file {0}. {1}\n".format(self._path, ex)
                sys.stderr.write(msg)
                return False
        else:
            self._file = sys.stdout

        return True

    def close(self):
        """Close self._file if open and not if not sys.stdout"""
        if self._file and not self._file.closed:
            if self._file.name not  in ['<stdout>', '<stderr>']: # don't close sys.stdout
                try:
                    self._file.close()
                except (AttributeError):
                    pass

        self._file = None

    def flush(self):
        """ flush self._file"""
        try:
            self._file.flush()
            try:
                os.fsync(self._file.fileno())
            except (AttributeError, ValueError,  OSError) as ex:
                pass
        except (AttributeError, ValueError) as  ex:
            pass

    def write(self, msg, verbosity=None):
        """Write to self._file
           If verbosity is None Or verbosity is less than or equal to self.verbosity
        """
        if verbosity is None or verbosity <= self._verbosity:
            self._file.write(msg)
            if self._flushy:
                self.flush()

    def terse(self, msg):
        """Write at terse verbosity level
        """
        self.write(msg, verbosity=self.Wordage.terse)

    def concise(self, msg):
        """Write at concise verbosity level
        """
        self.write(msg, verbosity=self.Wordage.concise)

    def verbose(self, msg):
        """Write at verbose verbosity level
        """
        self.write(msg, verbosity=self.Wordage.verbose)

    def profuse(self, msg):
        """Write at profuse verbosity level
        """
        self.write(msg, verbosity=self.Wordage.profuse)

    @staticmethod
    def ocfn(filename, openMode = 'r+'):
        """Atomically open or create file from filename.

           If file already exists, Then open file using openMode
           Else create file using write update mode
           Returns file object
        """
        try:
            newfd = os.open(filename, os.O_EXCL | os.O_CREAT | os.O_RDWR, 436) # 436 == octal 0664
            newfile = os.fdopen(newfd, openMode)
        except OSError as ex:
            if ex.errno == errno.EEXIST:
                newfile = open(filename, openMode)
            else:
                raise
        return newfile


def getConsole(name='console', **kw):
    """ Retrieves or creates console instance of name name. Reinits any arguments
        that are not None

        See Console.__init__ args for valid keyword args kw
    """
    console = Consoles.get(name)
    if not console:
        console = Console(name=name, **kw)
        Consoles[console._name] = console
        return console

    console.reinit(**kw)
    return console

getConsole('console') #create the default console named 'console'


def Test():
    """Module self test """
    console = Console(verbosity=Console.Wordage.concise)
    console.flush()
    console.close()
    console.reopen()
    console.write("Howdy\n")
    console.write("Pardner\n", verbosity=console.Wordage.concise)
    console.write("Goodeby\n", verbosity=console.Wordage.verbose)
    console.terse("In a while cocodile.\n")
    console.concise('Ok bluejay\n')
    console.verbose('See ya later alligator.\n')
    console.profuse('Not to soon baboon.\n')
    console.close()

    console = Console( verbosity=Console.Wordage.verbose,  path="/tmp/consoletesterfile")
    console.flush()
    console.close()
    console.reopen()
    console.write("Look me up.\n")
    console.close()

    console = getConsole( verbosity=Console.Wordage.concise)
    console.flush()
    console.close()
    console.reopen()
    console.write("Howdy\n")
    console.write("Pardner\n", verbosity=console.Wordage.concise)
    console.write("Goodeby\n", verbosity=console.Wordage.verbose)
    console.terse("In a while cocodile.\n")
    console.concise('Ok bluejay\n')
    console.verbose('See ya later alligator.\n')
    console.profuse('Not to soon baboon.\n')
    console.terse("{0}".format(Consoles))
    console.close()

    console = getConsole('ioflo', verbosity=Console.Wordage.concise)
    console.flush()
    console.close()
    console.reopen()
    console.write("Howdy\n")
    console.write("Pardner\n", verbosity=console.Wordage.concise)
    console.write("Goodeby\n", verbosity=console.Wordage.verbose)
    console.terse("In a while cocodile.\n")
    console.concise('Ok bluejay\n')
    console.verbose('See ya later alligator.\n')
    console.profuse('Not to soon baboon.\n')
    console.terse("{0}".format(Consoles))
    console.close()


if __name__ == "__main__":
    Test()
