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

def main():
    """ Run example scripts"""
    plans = getPlanFiles()
    for plan in plans:
        name, ext = os.path.splitext(os.path.basename(plan))
        ioflo.app.run.run(  name=name,
                            filename=plan,
                            period=0.0625, 
                            verbose=2,
                            realtime=False,)
        
    

if __name__ == '__main__':
    main()

