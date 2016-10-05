# -*- coding: utf-8 -*-
"""
Useful constants
"""
import logging, os, sys
from logging.handlers import RotatingFileHandler


# Basic Configuration
APPNAME = 'PKMeter'
VERSION = '0.7'
CONFIGDIR = os.path.join(os.getenv('HOME'), '.config', 'pkmeter')
CONFIGPATH = os.path.join(CONFIGDIR, 'config.json')
STATUSFILE = os.path.join(CONFIGDIR, 'status.json')
WORKDIR = os.path.dirname(os.path.dirname(__file__))
PLUGINDIR = os.path.join(WORKDIR, 'pkm', 'plugins')
SHAREDIR = os.path.join(WORKDIR, 'share')
THEMEDIR = os.path.join(SHAREDIR, 'themes')
HOMEPAGE = 'http://pushingkarma.com'


# Logging Configuration
log = logging.getLogger('pkm')
logfile = os.path.join(CONFIGDIR, 'pkmeter.log')
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
