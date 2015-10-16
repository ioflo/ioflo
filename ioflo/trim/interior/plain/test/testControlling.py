def TestPID():
    """

    """
    #clear registries
    storing.Store.Clear()
    #deeding.Deed.Clear()
    doing.Doer.Clear()

    store = storing.Store(name = 'Test')



    print("\nTesting PID Controller")
    controller = ControllerPid(name = 'controllerPIDTest', store = store,
                               group = 'controller.pid.test', output = 'goal.testoutput',
                               input = 'state.testinput', rate = 'state.testrate', rsp = 'goal.testrsp',
                               parms = dict(wrap = 0.0, drsp = 0.01, calcRate = True,
                                            ger = 1.0, gff = 0.0, gpe = 3.0, gde = 0.0, gie = 0.0,
                                            esmax = 0.0, esmin = 0.0, ovmax = 20.0, ovmin = -20.0))


    store.expose()

    input = store.fetch('state.testinput').update(value = 0.0)
    rate = store.fetch('state.testrate').update(value = 0.0)
    rsp = store.fetch('goal.testrsp').update(value = 45.0)
    controller.update()
    controller._expose()

    input.value = 22.5
    store.advanceStamp(0.125)
    controller.update()
    controller._expose()

    print("\nTesting Speed PID Controller")
    input = store.fetch('state.speed').update(value = 0.0)
    rate = store.fetch('state.speedRate').update(value = 0.0)
    rsp = store.fetch('goal.speed').update(value = 2.0)
    controllerPIDSpeed._expose()
    store.advanceStamp(0.125)
    controllerPIDSpeed.update()
    controllerPIDSpeed._expose()

    print("\nTesting Heading PID Controller")
    input = store.fetch('state.heading').update(value = 0.0)
    rate = store.fetch('state.headingRate').update(value = 0.0)
    rsp = store.fetch('goal.heading').update(value = 45.0)
    controllerPIDHeading._expose()
    store.advanceStamp(0.125)
    controllerPIDHeading.update()
    controllerPIDHeading._expose()

    print("\nTesting Depth PID Controller")
    input = store.fetch('state.depth').update(value = 0.0)
    rate = store.fetch('state.depthRate').update(value = 0.0)
    rsp = store.fetch('goal.depth').update(value = 5.0)
    controllerPIDDepth._expose()
    store.advanceStamp(0.125)
    controllerPIDDepth.update()
    controllerPIDDepth._expose()

    print("\nTesting Pitch PID Controller")
    input = store.fetch('state.pitch').update(value = 0.0)
    rate = store.fetch('state.pitchRate').update(value = 0.0)
    rsp = store.fetch('goal.pitch').update(value = 5.0)
    controllerPIDPitch._expose()
    store.advanceStamp(0.125)
    controllerPIDPitch.update()
    controllerPIDPitch._expose()



def TestMotion():
    """

    """

    #clear registries
    storing.Store.Clear()
    #deeding.Deed.Clear()
    doing.Doer.Clear()

    store = storing.Store(name = 'Test')


    print("\nTesting Motion Sim Controller")
    controller = MotionController(name = 'controllerMotionTest', store = store,
                                  group = 'controller.motion.test',
                                  speed = 'state.speed', speedRate = 'state.speedRate',
                                  depth = 'state.depth', depthRate = 'state.depthRate',
                                  pitch = 'state.pitch', pitchRate = 'state.pitchRate',
                                  altitude = 'state.altitude',
                                  heading = 'state.heading', headingRate = 'state.headingRate',
                                  position = 'state.position',
                                  rpm = 'goal.rpm', stern = 'goal.stern', rudder = 'goal.rudder',
                                  current = 'scenario.current', bottom = 'scenario.bottom',
                                  prevPosition = 'state.position',
                                  parms = dict(rpmLimit = 1000.0, sternLimit = 20.0, rudderLimit = 20.0,
                                               gs = 0.0025, gpr = -0.5, ghr = -0.5))

    store.expose()

    rpm = store.fetch('goal.rpm').update(value = 500.0)
    stern = store.fetch('goal.stern').update(value = 0.0)
    rudder = store.fetch('goal.rudder').update(value = 0.0)
    current = store.fetch('scenario.current').update(north = 0.0, east = 0.0)
    bottom = store.fetch('scenario.bottom').update(value =  50.0)
    prevPosition = store.fetch('scenario.startposition').update(north = 0.0, east = 0.0)

    controller.restart()
    controller._expose()
    store.advanceStamp(0.125)
    controller.update()
    controller._expose()



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

    controllerMotionVehicle.restart()

    controllerPidSpeed._expose()
    controllerPidHeading._expose()
    controllerPidDepth._expose()
    controllerPidPitch._expose()
    controllerMotionVehicle._expose()

    while (store.stamp <= duration):
        print("")
        controllerPidSpeed.action()
        controllerPidHeading.action()
        controllerPidDepth.action()
        controllerPidPitch.action()
        controllerMotionVehicle.action()
        controllerMotionVehicle._expose()

        store.advanceStamp(0.125)



if __name__ == "__main__":
    Test()
