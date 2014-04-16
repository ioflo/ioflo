
def TestOut():
    """Module self test



    """

    m = MonitorOut(store = storing.Store())
    print("ready to go")
    status = m.start()

    while (not (status == STOPPED or status == ABORTED)):
        status = m.run()

    #status = m.stop()



def Test():
    """Module self test



    """
    import storing

    m = Monitor(store = storing.Store())
    print("ready to go")
    status = m.start()

    while (not (status == STOPPED or status == ABORTED)):
        try:
            status = m.run()

        except KeyboardInterrupt: #CNTL-C shutdown skedder
            print("    Keyboard Interrupt manual shutdown of taskers ...")
            m.server.close()


            break


if __name__ == "__main__":
    Test()
