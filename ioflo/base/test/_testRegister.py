
import ioflo.base.aiding as aiding
import ioflo.base.registering as registering

def TestRegister():
    class A(object):
        __metaclass__ = registering.RegisterType
        def __init__(self, name="", store=None):
            self.name = name
            self.store = store


    print(A.Registrar)


def TestMetaclassify():
    @aiding.metaclassify(registering.RegisterType)
    class A(object):
        #__metaclass__ = registering.RegisterType
        def __init__(self, name="", store=None):
            self.name = name
            self.store = store


    print(A.Registrar)


if __name__ == "__main__":
    TestRegister()
    TestMetaclassify()
