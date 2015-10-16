def TestSalinity():
    """           """

    #clear registries
    storing.Store.Clear()
    #deeding.Deed.Clear()
    doing.Doer.Clear()

    store = storing.Store(name = 'Test')

    print("\nTesting Salinity Sensor Front Simulator")
    sim = SalinitySensorSimulator(name = 'simulatorSensorSalinity', store = store,
                                  group = 'simulator.sensor.salinity', output = 'ctd',
                                  input = 'state.position',
                                  parms = dict(track = 45.0, north = 0.0, east = 0.0,
                                               middle = 32.0, spread = 4.0, rising = True, width = 500.0))

    output = store.fetch('ctd').update(salinity = 32.0)
    store.expose()
    sim._expose()

    for k in range(1, 100):
        print("")
        store.advanceStamp(0.125)

        input = store.fetch('state.position').update(north = k * -50.0, east = 0.0)
        sim.update()
        sim._expose()





def TestMotion():
    """

    """
    #clear registries
    storing.Store.Clear()
    #deeding.Deed.Clear()
    doing.Doer.Clear()

    store = storing.Store(name = 'Test')
    #CreateActions(store)


    print("\nTesting Motion Sim Controller")
    simulator = SimulatorMotionUuv(name = 'simulatorMotionTest', store = store,
                                   group = 'simulator.motion.test',
                                   speed = 'state.speed', speedRate = 'state.speedRate',
                                   depth = 'state.depth', depthRate = 'state.depthRate',
                                   pitch = 'state.pitch', pitchRate = 'state.pitchRate',
                                   altitude = 'state.altitude',
                                   heading = 'state.heading', headingRate = 'state.headingRate',
                                   position = 'state.position',
                                   rpm = 'goal.rpm', stern = 'goal.stern', rudder = 'goal.rudder',
                                   current = 'scenario.current', bottom = 'scenario.bottom',
                                   prevPosition = 'state.position',
                                   parms = dict(rpmLimit = 1500.0, sternLimit = 20.0, rudderLimit = 20.0,
                                                gs = 0.0025, gpr = -0.5, ghr = -0.5))

    store.expose()

    rpm = store.fetch('goal.rpm').update(value = 500.0)
    stern = store.fetch('goal.stern').update(value = 0.0)
    rudder = store.fetch('goal.rudder').update(value = 0.0)
    current = store.fetch('scenario.current').update(north = 0.0, east = 0.0)
    bottom = store.fetch('scenario.bottom').update(value =  50.0)
    prevPosition = store.fetch('scenario.startposition').update(north = 0.0, east = 0.0)

    simulator.restart()
    simulator._expose()
    store.advanceStamp(0.125)
    simulator.update()
    simulator._expose()



def Test():
    """Module Common self test

    """

    #clear registries
    print("\nTesting Controllers\n")
    storing.Store.Clear()
    #deeding.Deed.Clear()
    doing.Doer.Clear()

    store = storing.Store(name = 'Test')
    store.expose()


    current = store.fetch('scenario.current').update(north = 0.0, east = 0.0)
    bottom = store.fetch('scenario.bottom').update(value =  50.0)
    prevPosition = store.fetch('state.position').update(north = 0.0, east = 0.0)

    headinggoal =  store.fetch('goal.heading').update(value = 45.0)
    depthgoal =  store.fetch('goal.depth').update(value = 5.0)
    speedgoal =  store.fetch('goal.speed').update(value = 2.0)
    duration = 10.0

    simulatorMotionUuv.restart()

    controllerPidSpeed._expose()
    controllerPidHeading._expose()
    controllerPidDepth._expose()
    controllerPidPitch._expose()
    simulatorMotionUuv._expose()

    while (store.stamp <= duration):
        print("")
        controllerPidSpeed.action()
        controllerPidHeading.action()
        controllerPidDepth.action()
        controllerPidPitch.action()
        simulatorMotionUuv.action()
        simulatorMotionUuv._expose()

        store.advanceStamp(0.125)



if __name__ == "__main__":
    Test()

