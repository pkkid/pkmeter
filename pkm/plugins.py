# -*- coding: utf-8 -*-
import importlib
import json5
import os
from collections import defaultdict
from pkm import ROOT, log, utils
from PySide6.QtCore import QStandardPaths

CONFIG_LOCATION = QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)


class Plugin:

    def __init__(self, app, rootdir, manifest):
        self.app = app                                          # Reference to main app
        self.rootdir = rootdir                                  # Root directory of this plugin
        self.name = manifest['name']                            # Required: Plugin name
        self.version = manifest['version']                      # Required: Plugin version
        self.theme = manifest['theme']                          # Required: Plugin theme
        self.id = self._createId()                              # Unique ID and namespace
        self.description = manifest.description                 # Optional: Plugin description
        self.settings = self._loadModule(manifest.settings)     # Optional: Settings QObject
        self.widget = self._loadModule(manifest.widget)         # Optional: Widget QObject
    
    def _loadModule(self, modpath):
        """ Load the specified module. """
        if not modpath: return None
        modname, clsname = modpath.split('.', 1)
        modpath = os.path.normpath(f'{self.rootdir}/{modname}.py')
        spec = importlib.util.spec_from_file_location(modname, modpath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, clsname)(self.app, self)
    
    def _createId(self):
        """ Create a unique id for this plugin. """
        theme = ''.join(c for c in self.theme.lower() if c.isalnum() or c == "_")
        name = ''.join(c for c in self.name.lower() if c.isalnum() or c == "_")
        return f'{theme}.{name}'


def loadPlugins(app, plugindirs=None):
    """ Find and load all plugins. Returns a dict of {id: plugin}. """
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
                        plugins[plugin.id] = plugin
                        log.info(f'  Found plugin {plugin.id}')
                    except Exception as err:
                        log.warning(f'Error loading plugin {subdir1}.{subdir2}')
                        log.debug(err, exc_info=1)
    return plugins


def getThemes(plugins):
    """ Loops through all plugins to create a themes dict. Returns a
        dict of {theme: [plugins]}.
    """
    themes = defaultdict(list)
    for plugin in plugins:
        themes[plugin.theme].append(plugin)
    for theme in themes:
        themes[theme] = sorted(themes[theme], key=lambda x: x.name)
    return themes


# def _loadPlugins(self):
#     """ Find and load all plugins. """
#     plugins = {}
#     plugindir = normpath(f'{ROOT}/pkm/plugins')
#     for dir in os.listdir(plugindir):
#         try:
#             log.info(f"Loading {dir} plugin")
#             pluginid = utils.cleanName(dir)
#             plugin = utils.Bunch(id=pluginid)
#             dirpath = normpath(f'{plugindir}/{dir}')
#             if isdir(dirpath):
#                 modules = utils.loadModules(dirpath)
#                 for module in modules:
#                     if module.__name__ == 'settings':
#                         plugin.settings = module.SettingsWidget(self)
#                     if module.__name__ == 'widget':
#                         plugin.widget = module.DesktopWidget(self)
#                         plugin.name = plugin.widget.NAME
#             if plugin.widget is None:
#                 raise Exception(f'{dir} plugin does not contain widget.py')
#             plugins[pluginid] = plugin
#         except Exception as err:
#             log.warning('Error loading plugin %s: %s', dir, err)
#             log.debug(err, exc_info=1)
#     return plugins
