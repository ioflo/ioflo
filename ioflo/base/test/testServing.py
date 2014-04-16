def TestOpenStuff():
    """    """
    import ioflo.base.storing as storing


    storing.Store.Clear() #clear registry
    s1 = ServerTask(store = storing.Store())
    s2 = ServerTask(store = storing.Store())

    print(s1.server.reopen())
    print(s2.server.reopen())


def Test(verbose = False):
    """Module self test



    """
    import ioflo.base.storing as storing
    import ioflo.base.tasking as tasking

    storing.Store.Clear() #clear registry
    tasking.Tasker.Clear()

    s = Server(store = storing.Store())

    s.store.expose()

    print("ready to go")
    status = s.start()

    while (not (status == STOPPED or status == ABORTED)):
        try:
            status = s.run()

        except KeyboardInterrupt: #CNTL-C shutdown skedder
            print("    Keyboard Interrupt manual shutdown of taskers ...")
            s.server.close()


            break



if __name__ == "__main__":
    Test()

