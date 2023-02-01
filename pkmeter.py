#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import signal
import sys
from pathlib import Path
from argparse import ArgumentParser
from PySide2 import QtCore, QtGui, QtQml

sys.path.append(Path(__file__).parent)
from pkm import ROOT, APPNAME, log  # noqa
from pkm import settings  # noqa


class PKMeterApplication(QtCore.QObject):
    
    def __init__(self, app, opts):
        super(PKMeterApplication, self).__init__()
        log.info(f'Starting {APPNAME} application')
        self.app = app                                  # QGuiApplication
        self.opts = opts                                # Command line options
        self.engine = QtQml.QQmlApplicationEngine()     # Application engine
        self.settings = settings.Settings(self)
        self.engine.rootContext().setContextProperty("settings", self.settings)
        self._init_window()

    def _init_window(self):
        """ Init the main desktop window to be displayed. """
        filepath = ROOT / 'qml' / 'desktop.qml'
        self.engine.load(QtCore.QUrl.fromLocalFile(str(filepath)))

    @classmethod
    def start(cls, opts):
        app = QtGui.QGuiApplication()
        
        _ = PKMeterApplication(app, opts)
        app.exec_()  # Start the event loop
        log.info('Quitting..')
        

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = ArgumentParser(description=f'{APPNAME} - Desktop System Monitor')
    parser.add_argument('--loglevel', default='INFO', help='Set the log level (DEBUG, INFO, WARN, ERROR).')
    opts = parser.parse_args()
    if opts.loglevel:
        log.setLevel(opts.loglevel)
    PKMeterApplication.start(opts)
