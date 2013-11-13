"""registering.py support functions and classes

"""
#print "module %s" % __name__

import random


from .globaling import *

from . import excepting

from .consoling import getConsole
console = getConsole()

class Registry(object):
    """Class that ensures every instance has a unique name
       uses class variable Counter and  Names dictionary
    """
    __slots__ = ('name')
    
    #for base class to have distinct name space shadow these by defining in sub class def
    Counter = 0  
    Names = {}

    def __init__(self, name = '', preface = 'Registry', **kw):
        """Initializer method for instance.

           instance attributes
           .name = unique name for instance

        """
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


class StoriedRegistry(Registry):
    """Adds store attribute to Registry instances
    """
    __slots__ = ('store')
    
    def __init__(self, store=None, **kw):
        """Initializer method for instance.
           Inherited instance attributes:
           .name
           
           New instance attributes
           .store = reference to shared data store

        """
        super(StoriedRegistry, self).__init__(**kw)
        self.changeStore(store=store)
        
    def changeStore(self, store=None):
        """Replace .store """
        from . import storing
        if store is not None: 
            if  not isinstance(store, storing.Store):
                raise ValueError("Not store %s" % store)
        self.store = store        

def Test():
    """Module self test



    """
    
    x = Registry()
    print x.name
    y = Registry()
    print y.name

    name = "Hello"
    if Registry.VerifyName(name):
        z = Registry(name= name)
    print Registry.Names
    print Registry.VerifyName(name)



if __name__ == "__main__":
    Test()

