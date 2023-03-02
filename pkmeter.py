#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import signal
import sys
from argparse import ArgumentParser
from os.path import dirname, normpath
from PySide6 import QtGui, QtWidgets

sys.path.append(dirname(__file__))
from pkm import APPNAME, CONFIG_STORAGE, ROOT
from pkm import log, logfile, plugins, utils
from pkm.datastore import DataStore
from pkm.settings import SettingsWindow


class PKMeter(QtWidgets.QApplication):

    def __init__(self, opts):
        super(PKMeter, self).__init__()
        self.opts = opts                        # Command line options
        self._initApplication()                 # Setup OS environment
        self.data = DataStore()                 # Globally shared datastore
        self.plugins = plugins.plugins()        # Find and load plugins
        self.settings = SettingsWindow()        # Settings window
        self._showWidgets()
        # self.settings.show()

    def _initApplication(self):
        """ Setup the application environment. """
        log.info(f'Logging: {logfile}')
        log.info(f'Settings: {normpath(CONFIG_STORAGE.fileName())}')
        # Application fonts
        resources = normpath(f'{ROOT}/resources')
        for filename in os.listdir(resources):
            if filename.endswith('.ttf'):
                filepath = normpath(f'{resources}/{filename}')
                fontid = QtGui.QFontDatabase.addApplicationFont(filepath)
                fontname = QtGui.QFontDatabase.applicationFontFamilies(fontid)[0]
                log.info(f'Loading font {fontname}')
        # Application stylesheet
        filepath = normpath(f'{ROOT}/resources/styles.sass')
        utils.setStyleSheet(self, filepath)

    def _showWidgets(self):
        """ Display all enabled plugins. """
        for pid, plugin in self.plugins.items():
            for cid, component in plugin.components.items():
                if component.datasource:
                    component.datasource.start()
                if component.widget:
                    component.widget.show()

    @classmethod
    def start(cls, opts):
        """ Start the application.
            We set base style OSes have same starting point.
        """
        log.info(f'--- Starting {APPNAME} ---')
        QtWidgets.QApplication.setStyle('windows')
        PKMeter(opts).exec()
        log.info('Quitting.')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = ArgumentParser(description=f'{APPNAME} - Desktop System Monitor')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--verbose', action='store_true', help='Even more verbose logging')
    parser.add_argument('--outline', action='store_true', help='Add outline to QWidgets')
    opts = parser.parse_args()
    if opts.debug:
        log.setLevel('DEBUG')
    PKMeter.start(opts)
