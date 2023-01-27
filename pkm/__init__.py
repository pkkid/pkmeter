# -*- coding: utf-8 -*-
import logging, os, signal, sys
from logging.handlers import RotatingFileHandler


# Global Constants
ROOT = os.path.dirname(__file__)

# OS Specific Settings
DATA = os.path.join(os.getenv('HOME'), '.config', 'PKMeter')
if os.name == 'nt':
    DATA = os.path.join(os.getenv('HOME'), os.environ['APPDATA'], 'PKMeter')
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # allow ctrl+c to close

# Logging Configuration
log = logging.getLogger('pkm')
logfile = os.path.join(DATA, 'pkmeter.log')
logformat = logging.Formatter('%(asctime)s %(module)12s:%(lineno)-4s %(levelname)-9s %(message)s')
logdir = os.path.dirname(logfile)
os.makedirs(logdir, exist_ok=True)
filehandler = RotatingFileHandler(logfile, 'a', 512000, 3)
filehandler.setFormatter(logformat)
streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(logformat)
log.addHandler(filehandler)
log.addHandler(streamhandler)
log.setLevel(logging.INFO)
