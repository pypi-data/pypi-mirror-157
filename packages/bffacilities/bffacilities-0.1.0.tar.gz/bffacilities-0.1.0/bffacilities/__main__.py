#!/usr/env/bin python3
# -*- coding: utf-8 -*-

'''
 # @ Author: brifuture
 # @ Create Time: 2021-04-02 15:33
 # @ Modified by: brifuture
 # @ Modified time: 2021-06-11 11:38
 # @ Description: This File is created and the program is coded by BriFuture. (c) All rights reserved.
    Use as script entry
 '''

import sys, os
import os.path as osp
from ._constants import BFF_ROOT_PATH as RootPath

from pathlib import Path

from . import __version__
from ._plugin import load_scripts
import json
from .utils import initGetText, createLogger
logger = createLogger('bffacilities', stream=True)

#  add custom sub-commands in this file
try:
    with open(osp.join(RootPath, "myscripts/meta.json")) as f:
        availableCmds = json.load(f)
except:
    availableCmds = {}
    logger.warning(f"RootDir ({RootPath}) dose not contain meta " )
    
availableCmds["tray"] = "tray"

tr = initGetText("bffacility")
def onError(parser):
    logger.info(tr('Available sub commands: '))
    cmds = ""
    for i, c in enumerate(availableCmds):
        cmds += f"{i+1}: {c}  \t"
    logger.info(f"{cmds} \n")
    parser.print_usage()

def loadPriScript(arg):
    """arg contain subscripts:
    for example: `bff pri test -h`
    arg should be `test -h`
    """
    if len(arg) < 1:
        logger.critical("Not Supported!")
        return
    pripath = Path(RootPath) / "../_pri"
    pripath = pripath.resolve()
    try:
        subscript = arg[0]
        p, ss = osp.split(subscript)
        pripath = Path(osp.join(pripath, p))
        if ss.endswith(".py"):
            ss = ss[:-3]
        logger.info(f"{ss}, {pripath}")
        arg = arg[1:]
        load_scripts(ss, arg, pripath)
    except Exception as e:
        logger.warning("Error Running Pri Scripts: ", e) 

def loadTorch(arg):
    if len(arg) < 1:
        logger.critical("Not Supported!")
        return
    torchpath = (Path(RootPath) / "torch").resolve()
    try:
        subscript = arg[0]
        p, ss = osp.split(subscript)
        torchpath = Path(osp.join(torchpath, p))
        if ss.endswith(".py"):
            ss = ss[:-3]
        logger.info(f"{ss}, {torchpath}")
        arg = arg[1:]
        load_scripts(ss, arg, torchpath)
    except Exception as e:
        logger.warning("Error running scripts: ", e) 

def main(**otherOpt):
    from argparse import ArgumentParser
    parser = ArgumentParser(prog='bffacility', description="Usage: bffacility <subcommand> [args]")
    parser.add_argument('subcmd', type=str, nargs="?", help=tr('type sub-command to exec certain function'))
    parser.add_argument('-V', action="version", help=tr(f'show version: {__version__}'), version=f'%(prog)s {__version__}')

    sys.argv.pop(0)  # remove script name
    args = vars(parser.parse_args(sys.argv[:1]))
    cmd = args["subcmd"]
    
    arg = sys.argv[1:]
    
    # logger.info(sys.stdout)

    if cmd == 'tray':
        from .win_tray import main as tray
        tray(arg)
        return
    elif cmd == 'pri':
        loadPriScript(arg)
    elif cmd == 'torch':
        loadTorch(arg)
    elif cmd in availableCmds:
        load_scripts(availableCmds[cmd], arg, **otherOpt)
    else:
        onError(parser)

# if __name__ == "__main__":
#     main()