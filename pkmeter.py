#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import signal
import sys
from os.path import dirname, isdir, normpath
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
        # Application fonts
        resources = normpath(f'{ROOT}/resources')
        for filename in os.listdir(resources):
            if filename.endswith('.ttf'):
                filepath = normpath(f'{resources}/{filename}')
                fontid = QtGui.QFontDatabase.addApplicationFont(filepath)
                fontname = QtGui.QFontDatabase.applicationFontFamilies(fontid)[0]
                log.info(f"Loading font '{fontname}'")
        # Application stylesheet
        styles = open(normpath(f'{ROOT}/resources/styles.qss')).read()
        if opts.outline:
            styles += 'QWidget { border:1px solid rgba(255,0,0,0.3) !important; }'
        self.setStyleSheet(utils.render(styles))
    
    def _load_plugins(self):
        """ Find and load all plugins. """
        plugins = {}
        plugindir = normpath(f'{ROOT}/pkm/plugins')
        for dir in os.listdir(plugindir):
            try:
                log.info(f"Loading {dir} plugin")
                pluginid = utils.clean_name(dir)
                plugin = utils.Bunch(id=pluginid)
                dirpath = normpath(f'{plugindir}/{dir}')
                if isdir(dirpath):
                    modules = utils.load_modules(dirpath)
                    for module in modules:
                        if module.__name__ == 'settings':
                            plugin.settings = module.SettingsWidget(self)
                            # plugin.settings.setObjectName(f'{pluginid}_settings')
                        if module.__name__ == 'widget':
                            plugin.widget = module.DesktopWidget(self)
                            plugin.widget.setObjectName(f'{pluginid}_widget')
                            plugin.name = plugin.widget.NAME
                if plugin.widget is None:
                    raise Exception(f'{dir} plugin does not contain widget.py')
                plugins[pluginid] = plugin
            except Exception as err:
                log.warning('Error loading plugin %s: %s', dir, err)
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
    parser.add_argument('--outline', action='store_true', help='Add outline to QWidgets')
    opts = parser.parse_args()
    if opts.debug:
        log.setLevel('DEBUG')
    PKMeter.start(opts)
