# -*- coding: utf-8 -*-
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from os.path import dirname, normpath
from PySide6.QtCore import QStandardPaths

# Global Constants
APPNAME = 'PKMeter'
ROOT = dirname(dirname(__file__))
APPDATA = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)

# Color Theme
THEME = {
    'primary': '#458588',
    'primarylight': '#83a598',
    'secondary': '#282828',
    'secondarylight': '#3c3836',
    'secondarydark': '#1d2021',
    'primarytext': '#fbf1c7',
    'secondarytext': '#bdae93',
    'dimtext': '#a89984',
}

# Logging Configuration
log = logging.getLogger('pkm')
logfile = normpath(f'{APPDATA}/{APPNAME}/pkmeter.log')
logformat = logging.Formatter('%(asctime)s %(module)12s:%(lineno)-4s %(levelname)-9s %(message)s')
os.makedirs(dirname(logfile), exist_ok=True)
filehandler = RotatingFileHandler(logfile, 'a', 512000, 3, 'utf-8')
filehandler.setFormatter(logformat)
streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(logformat)
log.addHandler(filehandler)
log.addHandler(streamhandler)
log.setLevel(logging.INFO)
