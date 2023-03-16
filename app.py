#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inkwell
import signal
import sys
from argparse import ArgumentParser
from os.path import dirname, normpath
from PySide6 import QtWidgets
from PySide6.QtCore import QSettings
from qtemplate import DataStore

sys.path.append(dirname(__file__))
from pkm import APPNAME, CONFIG_LOCATION
from pkm import log, logfile, plugins, utils
from pkm.settings import SettingsWindow


class Application(QtWidgets.QApplication):

    def __init__(self, opts):
        super(Application, self).__init__()
        inkwell.addApplicationFonts()               # Add Inkwell fonts
        inkwell.applyStyleSheet(self)               # Apply Inkwell styles
        self.opts = opts                            # Command line options
        self.data = DataStore()                     # Shared datastore to auto-update widgets
        self.storage = self._initStorage()          # Setup settings storage
        self.plugins = plugins.plugins()            # Available plugins
        self.settings = SettingsWindow()            # Application settings
        self._showWidgets()

    def _initStorage(self):
        """ Create the storage object and read all current settings into the datastore. """
        filepath = f'{CONFIG_LOCATION}/{APPNAME}/pkmeter.ini'
        self.storage = QSettings(filepath, QSettings.IniFormat)
        log.info(f'Settings: {normpath(self.storage.fileName())}')
        log.info(f'Logging: {logfile}')
        for location in self.storage.allKeys():
            value = self.getSetting(location)
            self.setValue(location.replace('/', '.'), value)
        return self.storage

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
        value = self.storage.value(location, None)
        log.debug(f'getSetting({location=}) = {value}')
        return default if value is None else utils.parseValue(value)
    
    def getValue(self, datapath, default=None):
        """ Get the specified datastore value. """
        value = utils.rget(self.data, datapath, default=default)
        log.debug(f'getValue({datapath=}) = {value}')
        return default if value is None else value

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
        Application(opts).exec()
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
    Application.start(opts)
