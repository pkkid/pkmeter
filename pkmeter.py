#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import signal
import sys
from pathlib import Path
from argparse import ArgumentParser
from PySide6 import QtWidgets

sys.path.append(Path(__file__).parent)
from pkm import APPNAME, log
from pkm.desktop import DesktopWindow


class PKMeterApplication:

    def __init__(self, app, opts):
        log.info(f'Starting {APPNAME} application')
        self.app = app                  # QGuiApplication
        self.opts = opts                # Command line options
        self.desktop = DesktopWindow()  # Main desktop window
        self.desktop.show()
    
    @classmethod
    def start(cls, opts):
        app = QtWidgets.QApplication()
        _ = PKMeterApplication(app, opts)
        app.exec()  # start the event loop
        log.info('Quitting..')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = ArgumentParser(description=f'{APPNAME} - Desktop System Monitor')
    parser.add_argument('--loglevel', default='INFO', help='Set the log level (DEBUG, INFO, WARN, ERROR).')
    opts = parser.parse_args()
    if opts.loglevel:
        log.setLevel(opts.loglevel)
    PKMeterApplication.start(opts)
