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

def run(plan):
    """
    Run the  example script named plan
    """

    plan = os.path.join(PLAN_DIR_PATH, plan)
    plan = os.path.abspath(plan)
    root, ext = os.path.splitext(plan)
    if ext != '.flo' or root.startswith('__'):
        print("**** Invalid plan file = {0}.\n".format(plan))
        sys.exit()

    name, ext = os.path.splitext(os.path.basename(plan))
    skeddar = ioflo.app.run.run(  name=name,
                        filepath=plan,
                        period=0.0625,
                        verbose=2,
                        real=False,)

    print("Running Plan: {0}\n".format(plan))
    failed = False
    for house in skeddar.houses:
        failure = house.metas['failure'].value
        if failure:
            failed = True
            print("**** Failed in House = {0}. "
                  "Failure = {1}.\n".format(house.name, failure))
        else:
            print("**** Succeeded in House = {0}.\n".format(house.name))


if __name__ == '__main__':
    run('testRearRaze.flo')

