#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import signal
import sys
from argparse import ArgumentParser
from PySide6 import QtGui, QtWidgets

sys.path.append(os.path.dirname(__file__))
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
        iconpath = os.path.join(ROOT, 'resources', 'chart-box-custom.png')
        self.setWindowIcon(QtGui.QIcon(iconpath))
        # Application fonts
        resources = os.path.join(ROOT, 'resources')
        for filename in os.listdir(resources):
            if filename.endswith('.ttf'):
                filepath = os.path.join(resources, filename)
                fontid = QtGui.QFontDatabase.addApplicationFont(filepath)
                fontname = QtGui.QFontDatabase.applicationFontFamilies(fontid)[0]
                log.info(f"Loading font '{fontname}'")
        # Application stylesheet
        stylepath = os.path.join(ROOT, 'resources', 'styles.qss')
        stylesheet = open(stylepath).read()
        self.setStyleSheet(stylesheet)
    
    def _load_plugins(self):
        """ Find and load all plugins. """
        plugins = []
        plugindir = os.path.join(ROOT, 'pkm', 'plugins')
        for dirname in os.listdir(plugindir):
            try:
                log.info(f"Loading {dirname} plugin")
                pluginid = utils.clean_name(dirname)
                plugin = utils.Bunch(id=pluginid)
                dirpath = os.path.join(plugindir, dirname)
                if os.path.isdir(dirpath):
                    modules = utils.load_modules(dirpath)
                    for module in modules:
                        if module.__name__ == 'settings':
                            plugin.settings = module.SettingsWidget(self)
                            plugin.settings.setObjectName(f'{pluginid}_settings')
                        if module.__name__ == 'widget':
                            plugin.widget = module.DesktopWidget(self)
                            plugin.widget.setObjectName(f'{pluginid}_widget')
                if plugin.widget is None:
                    raise Exception(f'{dirname} plugin does not contain widget.py')
                plugins.append(plugin)
            except Exception as err:
                log.warning('Error loading plugin %s: %s', dirname, err)
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
    parser.add_argument('--debug', action='store_true', help='Enable debug logging.')
    opts = parser.parse_args()
    if opts.debug:
        log.setLevel('DEBUG')
    PKMeter.start(opts)
