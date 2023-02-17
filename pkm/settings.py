# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import APPDATA, APPNAME, log, utils
from pkm.qtemplate import QTemplateWidget
from pkm.widgets import gensettings
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QCoreApplication, QSettings, Qt

GENERAL = 'General'  # General settings pluginid


class SettingsWindow(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/tmpl/settings.tmpl')

    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.app = QCoreApplication.instance()
        self._initStorage()
        self._initGeneralSettings()
    
    def show(self):
        """ Show this settings window. """
        self._initPlugins()
        utils.centerWindow(self)
        self._swapContent(GENERAL)
        super(SettingsWindow, self).show()
        
    def _initStorage(self):
        """ Initialize the settings storage file. """
        self.storage = QSettings(QSettings.IniFormat, QSettings.UserScope, APPNAME, APPNAME.lower())
        self.storage.setPath(QSettings.IniFormat, QSettings.UserScope, str(APPDATA))
        log.info(f'Settings storage: {self.storage.fileName()}')

    def _initGeneralSettings(self):
        """ Create the general settings widget. """
        widget = gensettings.SettingsWidget()
        self._addSettingsContent(GENERAL, widget)

    def _initPlugins(self):
        """ Initialize the plugins list and settings content. """
        pluginlist = self.ids.pluginlist
        pluginlist.clear()
        for plugin in self.app.plugins.values():
            item = QtWidgets.QListWidgetItem(f'{plugin.name}')
            item.setData(Qt.UserRole, plugin.id)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setSizeHint(QtCore.QSize(80, 30))
            pluginlist.addItem(item)
            self._addSettingsContent(plugin.id, plugin.settings)

    def _addSettingsContent(self, pluginid, widget):
        """ Add settings content to the window. """
        widget.setObjectName(f'{pluginid}_settings')
        widget.layout().setContentsMargins(0,15,0,20)
        self.ids[widget.objectName()] = widget
        self.ids.content.layout().addWidget(widget)
        widget.hide()

    def _swapContent(self, pluginid):
        """ Show the specified settings content. """
        # Hide all currently displayed settings
        layout = self.ids.content.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            item.widget().setVisible(False)
        utils.setPropertyAndRedraw(self.ids.generalbtn, 'class', '')
        # Display the newly selected plugin settings
        title = f'{GENERAL} Settings'
        if pluginid in self.app.plugins:
            title = f'{self.app.plugins[pluginid].name} Settings'
        self.ids.plugintitle.setText(title)
        self.ids[f'{pluginid}_settings'].setVisible(True)
        # If the pluginid is general, delselect all items in the
        # QListWidget and set the button to be highlighted
        if pluginid == GENERAL:
            self.ids.pluginlist.clearSelection()
            utils.setPropertyAndRedraw(self.ids.generalbtn, 'class', 'selected')

    def pluginDropEvent(self, event):
        """ Reorder the plugins. """
        log.info('Reorder the plugins.')
        event.accept()

    def pluginMouseReleaseEvent(self, event):
        """ Callback when a plugin listitem is clicked. """
        items = self.ids.pluginlist.selectedItems()
        if len(items):
            if event.pos().x() <= 22:
                # Click was inside the checkmark, toggle the plugin
                pass
            else:
                # Click was outside the checkmark, select the item
                item = self.ids.pluginlist.selectedItems()[0]
                pluginid = item.data(Qt.UserRole)
                self._swapContent(pluginid)
    
    def generalSettingsClicked(self):
        """ Callback when the general settings button is clicked. """
        self._swapContent(GENERAL)

    def closeEvent(self, event):
        """ Close this settings window. """
        self.hide()
        event.ignore()
        self.app.quit()  # TODO: REMOVE
