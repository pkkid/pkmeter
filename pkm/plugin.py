# -*- coding: utf-8 -*-
import pkgutil
import importlib
import json5
import os
from pkm import ROOT
from pkm import log, utils
from PySide6.QtCore import QStandardPaths

CONFIG_LOCATION = QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)


class Plugin:

    def __init__(self, app, rootdir, manifest):
        self.app = app
        self.rootdir = rootdir
        self.name = manifest['name']
        self.namespace = manifest['namespace']
        self.version = manifest['version']
        self.theme = manifest['theme']
        self.description = manifest.description
        self.settings = self._loadModule(manifest.settings)
        self.widget = self._loadModule(manifest.widget)
    
    def _loadModule(self, modpath):
        """ Load the specified module. """
        modname, clsname = modpath.split('.', 1)
        modpath = os.path.normpath(f'{self.rootdir}/{modname}.py')
        spec = importlib.util.spec_from_file_location(modname, modpath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, clsname)(self.app, self)


def loadPlugins(app, plugindirs=None):
    plugins = utils.Bunch()
    plugindirs = plugindirs or [
        os.path.normpath(f'{ROOT}/pkm/plugins'),
        os.path.normpath(f'{CONFIG_LOCATION}/plugins'),
    ]
    for plugindir in plugindirs:
        log.info(f"Looking for plugins at {plugindir}")
        if not os.path.isdir(plugindir):
            continue
        for subdir1 in os.listdir(plugindir):
            dirpath = os.path.normpath(f'{plugindir}/{subdir1}')
            for subdir2 in os.listdir(dirpath):
                rootdir = os.path.normpath(f'{dirpath}/{subdir2}')
                manifestpath = os.path.normpath(f'{rootdir}/manifest.json')
                if os.path.isfile(manifestpath):
                    try:
                        with open(manifestpath) as handle:
                            manifest = utils.Bunch(json5.load(handle))
                        plugin = Plugin(app, rootdir, manifest)
                        plugins[plugin.name] = plugin
                        log.info(f'Loaded plugin {subdir1}.{subdir2}')
                    except Exception as err:
                        log.warning(f'Error loading plugin {subdir1}.{subdir2}')
                        log.debug(err, exc_info=1)
    return plugins
