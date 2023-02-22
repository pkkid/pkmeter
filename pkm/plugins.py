# -*- coding: utf-8 -*-
import importlib
import inspect
import json5
import os
import pkgutil
from collections import defaultdict
from functools import cached_property
from pkm import APPNAME, CONFIG_STORAGE, PLUGIN_DIRS, VERSION, log, utils
from PySide6 import QtCore, QtGui, QtWidgets

_WIDGETS = None


class Plugin:

    def __init__(self, rootdir, manifest):
        self.manifest = manifest                    # Reference to the manifest
        self.rootdir = rootdir                      # Root directory of this plugin
        self.name = manifest['name']                # Required: Plugin name
        self.version = manifest['version']          # Required: Plugin version
        self.theme = manifest['theme']              # Required: Plugin theme
        self.description = manifest.description     # Optional: Plugin description
    
    @cached_property
    def settings(self):
        return self._loadModule(self.manifest.settings)

    @cached_property
    def widget(self):
        return self._loadModule(self.manifest.widget)
    
    @cached_property
    def themevar(self):
        return ''.join(c for c in self.theme.lower() if c.isalnum() or c == "_")
    
    @cached_property
    def namevar(self):
        return ''.join(c for c in self.name.lower() if c.isalnum() or c == "_")

    @cached_property
    def id(self):
        return f'{self.themevar}.{self.namevar}'

    def saveValue(self, varname, value):
        location = f'{self.themevar}/{self.namevar}.{varname}'
        CONFIG_STORAGE.setValue(location, value)
    
    def getValue(self, varname, default=None):
        location = f'{self.themevar}/{self.namevar}.{varname}'
        return CONFIG_STORAGE.value(location, default)

    def _loadModule(self, modpath):
        """ Load the specified module. """
        if not modpath: return None
        modname, clsname = modpath.split('.', 1)
        modpath = os.path.normpath(f'{self.rootdir}/{modname}.py')
        spec = importlib.util.spec_from_file_location(modname, modpath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, clsname)(self)


def themes(plugins):
    """ Loops through all plugins to create a themes dict. Returns a
        dict of {theme: [plugins]}.
    """
    themes = defaultdict(list)
    for plugin in plugins:
        themes[plugin.theme].append(plugin)
    for theme in themes:
        themes[theme] = sorted(themes[theme], key=lambda x: x.name)
    return themes


def plugins(plugindirs=PLUGIN_DIRS, depth=0):
    """ Find and load all plugins. Returns a dict of {id: plugin}. """
    plugins = utils.Bunch()
    pathfilter = lambda path: os.path.isfile(path) and os.path.basename(path) == 'manifest.json'
    for filepath in _iterDirectories(plugindirs, pathfilter):
        try:
            with open(filepath) as handle:
                manifest = utils.Bunch(json5.load(handle))
            plugin = Plugin(os.path.dirname(filepath), manifest)
            log.info(f'Loading plugin {plugin.id}')
            plugins[plugin.id] = plugin
        except Exception as err:
            name = '.'.join(filepath.split(os.path.sep)[-2:-1])
            log.warning(f'Error loading plugin {name}')
            log.debug(err, exc_info=1)
    return plugins


def widgets(plugindirs=PLUGIN_DIRS):
    """ Load widgets from the plugin directories as well as the Qt libraries. """
    global _WIDGETS
    if _WIDGETS is None:
        # Start with a few constants
        app = QtCore.QCoreApplication.instance()
        _WIDGETS = {'APPNAME':APPNAME, 'VERSION':VERSION, 'app':app}
        # Load widgets from the Qt libraries; This section should probably live in
        # the qtemplate module, but I feel like keeping it together with the plugin
        # widget loader makes more sense than spreading it around.
        for module in (QtGui, QtWidgets):
            members = dict(inspect.getmembers(module, inspect.isclass))
            _WIDGETS.update({k:v for k,v in members.items()})
        # Load widgets from the plugin dirtectories
        dirfilter = lambda path: os.path.isdir(path) and os.path.basename(path) == 'widgets'
        clsfilter = lambda obj: (inspect.isclass(obj) and obj.__module__ == module.__name__
            and issubclass(obj, QtWidgets.QWidget))
        for dirpath in _iterDirectories(PLUGIN_DIRS, dirfilter):
            for loader, name, ispkg in pkgutil.iter_modules([dirpath]):
                try:
                    module = loader.find_module(name).load_module(name)
                    members = dict(inspect.getmembers(module, clsfilter))
                    for clsname, cls in members.items():
                        log.info(f'Loading widget {clsname}')
                        _WIDGETS[clsname] = cls
                except Exception as err:
                    log.warn('Error loading module %s: %s', name, err)
                    log.debug(err, exc_info=1)
    return _WIDGETS


def _iterDirectories(dirpaths, predicate, maxdepth=2, depth=0):
    for dirpath in dirpaths:
        if not os.path.isdir(dirpath) or depth > maxdepth:
            continue
        for filename in os.listdir(dirpath):
            filepath = os.path.join(dirpath, filename)
            if predicate(filepath):
                yield filepath
            elif os.path.isdir(filepath):
                for result in _iterDirectories([filepath], predicate, maxdepth, depth+1):
                    yield result
