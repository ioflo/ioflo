
def Test():
    """Module self test """


    try:
        Store.Clear()

        store = Store()
        print("Store shares = %s" % store.shares)

        store.add(Share(name = 'autopilot.depth')).create(depth = 0.0)
        print( store.fetch('autopilot.depth').data.depth)
        try:
            print( store.fetch('autopilot.depth').data.value)
        except AttributeError as e1:
            print( e1.message)
        print( store.fetch('autopilot.depth').value)
        print( "Store shares = %s" % store.shares)

        store.create('autopilot.heading').create(heading = 0.0)
        print( store.fetch('autopilot.heading').data.heading)
        try:
            print( store.fetch('autopilot.heading').data.value)
        except AttributeError as e1:
            print( e1.message)
        print( store.fetch('autopilot.heading').value)
        print( "Store shares = %s" % store.shares)

        s = Share(store = store, name = 'autopilot.heading')
        s.create(value = 60.0)
        s.create(value = 50.0)
        print( s.data.value)
        print( s.value)
        print( s.data.value)
        print( s.value)
        store.change(s)
        print( "Store shares = %s" % store.shares)

        try:
            store.add(Share(name = 'autopilot.depth'))
        except ValueError as e1:
            print( e1.message)
        print( "Store shares = %s" % store.shares)

        try:
            store.change(Share(name = 'autopilot.speed'))
        except ValueError as e1:
            print( e1.message)
        print( "Store shares = %s" % store.shares)

        print( "autopilot.heading = %s" % store.fetch('autopilot.heading'))
        print( "autopilot = %s" % store.fetch('autopilot'))
        print( "dog = %s" % store.fetch('dog'))

        store.expose()

    except ValueError as e1:
        print( e1.message)

    return store


if __name__ == "__main__":
    Test()

