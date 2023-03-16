# -*- coding: utf-8 -*-
import importlib
import inspect
import json5
import os
import pkgutil
from functools import cached_property
from pkm import APPNAME, PLUGIN_DIRECTORIES, VERSION
from pkm import base, log, utils
from PySide6 import QtCore, QtGui, QtWidgets

_WIDGETS = None


class Plugin:

    def __init__(self, rootdir, manifest):
        self.manifest = manifest                        # Reference to the manifest
        self.rootdir = rootdir                          # Root directory of this plugin
        self.name = manifest['name']                    # Required: Plugin name
        self.version = manifest['version']              # Required: Plugin version
        self.author = manifest.get('author')            # Optional: Plugin author
        self.description = manifest.get('description')  # Optional: Plugin description
        self.components = self._components()

    @cached_property
    def id(self):
        idstr = self.manifest['id'] if 'id' in self.manifest else self.name
        return ''.join(c for c in idstr.lower() if c.isalnum() or c == "_")
    
    @cached_property
    def widgets(self):
        widgets = {}
        if not self.manifest.get('commonwidgets'):
            return widgets
        dirpath = os.path.normpath(f'{self.rootdir}/{self.manifest["commonwidgets"]}')
        for loader, name, ispkg in pkgutil.iter_modules([dirpath]):
            try:
                module = loader.find_module(name).load_module(name)
                members = dict(inspect.getmembers(module, lambda obj: (inspect.isclass(obj)
                    and obj.__module__ == module.__name__
                    and issubclass(obj, (QtWidgets.QWidget, base.QTemplateTag))
                )))
                for clsname, cls in members.items():
                    widgets[clsname] = cls
            except Exception as err:
                log.warn('Error loading module %s: %s', name, err)
                log.debug(err, exc_info=1)
        return widgets

    def _components(self):
        components = utils.Bunch()
        for submanifest in self.manifest.get('components', []):
            log.info(f'  adding component {submanifest["name"]}')
            component = Component(self, submanifest)
            components[component.id] = component
        return components
    
    def styles(self):
        pass
    

class Component:

    def __init__(self, plugin, manifest):
        self.plugin = plugin                            # Reference to Plugin object
        self.app = QtCore.QCoreApplication.instance()   # QtCore application
        self.manifest = manifest                        # Reference to the manifest
        self.name = manifest['name']                    # Required: Plugin name

    @cached_property
    def fullid(self):
        return f'{self.plugin.id}.{self.id}'

    @cached_property
    def id(self):
        idstr = self.manifest['id'] if 'id' in self.manifest else self.name
        return ''.join(c for c in idstr.lower() if c.isalnum() or c == "_")

    @cached_property
    def datasource(self):
        clspath = self.manifest.get('datasource')
        if not clspath: return None
        return loadmodule(self.plugin.rootdir, clspath, self)

    @cached_property
    def settings(self):
        clspath = self.manifest.get('settings')
        if not clspath: return None
        return loadmodule(self.plugin.rootdir, clspath, self)
    
    @cached_property
    def widget(self):
        clspath = self.manifest.get('widget')
        if not clspath: return None
        return loadmodule(self.plugin.rootdir, clspath, self)
    
    def getSetting(self, name, default=None):
        """ Get the specified settings value. """
        location = f'{self.plugin.id}/{self.id}.{name}'
        return self.app.getSetting(location, default)

    def getValue(self, name, default=None):
        """ Get the specified datastore value for this namespace. """
        namespace = self.manifest.get('datanamespace', self.fullid)
        datapath = f'{namespace}.{name}'
        result = self.app.getValue(datapath, default)
        return result if result is not None else default

    def saveSetting(self, name, value):
        """ Save the specified settings value to disk. """
        location = f'{self.plugin.id}/{self.id}.{name}'
        self.app.saveSetting(location, value)
        # Also update value in the datastore. This does NOT use the namespace
        # override because settings values should be unrelated to the datasource.
        datapath = location.replace('/', '.')
        self.app.setValue(datapath, value)

    def setValue(self, name, value):
        """ Set the spcified datastore value for this namespace. """
        namespace = self.manifest.get('datanamespace', self.fullid)
        datapath = f'{namespace}.{name}'
        return self.app.setValue(datapath, value)


def loadmodule(rootdir, modpath, component):
    """ Load the specified module. """
    if not modpath: return None
    log.debug(f'  loading module {modpath}')
    modname, clsname = modpath.rsplit('.', 1)
    modpath = os.path.normpath(f'{rootdir}/{modname.replace(".","/")}.py')
    spec = importlib.util.spec_from_file_location(modname, modpath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, clsname)(component)
    

def plugins(plugindirs=PLUGIN_DIRECTORIES):
    """ Find and load all plugins. Returns a dict of {id: plugin}. """
    plugins = utils.Bunch()
    for plugindir in plugindirs:
        if not os.path.isdir(plugindir): continue
        for dirname in os.listdir(plugindir):
            dirpath = os.path.normpath(f'{plugindir}/{dirname}')
            if not os.path.isdir(dirpath): continue
            for filename in os.listdir(dirpath):
                filepath = os.path.normpath(f'{dirpath}/{filename}')
                if os.path.isfile(filepath) and filename == 'manifest.json':
                    try:
                        with open(filepath) as handle:
                            manifest = json5.load(handle)
                        log.info(f'Loading plugin {dirname}')
                        plugin = Plugin(dirpath, manifest)
                        plugins[plugin.id] = plugin
                    except Exception as err:
                        log.warning(f'Error loading plugin {dirname}')
                        log.debug(err, exc_info=1)
    initGlobalContext(plugins)
    return plugins


def widgets():
    global _WIDGETS
    if _WIDGETS is None:
        # Add application constants
        app = QtCore.QCoreApplication.instance()
        _WIDGETS = {'APPNAME':APPNAME, 'VERSION':VERSION, 'app':app, 'data':app.data}
        # Load widgets from the Qt libraries; This section should probably live in
        # the qtemplate module, but I feel like keeping it together with the plugin
        # widget loader makes more sense than spreading it around.
        for module in (QtGui, QtWidgets):
            members = dict(inspect.getmembers(module, inspect.isclass))
            _WIDGETS.update({k:v for k,v in members.items()})
        # Load widgets from the plugin directories
        for pid, plugin in app.plugins.items():
            _WIDGETS.update(plugin.widgets)
    return _WIDGETS


def initGlobalContext(plugins):
    from qtemplate import QTemplateWidget  # noqa
    app = QtCore.QCoreApplication.instance()
    QTemplateWidget.globalcontext.update({'APPNAME':APPNAME, 'VERSION':VERSION, 'app':app, 'data':app.data})
    for pid, plugin in plugins.items():
        QTemplateWidget.globalcontext.update(plugin.widgets)
