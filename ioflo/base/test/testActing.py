import ioflo
from ioflo.base import registering
from ioflo.base import storing
from ioflo.base import framing
from ioflo.base import acting
from ioflo.base import deeding


def test():
    """Module Common self test

    """

    store = storing.Store()

    actor = acting.Actor(store = store)
    actor()

    #depthNeed = DepthNeed(name = 'checkDepth', store = store)
    #depthNeed(depth = 1.0)

    #depthGoal = DepthGoal(name = 'setDepth', store = store)
    #depthGoal(depth = 2.0)

    #depthDeed = DepthDeed(name = 'doDepth', store = store)
    #depthDeed(depth = 3.0)

    #depthTrait = DepthTrait(name = 'useDepth', store = store)
    #depthTrait(depth = 4.0)

    #depthSpec = DepthSpec(name = 'optDepth', store = store)
    #depthSpec(depth = 5.0)

    fr = framing.Framer(store = store)
    f = framing.Frame(store = store)
    fr.startFrame = f

    #startFiat = StartFiat(name = 'tellStart', store = store)
    #startFiat(framer = fr)

    #startWant = StartWant(name = 'askStart', store = store)
    #startWant(framer = fr)

    #poke = Poke(name = 'put', store = store)
    #poke(name = 'autopilot.depth', value = dict(depth = 5))

def testActorify():

    @acting.actorify("beardBlue")
    def testy(self, x=1, z=2):
        """ Testy is a function"""
        print self
        print x
        print z

    actor, inits, ioinits, parms = acting.Actor.__fetch__("beardBlue")
    print actor.Registry
    print actor._Parametric
    print actor.Inits
    print actor.Ioinits
    print actor.Parms
    print inits
    print ioinits
    print parms

    actor = actor()
    actor()
    print actor.action
    print actor.action.__name__
    print actor.action.__doc__

def testDeedify():

    @deeding.deedify("blackSmith")
    def hammer(self, x=1, z=2):
        """ hammer is a function"""
        print self
        print x
        print z

    actor, inits, ioinits, parms = deeding.Deed.__fetch__("blackSmith")
    print actor.Registry
    print actor._Parametric
    print actor.Inits
    print actor.Ioinits
    print actor.Parms
    print inits
    print ioinits
    print parms

    actor = actor()
    actor()
    print actor.action
    print actor.action.__name__
    print actor.action.__doc__

if __name__ == "__main__":
    testActorify()
    testDeedify()
