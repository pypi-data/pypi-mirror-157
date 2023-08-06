# -*- coding: utf-8 -*-

"""
0.1.0: optimize utils

0.0.41: optimize network.socket 

0.0.40: move socket server and bluetooth into network, remove _globals

0.0.35: optimize scripts in torch folder

0.0.34: fix database error

0.0.33: move logger from utils to avoid log too much content

0.0.32: update with pyupdator

0.0.22: socket server has been improved a lot, interface has changed

v0.0.20 add bluetooth manager for bluetooth device list and connect

v0.0.19 some updates on generateQtTest and torch scripts

0.0.17: scripts in `myscripts` folder could add more scripts
without change main.py file.

0.0.13: add torch scripts and labelme scripts for MachineLearing data processing or model building.

0.0.7: add simple tcp socket server

0.0.6: add common flask functions
"""

__version__ = "0.1.0"
__author__ = "BriFuture"

from .utils import createLogger, initGetText, setup_logger
from ._constants import BFF_ROOT_PATH, BFF_OTHER_PATH, terminal_colors


