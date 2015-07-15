
import ioflo.base.registering as registering

def TestRegistry():
    """Module self test
    """
    x = Registrar()
    print(x.name)
    y = Registrar()
    print(y.name)

    name = "Hello"
    if Registrar.VerifyName(name):
        z = Registrar(name=name)
    print(Registrar.Names)
    print(Registrar.VerifyName(name))

if __name__ == "__main__":
    TestRegistry()
