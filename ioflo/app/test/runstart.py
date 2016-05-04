#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Runs alls the example FloScripts


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
        if ext != '.flo' or root.startswith('__'):
            continue

        planFiles.append(os.path.abspath(os.path.join(planDirPath, fname)))
    return planFiles

def test():
    """ Execute run.start """
    plans = getPlanFiles()
    filepath = "../plan/continuation.flo"
    opts = dict(gandolf='grey', saruman='white')
    metas = [("opts", ".testmeta.opts", dict(value=opts))]

    ioflo.app.run.start(
                        name='teststart',
                        period=0.125,
                        stamp=0.0,
                        real=False,
                        filepath=filepath,
                        behaviors=None,
                        username="",
                        password="",
                        mode=None,
                        houses=None,
                        metas=metas,
                        verbose=4,
                        )

if __name__ == '__main__':
    test()


