def TestBox():
    """           """

    #clear registries
    storing.Store.Clear()
    #deeding.Deed.Clear()
    doing.Doer.Clear()

    store = storing.Store(name = 'Test')

    print("\nTesting Box Position Detector")
    detector = DetectorPositionBox(name = 'detectorPositionBox', store = store,
                                   group = 'detector.position.box', input = 'state.position',
                                   parms = dict(track = 0.0, north = -50.0, east = 0.0,
                                                length = 10000, width = 2000))


    store.expose()
    detector._expose()

    print("")
    input = store.fetch('state.position').update(north = 9950.0, east = 0.0)
    detector.action()
    detector._expose()
    print("")
    input = store.fetch('state.position').update(north = 9949.0, east = 0.0)
    detector.action()
    detector._expose()
    print("")
    input = store.fetch('state.position').update(north = 9951, east = 0.0)
    detector.action()
    detector._expose()
    print("")
    input = store.fetch('state.position').update(north = 9900.0, east = 500.0)
    detector.action()
    detector._expose()

    input = store.fetch('state.position').update(north = 1000.0, east = 2000.0)
    detector.action()
    detector._expose()

    input = store.fetch('state.position').update(north = 1000.0, east = -2000.0)
    detector.action()
    detector._expose()

    input = store.fetch('state.position').update(north = 11000.0, east = 500.0)
    detector.action()
    detector._expose()

    input = store.fetch('state.position').update(north = 11000.0, east = 2000.0)
    detector.action()
    detector._expose()

    input = store.fetch('state.position').update(north = 11000.0, east = -2000.0)
    detector.action()
    detector._expose()

    input = store.fetch('state.position').update(north = -1000.0, east = 2000.0)
    detector.action()
    detector._expose()

    input = store.fetch('state.position').update(north = -1000.0, east = -2000.0)
    detector.action()
    detector._expose()


def Test():
    """Module Common self test

    """
    pass


if __name__ == "__main__":
    Test()

