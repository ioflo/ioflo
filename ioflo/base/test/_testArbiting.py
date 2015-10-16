def Test():
    """Module Common self test

    """
    #clear registries
    storing.Store.Clear()
    #deeding.Deed.Clear()
    doing.Doer.Clear()

    store = storing.Store(name = 'Test')


    in1 = store.create('inputs.in1').create(value = 1.0).truth = 0.5
    in2 = store.create('inputs.in2').create(value = 2.0).truth = False
    in3 = store.create('inputs.in3').create(value = 3.0).truth = None
    in4 = store.create('inputs.in4').create(value = 4.0).truth = True
    in5 = store.create('inputs.in5').create(value = 5.0).truth = 1.0

    inputs = odict()
    inputs['one'] = ('inputs.in1', True, 0.1)
    inputs['two'] = ('inputs.in2', True, 0.5)
    inputs['three'] = ('inputs.in3', True, 0.3)
    inputs['four'] = ('inputs.in4', True, 0.5)
    inputs['five'] = ('inputs.in5', True, 0.2)

    print("\nTesting ArbiterSwitch")
    group = 'arbiters.switch'
    output = 'switch.output'
    arbiter = ArbiterSwitch(name = 'Switch', store = store, output = output,
                            group = group, inputs = inputs)
    arbiter._expose()
    store.expose()

    arbiter.update()
    arbiter._expose()

    arbiter.insels.data.one = False
    arbiter.update()
    arbiter._expose()

    print("\nTesting ArbiterPriority")
    group = 'arbiters.priority'
    output = 'priority.output'
    arbiter = ArbiterPriority(name = 'Priority', store = store, output = output,
                              group = group, inputs = inputs)
    arbiter._expose()
    store.expose()

    arbiter.update()
    arbiter._expose()

    in2.truth = True
    arbiter.insels.data.one = False
    arbiter.update()
    arbiter._expose()

    in1.truth = 0.5
    in2.truth = 0.6
    in3.truth = 0.4
    in4.truth = 0.2
    in5.truth = 0.3
    arbiter.default.truth = 0.7
    arbiter.update()
    arbiter._expose()


    print("\nTesting ArbiterTrusted")
    group = 'arbiters.trusted'
    output = 'trusted.output'
    arbiter = ArbiterTrusted(name = 'Trusted', store = store, output = output,
                             group = group, inputs = inputs)
    arbiter._expose()
    store.expose()

    arbiter.update()
    arbiter._expose()

    in4.truth = 0.7
    arbiter.insels.data.one = False
    arbiter.update()
    arbiter._expose()

    in5.truth = True
    #arbiter.default.truth = 0.7
    arbiter.update()
    arbiter._expose()

    in5.truth = False
    arbiter.default.truth = 0.8
    arbiter.update()
    arbiter._expose()


    print("\nTesting ArbiterWeighted")
    group = 'arbiters.weighted'
    output = 'weighted.output'
    arbiter = ArbiterWeighted(name = 'Weighted', store = store, output = output,
                              group = group, inputs = inputs)
    arbiter._expose()
    store.expose()

    arbiter.update()
    arbiter._expose()

    in4.truth = 0.7
    arbiter.insels.data.one = False
    arbiter.update()
    arbiter._expose()

    in5.truth = True
    arbiter.update()
    arbiter._expose()

    arbiter.default.truth = 0.8
    arbiter.update()
    arbiter._expose()


if __name__ == "__main__":
    test()
