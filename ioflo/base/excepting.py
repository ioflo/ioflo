"""excepting.py exception classes

"""
#print("module {0}".format(__name__))


import random

from ..aid.sixing import *


class ParameterError(Exception):
    """Used to indicate a function parameter is either of the wrong type or value
       usage:
       raise excepting.ParameterError("Expected Frame instance", "active", active)
    """
    def __init__(self, message = None, name = None, value = None):
        self.message = message #description of error
        self.name = name #parameter name
        self.value = value #parameter value

        self.args = (message, name, value)


    def __str__(self):
        return ("%s. Name = %s, Type = %s, Value = %s.\n" %\
                (self.message, self.name, str(type(self.value)), repr(self.value)) )

class ParseError(Exception):
    """Used to indicate a mission script statement has a parsing error

       usage:
       msg = "ParseError: Not enough tokens in command '%s'" % (kind)
       raise excepting.ParseError(msg, tokens, index)
    """
    def __init__(self, message = None, tokens = None, index = None):
        self.message = message #description of error
        self.tokens = tokens #token value
        self.index = index #action name

        self.args = (message, tokens, index)


    def __str__(self):
        return ("%s. tokens = %s, index = %s.\n" %\
                (self.message, repr(self.tokens), self.index) )

class ParseWarning(Exception):
    """Used to indicate a mission script statement has a parsing warning

       usage:
       msg = "ParseWarning: Not enough tokens in command '%s'" % (kind)
       raise excepting.ParseWarning(msg, index, tokens)
    """
    def __init__(self, message = None, tokens = None, index = None):
        self.message = message #description of error
        self.tokens = tokens #token value
        self.index = index #action name

        self.args = (message, tokens, index)


    def __str__(self):
        return ("%s. tokens = %s  index = %s.\n" %\
                (self.message, repr(self.tokens), self.index) )


class ResolveError(Exception):
    """Used to indicate a mission script statement link or reference in an
       component (framer, frame, action etc) is in error

       usage:
       msg = "ResolveError: Bad frame link '%s' for action '%s'" % (link, action.name)
       raise excepting.ResolveError(msg, link, action)
    """
    def __init__(self, message=None, name=None, value=None, human='', count=None):
        self.message = message  # description of error
        self.name = name  # link name or description
        self.value = value  # actor, framer, frame etc
        self.human = human  # human readable Floscript declaration
        self.count = count  # count of line for Floscript declaration

        self.args = (message, name, value, human, count)


    def __str__(self):
        return ("%s. Name = %s, Value = %s. at line %s\n    %s\n" %\
                (self.message, self.name, repr(self.value), self.count, self.human, ) )

class CloneError(Exception):
    """Used to indicate cloning error

       usage:
       msg = "CloneError: Framer '%s' already exists" % (name)
       raise excepting.CloneError(msg)
    """
    def __init__(self, message = None):
        self.message = message #description of error

        self.args = (message)


    def __str__(self):
        return ("%s.\n" % (self.message, ))

class RegisterError(Exception):
    """Used to indicate error in Registry

       usage:
       msg = "Entry '{0}' already exists in registry".format(rname)
       raise excepting.RegisterError(msg)
    """
    def __init__(self, message = None):
        self.message = message #description of error
        self.args = (message)

    def __str__(self):
        return ("{0}: {1}.\n".format(self.__class__.__name__, self.message))

class TimerRetroError(Exception):
    """Used to indicate timer base has retrograded while timer is running

       usage:

       raise excepting.TimerRetrogradeError(msg)
    """
    def __init__(self, message = None):
        self.message = message #description of error
        self.args = (message)

    def __str__(self):
        return ("{0}: {1}.\n".format(self.__class__.__name__, self.message))

def Test():
    """Module self test



    """

    raise ParameterError("Expected something else", 'whatever', 1)


if __name__ == "__main__":
    Test()
