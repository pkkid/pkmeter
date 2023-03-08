#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import signal
import sys
from argparse import ArgumentParser
from os.path import dirname, normpath
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QSettings

sys.path.append(dirname(__file__))
from pkm import APPNAME, ROOT
from pkm import log, logfile, plugins, utils
from pkm.datastore import DataStore
from pkm.settings import SettingsWindow


class PKMeter(QtWidgets.QApplication):

    def __init__(self, opts):
        super(PKMeter, self).__init__()
        self.opts = opts                                    # Command line options
        self.data = DataStore()                             # Shared datastore to auto-update widgets
        self.storage = QSettings(QSettings.IniFormat,       # Settings ini storage
            QSettings.UserScope, APPNAME, APPNAME.lower())
        self.plugins = plugins.plugins()                    # Available plugins
        self.settings = SettingsWindow()                    # Application settings
        self._initApplication()                             # Setup OS environment
        self._showWidgets()
        # self.settings.show()

    def _initApplication(self):
        """ Setup the application environment. """
        log.info(f'Logging: {logfile}')
        log.info(f'Settings: {normpath(self.storage.fileName())}')
        # Application fonts
        resources = normpath(f'{ROOT}/resources')
        for filename in os.listdir(resources):
            if filename.endswith('.ttf'):
                filepath = normpath(f'{resources}/{filename}')
                fontid = QtGui.QFontDatabase.addApplicationFont(filepath)
                fontname = QtGui.QFontDatabase.applicationFontFamilies(fontid)[0]
                log.info(f'Loading font {fontname}')
        # Application stylesheet
        filepath = 'resources/styles.sass'
        utils.setStyleSheet(self, filepath, None, self.opts.outline)

    def _showWidgets(self):
        """ Display all enabled plugins. """
        for pid, plugin in self.plugins.items():
            for cid, component in plugin.components.items():
                if component.datasource:
                    component.datasource.start()
                if component.widget:
                    component.widget.show()
    
    def getSetting(self, location, default=None):
        """ Get the specified settings value. """
        return self.storage.value(location, default)
    
    def getValue(self, datapath, default=None):
        """ Get the specified datastore value. """
        utils.rget(self.data, datapath, default=default)

    def saveSetting(self, location, value):
        """ Save the specified settings value to disk. """
        self.storage.setValue(location, value)

    def setValue(self, datapath, value):
        """ Save the specified datastore value. """
        self.data.setValue(datapath, value)

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
