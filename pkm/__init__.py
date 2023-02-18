# -*- coding: utf-8 -*-
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from os.path import dirname, normpath
from PySide6.QtCore import QStandardPaths

# Global Constants
APPNAME = 'PKMeter'
VERSION = '0.1'
ROOT = dirname(dirname(__file__))
CONFIG_LOCATION = QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)
PLUGIN_DIRS = [
    os.path.normpath(f'{ROOT}/pkm/plugins'),
    os.path.normpath(f'{CONFIG_LOCATION}/{APPNAME}/plugins'),
]

# Logging Configuration
log = logging.getLogger('pkm')
logfile = normpath(f'{CONFIG_LOCATION}/{APPNAME}/pkmeter.log')
logformat = logging.Formatter('%(asctime)s %(module)12s:%(lineno)-4s %(levelname)-9s %(message)s')
os.makedirs(dirname(logfile), exist_ok=True)
filehandler = RotatingFileHandler(logfile, 'a', 512000, 3, 'utf-8')
filehandler.setFormatter(logformat)
streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(logformat)
log.addHandler(filehandler)
log.addHandler(streamhandler)
log.setLevel(logging.INFO)
