# -*- coding: utf-8 -*-
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from os.path import dirname, join
from PySide6.QtCore import QStandardPaths

# Global Constants
APPNAME = 'PKMeter'
ROOT = dirname(dirname(__file__))
APPDATA = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)

# Logging Configuration
log = logging.getLogger('pkm')
logfile = join(APPDATA, APPNAME, 'pkmeter.log')
logformat = logging.Formatter('%(asctime)s %(module)12s:%(lineno)-4s %(levelname)-9s %(message)s')
os.makedirs(dirname(logfile), exist_ok=True)
filehandler = RotatingFileHandler(logfile, 'a', 512000, 3, 'utf-8')
filehandler.setFormatter(logformat)
streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(logformat)
log.addHandler(filehandler)
log.addHandler(streamhandler)
log.setLevel(logging.INFO)
