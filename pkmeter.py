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
from pkm import APPNAME, CONFIG_LOCATION, ROOT
from pkm import log, logfile, plugins, utils
from pkm.datastore import DataStore
from pkm.settings import SettingsWindow


class PKMeter(QtWidgets.QApplication):

    def __init__(self, opts):
        super(PKMeter, self).__init__()
        self.opts = opts                                    # Command line options
        self.data = DataStore()                             # Shared datastore to auto-update widgets
        self.storage = self._initStorage()                  # Setup settings storage
        self._initApplication()                             # Setup OS environment
        self.plugins = plugins.plugins()                    # Available plugins
        self.settings = SettingsWindow()                    # Application settings
        self._showWidgets()
        # self.settings.show()
        self.picker = plugins.widgets()['ColorPicker']()
        self.picker.show()

    def _initStorage(self):
        """ Create the storage object and read all current settings into the datastore. """
        filepath = f'{CONFIG_LOCATION}/{APPNAME}/pkmeter.ini'
        self.storage = QSettings(filepath, QSettings.IniFormat)
        for location in self.storage.allKeys():
            value = self.getSetting(location)
            self.setValue(location.replace('/', '.'), value)
        return self.storage

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
        # Save a few custom fonts
        # https://devdocs.io/qt/qfont#Weight-enum
        # self.fontform = QtGui.QFontDatabase.font('Liberation Mono', 'regular', 11)
        # self.fontform.setWeight(QtGui.QFont.Medium)
        # self.fontform.setHintingPreference(QtGui.QFont.PreferFullHinting)
        # self.setFont(self.fontform)
        # self.fonttitle = QtGui.QFontDatabase.font('Josefin Sans', 'regular', 12)
        # self.fonttitle.setWeight(QtGui.QFont.Medium)
        # self.setFont(self.fonttitle)

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
