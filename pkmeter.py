#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import signal
import sys
from os.path import dirname, join
from argparse import ArgumentParser
from PySide6 import QtGui, QtWidgets

sys.path.append(dirname(__file__))
from pkm import APPNAME, ROOT, log
from pkm.desktop import DesktopWindow


class PKMeterApplication:

    def __init__(self, app, opts):
        log.info(f'Starting {APPNAME} application')
        self.app = app                  # QGuiApplication
        self.opts = opts                # Command line options
        self._init_fonts()              # Load custom fonts
        self.desktop = DesktopWindow()  # Main desktop window
        self.desktop.show()
    
    def _init_fonts(self):
        """ Load custom fonts. """
        # font-family: 'Material Design Icons'
        filepath = join(ROOT, 'resources', 'mdi-v7.1.96.ttf')
        font_id = QtGui.QFontDatabase.addApplicationFont(filepath)
        font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
        log.info(font_family)

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
