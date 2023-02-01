# -*- coding: utf-8 -*-
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from PySide6.QtCore import QStandardPaths


# Global Constants
APPNAME = "PKMeter"
ROOT = Path(__file__).parent.parent
APPDATA = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))

# Logging Configuration
log = logging.getLogger('pkm')
logfile = APPDATA / APPNAME / 'pkmeter.log'
logformat = logging.Formatter('%(asctime)s %(module)12s:%(lineno)-4s %(levelname)-9s %(message)s')
os.makedirs(logfile.parent, exist_ok=True)
filehandler = RotatingFileHandler(logfile, 'a', 512000, 3)
filehandler.setFormatter(logformat)
streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(logformat)
log.addHandler(filehandler)
log.addHandler(streamhandler)
log.setLevel(logging.INFO)
