#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import signal
import sys
from os.path import dirname, join
from argparse import ArgumentParser
from PySide6 import QtGui, QtWidgets

sys.path.append(dirname(__file__))
from pkm import APPNAME, ROOT
from pkm import log, utils  # noqa
from pkm.settings import SettingsWindow


class PKMeter(QtWidgets.QApplication):

    def __init__(self, opts):
        super(PKMeter, self).__init__()
        self.opts = opts                        # Command line options
        self._init_application()                # Setup OS environment
        self.settings = SettingsWindow(self)    # Settings window
        self.plugins = self._load_plugins()     # Find and load plugins
        self.settings.show()
    
    def _init_application(self):
        """ Setup the application environment. """
        # Application Icon
        iconpath = join(ROOT, 'resources', 'chart-box-custom.png')
        self.setWindowIcon(QtGui.QIcon(iconpath))
        # Application fonts
        resources = join(ROOT, 'resources')
        for filename in os.listdir(resources):
            if filename.endswith('.ttf'):
                fontid = QtGui.QFontDatabase.addApplicationFont(join(resources, filename))
                fontname = QtGui.QFontDatabase.applicationFontFamilies(fontid)[0]
                log.info(f"Loading font '{fontname}'")
        # Application stylesheet
        stylesheet = open(join(ROOT, 'resources', 'styles.qss')).read()
        self.setStyleSheet(stylesheet)
    
    def _load_plugins(self):
        """ Find and load all plugins. """
        plugins = utils.Bunch()
        plugindir = join(ROOT, 'pkm', 'plugins')
        for name in os.listdir(plugindir):
            try:
                log.info(f"Loading {name} plugin")
                plugin = utils.Bunch(widget=None, settings=None)
                dirpath = join(plugindir, name)
                if os.path.isdir(dirpath):
                    modules = utils.load_modules(dirpath)
                    for module in modules:
                        if module.__name__ == 'widget':
                            plugin.widget = module.DesktopWidget(self)
                        if module.__name__ == 'settings':
                            plugin.settings = module.SettingsWidget()
                if plugin.widget is None:
                    raise Exception(f'{name} plugin does not contain widget.py')
                plugins[name] = plugin
            except Exception as err:
                log.warning('Error loading plugin %s: %s', name, err)
                log.debug(err, exc_info=1)
        return plugins

    @classmethod
    def start(cls, opts):
        log.info('---')
        log.info(f'Starting {APPNAME} application')
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
