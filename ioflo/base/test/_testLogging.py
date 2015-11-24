from ioflo.aid.sixing import *
from ioflo.base import storing
from ioflo.base import logging

def TestLog(rule = UPDATE):
    """Module Common self test

    """
    storing.Store.Clear() #clear registry
    logging.Log.Clear()


    store = storing.Store(name = 'Test',  stamp=0.0)
    heading = store.create('pose.heading').create(value = 0.0)
    position = store.create('pose.position').create(north = 10.0, east = 5.0)

    log = logging.Log(name = 'test', store = store, kind = 'console',
              prefix = 'log', path = './logs/', rule = rule)
    log.addLoggee(tag = 'heading', loggee = 'pose.heading')
    log.addLoggee(tag = 'pos', loggee = 'pose.position')
    log.resolve()
    log.prepare()

    print("logging log %s to file %s" % (log.name, log.fileName))
    log() #log
    for i in range(20):
        store.advanceStamp(0.125)
        if i == 5:
            heading.value += 0.0
            position.data.north += 0.0
            position.data.east -= 0.0
        elif i == 10:
            pass
        else:
            heading.value = float(i)
            position.data.north += 2.0
            position.data.east -= 1.5

        log() #log



    log.close()




def Test(rule = UPDATE):
    """Module Common self test

    """

    storing.Store.Clear()
    logging.Logger.Clear()
    logging.Log.Clear()

    store = storing.Store(name = 'Test', stamp=0.0)

    heading = store.create('pose.heading').create(value = 0.0)
    position = store.create('pose.position').create(north = 10.0, east = 5.0)

    log = logging.Log(name = 'test', store = store, kind = 'text',
              prefix = 'log', path = './logs/', rule = rule)
    log.addLoggee(tag = 'heading', loggee = 'pose.heading')
    log.addLoggee(tag = 'pos', loggee = 'pose.position')
    log.resolve()

    logger = logging.Logger(name = 'Test', store = store)
    logger.addLog(log)

    status = logger.runner.send(START) #also prepares logs
    status = logger.runner.send(RUN)

    for i in range(20):
        store.advanceStamp(0.125)
        if i == 5:
            heading.value += 0.0
            position.data.north += 0.0
            position.data.east -= 0.0
        elif i == 10:
            pass
        else:
            heading.value = float(i)
            position.data.north += 2.0
            position.data.east -= 1.5

        status = logger.runner.send(RUN)

    status = logger.runner.send(STOP)

    status = logger.runner.send(START)
    store.advanceStamp(0.125)
    heading.value += 5.0
    status = logger.runner.send(RUN)
    status = logger.runner.send(STOP)



if __name__ == "__main__":
    Test()

