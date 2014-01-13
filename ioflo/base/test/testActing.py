import ioflo
from ioflo.base import storing
from ioflo.base import framing
from ioflo.base import acting


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



if __name__ == "__main__":
    test()
