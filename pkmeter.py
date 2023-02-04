#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import signal
import sys
from os.path import dirname, join
from argparse import ArgumentParser
from PySide6 import QtGui, QtWidgets

sys.path.append(dirname(__file__))
from pkm import APPNAME, ROOT, log
from pkm.desktopwidget import DesktopWidget
from pkm.settings import SettingsWindow


class PKMeter(QtWidgets.QApplication):

    def __init__(self, opts):
        log.info(f'Starting {APPNAME} application')
        super(PKMeter, self).__init__()
        self.opts = opts                        # Command line options
        self._init_styles()                     # Load stylesheet and fonts
        self.desktop = DesktopWidget(self)      # Main desktop window
        self.settings = SettingsWindow(self)    # Settings window
        self.desktop.show()
    
    def _init_styles(self):
        """ Load custom fonts. """
        # Application fonts
        resources = join(ROOT, 'resources')
        for filename in os.listdir(resources):
            if filename.endswith('.ttf'):
                fontid = QtGui.QFontDatabase.addApplicationFont(join(resources, filename))
                fontname = QtGui.QFontDatabase.applicationFontFamilies(fontid)[0]
                log.info(f"Loading font '{fontname}'")
        # Application stylesheet
        stylesheet = open(join(ROOT, 'resources', 'style.qss')).read()
        self.setStyleSheet(stylesheet)

    @classmethod
    def start(cls, opts):
        app = PKMeter(opts)
        app.exec()
        log.info('Quitting.')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = ArgumentParser(description=f'{APPNAME} - Desktop System Monitor')
    parser.add_argument('--loglevel', default='INFO', help='Set the log level (DEBUG, INFO, WARN, ERROR).')
    opts = parser.parse_args()
    if opts.loglevel:
        log.setLevel(opts.loglevel)
    PKMeter.start(opts)
