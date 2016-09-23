#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Runs all the example FloScripts


"""
import sys
import os

import ioflo.app.run

PLAN_DIR_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    , 'plan')

def getPlanFiles(planDirPath=PLAN_DIR_PATH):
    planFiles = []
    for fname in os.listdir(os.path.abspath(planDirPath)):
        root, ext = os.path.splitext(fname)
        if ext != '.flo' or root.startswith('__') or root.startswith('gps'):
            continue

        planFiles.append(os.path.abspath(os.path.join(planDirPath, fname)))
    return planFiles

def main():
    """ Run example scripts"""
    failedCount = 0
    plans = getPlanFiles()
    for plan in plans:
        failed = False
        name, ext = os.path.splitext(os.path.basename(plan))
        try:
            skeddar = ioflo.app.run.run(  name=name,
                                filepath=plan,
                                period=0.0625,
                                verbose=1,
                                real=False,)

            print("Plan {0}\n  Skeddar {1}\n".format(plan, skeddar.name))

            if not skeddar.built:
                failed = True
            else:
                for house in skeddar.houses:
                    failure = house.metas['failure'].value
                    if failure:
                        failed = True
                        print("**** Failed in House = {0}. "
                              "Failure = {1}.\n".format(house.name, failure))
                    else:
                        print("**** Succeeded in House = {0}.\n".format(house.name))

        except Exception as ex:
            print("Failed with Exception: {0}\n".format(ex))
            failed = True

        if failed:
            failedCount += 1

    print("{0} failed out of {1}.\n".format(failedCount, len(plans)))

if __name__ == '__main__':
    main()

