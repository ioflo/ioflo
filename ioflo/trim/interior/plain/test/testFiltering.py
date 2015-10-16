

def TestTemperature():
    """           """


    #clear registries
    storing.Store.Clear()
    #deeding.Deed.Clear()
    doing.Doer.Clear()

    store = storing.Store(name = 'Test')

    print("\nTesting Temperature Filter")
    filter = TemperatureSensorFilter(name = 'filterSensorTemp', store = store,
                                     group = 'filter.sensor.temperature', output = 'state.temperature',
                                     input = 'ctd', depth = 'state.depth',
                                     parms = dict(window = 60.0, frac = 0.9, preload = 10.0,
                                                  layer = 40.0, tolerance = 5.0))


    output = store.fetch('state.temperature').update(value = 10.0)
    output = store.fetch('state.depth').update(value = 40.0)
    store.expose()
    filter._expose()

    for k in range(1, 300):
        print("")
        store.advanceStamp(0.125)
        s = 10.0 + 2.0 * math.sin(math.pi * 2.0 * k/300.0)
        input = store.fetch('ctd').update(temperature = s)
        filter.update()
        filter._expose()
        print(s)



def TestSalinity():
    """           """

    #clear registries
    storing.Store.Clear()
    #deeding.Deed.Clear()
    doing.Doer.Clear()

    store = storing.Store(name = 'Test')

    print("\nTesting Salinity Filter")
    filter = SalinitySensorFilter(name = 'filterSensorSalinity', store = store,
                                  group = 'filter.sensor.salinity', output = 'state.salinity',
                                  input = 'ctd.salinity',
                                  parms = dict(window = 60.0, frac = 0.9))

    output = store.fetch('state.salinity').update(value = 32.0)
    store.expose()
    filter._expose()

    for k in range(1, 300):
        print("")
        store.advanceStamp(0.125)
        s = 32.0 + 2.0 * math.sin(math.pi * 2.0 * k/300.0)
        input = store.fetch('ctd.salinity').update(value = s)
        filter.update()
        filter._expose()



def Test():
    """Module Common self test

    """
    pass

if __name__ == "__main__":
    Test()

