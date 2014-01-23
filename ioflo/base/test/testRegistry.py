def TestRegistry():
    """Module self test



    """
    
    x = Registry()
    print x.name
    y = Registry()
    print y.name

    name = "Hello"
    if Registry.VerifyName(name):
        z = Registry(name= name)
    print Registry.Names
    print Registry.VerifyName(name)
    