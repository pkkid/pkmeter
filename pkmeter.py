#!/usr/bin/python3
# -*- coding: utf-8 -*-
import signal
import sys
from pathlib import Path
from argparse import ArgumentParser
from PySide2 import QtCore, QtGui, QtQml
from PySide2.QtCore import QSettings

sys.path.append(Path(__file__).parent)
import pkm  # noqa
log = pkm.log


class PKMeterApplication:
    
    def __init__(self, opts):
        super(PKMeterApplication, self).__init__()
        log.info(f'Starting {pkm.APPNAME} application')
        self.opts = opts                                # Command line options
        self.engine = QtQml.QQmlApplicationEngine()     # Application engine
        self._init_settings()
        self._init_window()
        self._save_settings()
        
    def _init_settings(self):
        """ Initialize the settings object to save to ~/AppData/Roaming/PKMeter/ on
            Windows and in ~/.config/PKMeter/ on Linux.
        """
        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, pkm.COMPANYNAME, pkm.APPNAME)
        self.settings.setPath(QSettings.IniFormat, QSettings.UserScope, str(pkm.APPDATA))
        log.info(f'Settings location: {self.settings.fileName()}')
        # self._load_settings()

    def _init_window(self):
        """ Init the main desktop window to be displayed. """
        filepath = pkm.ROOT / 'qml' / 'desktop.qml'
        self.window = self.engine.load(QtCore.QUrl.fromLocalFile(str(filepath)))

    def _load_settings(self):
        # root.findChild(QtCore.QObject, "option1").setProperty("checked", settings.value("settings/option1", "World"))
        # root.findChild(QtCore.QObject, "option2").setProperty("text", settings.value("settings/option2", "Hello"))
        pass

    def _save_settings(self):
        # self.settings.setValue("settings/option1", "Hello")
        # self.settings.setValue("settings/option2", "World")
        self.settings.sync()

    @classmethod
    def start(cls, opts):
        app = QtGui.QGuiApplication()
        _ = PKMeterApplication(opts)
        app.exec_()  # Start the event loop
        log.info('Quitting..')
        

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = ArgumentParser(description=f'{pkm.APPNAME} - Desktop System Monitor')
    parser.add_argument('--loglevel', default='INFO', help='Set the log level (DEBUG, INFO, WARN, ERROR).')
    opts = parser.parse_args()
    if opts.loglevel:
        log.setLevel(opts.loglevel)
    PKMeterApplication.start(opts)
