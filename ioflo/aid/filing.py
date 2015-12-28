"""
filing.py file and serialization utility functions
"""
from __future__ import absolute_import, division, print_function

import sys
import os
import errno

try:
    import simplejson as json
except ImportError:
    import json

# Import ioflo libs
from .sixing import *
from .odicting import odict
from .consoling import getConsole

console = getConsole()


def ocfn(filename, openMode='r+', binary=False):
    """Atomically open or create file from filename.

       If file already exists, Then open file using openMode
       Else create file using write update mode If not binary Else
           write update binary mode
       Returns file object

       If binary Then If new file open with write update binary mode
    """
    try:
        newfd = os.open(filename, os.O_EXCL | os.O_CREAT | os.O_RDWR, 436) # 436 == octal 0664
        if not binary:
            newfile = os.fdopen(newfd,"w+")
        else:
            newfile = os.fdopen(newfd,"w+b")
    except OSError as ex:
        if ex.errno == errno.EEXIST:
            newfile = open(filename, openMode)
        else:
            raise
    return newfile

def dump(data, filepath):
    '''
    Write data as as type self.ext to filepath. json or .msgpack
    '''
    if ' ' in filepath:
        raise IOError("Invalid filepath '{0}' "
                                "contains space".format(filepath))

    root, ext = os.path.splitext(filepath)
    if ext == '.json':
        with ocfn(filepath, "w+") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
    elif ext == '.msgpack':
        if not msgpack:
            raise IOError("Invalid filepath ext '{0}' "
                        "needs msgpack installed".format(filepath))
        with ocfn(filepath, "w+b", binary=True) as f:
            msgpack.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
    else:
        raise IOError("Invalid filepath ext '{0}' "
                    "not '.json' or '.msgpack'".format(filepath))

def load(filepath):
    '''
    Return data read from filepath as dict
    file may be either json or msgpack given by extension .json or .msgpack
    Otherwise return None
    '''
    try:
        root, ext = os.path.splitext(filepath)
        if ext == '.json':
            with ocfn(filepath, "r") as f:
                it = json.load(f, object_pairs_hook=odict)
        elif ext == '.msgpack':
            if not msgpack:
                raise IOError("Invalid filepath ext '{0}' "
                            "needs msgpack installed".format(filepath))
            with ocfn(filepath, "rb", binary=True) as f:
                it = msgpack.load(f, object_pairs_hook=odict)
        else:
            it = None
    except EOFError:
        return None
    except ValueError:
        return None
    return it

def loadPickle(file=""):
    """
    Loads pickled object from file, returns object
    """
    if not file:
        raise ParameterError("No file to load from: {0}".format(file))

    with open(file,"r+") as f:
        p = pickle.Unpickler(f)
        it = p.load()

    return it

def dumpPickle(it=None, file=""):
    """
    Pickles it object to file
    """
    if not it:
        raise ParameterError("No object to dump: {0}".format(str(it)))

    if not file:
        raise ParameterError("No file to dump to: {0}".format(file))

    with open(file, "w+") as f:
        p = pickle.Pickler(f)
        p.dump(it)

def loadJson(filename=""):
    """ Loads json object from filename, returns unjsoned object"""
    if not filename:
        raise ParameterError("Empty filename to load.")

    with ocfn(filename) as f:
        try:
            it = json.load(f, object_pairs_hook=odict())
        except EOFError:
            return None
        except ValueError:
            return None
        return it

def dumpJson(it=None, filename="", indent=2):
    """Jsonifys it and dumps it to filename"""
    if not it:
        raise ValueError("No object to Dump: {0}".format(it))

    if not filename:
        raise ValueError("No file to Dump to: {0}".format(filename))

    with ocfn(filename, "w+") as f:
        json.dump(it, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
