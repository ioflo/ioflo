"""registering.py support functions and classes

"""
print "Module %s" % __name__

import random

#******haf modules******
from .globaling import *

from . import excepting

from .consoling import getConsole
console = getConsole()

#debugging support
#debug = True
debug = False

#Class definitions

class Corpus(object):
    """ Catchall class to workaround python 2.6 change to root class object behavior
       that does not allow __init__ args
    """
    def __init__(self, **kw):
        """ Initializer """
        super(Corpus, self).__init__()

#Class that ensures every instance has a unique name and id 
class Registry(Corpus):
    """Class that ensures every instance has a unique name
       uses class variable Counter and  Names dictionary
    """
    #for base class to have distinct name space shadow these by defining in sub class def
    Counter = 0  
    Names = {}

    def __init__(self, name = '', preface = 'Registry', **kw):
        """Initializer method for instance.

           instance attributes
           .name = unique name for instance

        """
        super(Registry, self).__init__(name = name, preface = preface, **kw)
        #super(Registry, self).__init__()

        self.__class__.Counter += 1 #increment class Counter variable

        if not isinstance(name,str): #name must be string
            raise excepting.ParameterError("Expected str instance", "name", name)

        if not name: #if name empty then provide name
            name = str(preface) + str(self.__class__.Counter)
            while (name in self.__class__.Names):
                name += chr(ord('a') + random.randint(0,25)) #add a random letter
        elif (name in self.__class__.Names): #if provided name must be unique
            raise excepting.ParameterError("Instance name attribute not unique", "name", name)

        self.name = name
        self.__class__.Names[self.name] = self #add instance to Names dict indexed by name



    @classmethod
    def Clear(cls):
        """clears (empties) registry of Names and resets Counter to 0

        """
        cls.Names = {}
        cls.Counter = 0

    @classmethod
    def VerifyName(cls, name = ''):
        """verifies that name would be unique non empty string for instance name

           return False if empty or if already in Names , True otherwise
        """
        if not isinstance(name,str): #name must be string
            return False

        if (not name) or (name in cls.Names): #name must be unique and not empty
            return False

        return True

    @classmethod
    def Retrieve(cls, name = ''):
        """Retrieves object in registry with name 

           return object with name or  False if no object by name
        """
        return cls.Names.get(name, None)


def Test():
    """Module self test



    """
    global debug

    oldDebug = debug
    debug = True #turn on debug during tes

    x = Registry()
    print x.name
    y = Registry()
    print y.name

    name = "Hello"
    if Registry.VerifyName(name):
        z = Registry(name= name)
    print Registry.Names
    print Registry.VerifyName(name)


    debug = oldDebug #restore debug value


if __name__ == "__main__":
    Test()

