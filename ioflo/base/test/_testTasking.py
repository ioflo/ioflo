def Test(real = False, verbose = False):
    """Module Common self test

    """

    import housing
    reload(housing)
    import skedding

    housing.ClearRegistries()

    print(housing.Registries)
    print("")
    print(housing.Registries["tasker"].Names)
    print(housing.Registries["tasker"].Counter)
    print("")

    house = housing.House()

    t1 = Tasker(name = 't1', store = house.store)
    t2 = Tasker(name = 't2', store = house.store)
    t3 = Tasker(name = 't3', store = house.store, period = 0.125)
    t4 = Tasker(name = 't4', store = house.store, period = 0.125)
    t5 = Tasker(name = 't5', store = house.store, period = 0.5)
    t6 = Tasker(name = 't6', store = house.store, period = 1.0)

    house.actives = [t1,t6,t2,t5,t3,t4]

    skedder = skedding.Skedder(name = "TestTasker", period = 0.125, real = real, houses = [house])
    skedder.run()


def TestProfile(real = False, verbose = False):
    """Module Common self test



    """
    import cProfile
    import pstats

    import housing
    reload(housing)
    import skedding

    housing.ClearRegistries()

    print(housing.Registries)
    print("")
    print(housing.Registries["tasker"].Names)
    print(housing.Registries["tasker"].Counter)
    print("")

    house = housing.House()

    t1 = Tasker(name = 't1', store = house.store)
    t2 = Tasker(name = 't2', store = house.store)
    t3 = Tasker(name = 't3', store = house.store, period = 0.125)
    t4 = Tasker(name = 't4', store = house.store, period = 0.125)
    t5 = Tasker(name = 't5', store = house.store, period = 0.5)
    t6 = Tasker(name = 't6', store = house.store, period = 1.0)

    house.actives = [t1,t6,t2,t5,t3,t4]

    skedder = skedding.Skedder(name = "TestSkedder", period = 0.125, real = real, houses = [house])
    #skedder.run()
    cProfile.runctx('skedder.run()',globals(),locals(), './test/profiles/skeddertest')

    p = pstats.Stats('./test/profiles/skeddertest')
    p.sort_stats('time').print_stats()
    p.print_callers()
    p.print_callees()


if __name__ == "__main__":
    Test()
