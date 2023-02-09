# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import APPDATA, APPNAME, log, utils
from pkm.qtemplate import QTemplateWidget
from pkm.widgets import generalsettings
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QSettings, Qt

GENERAL = 'General'  # General settings pluginid
ICONBLANK = '󰄱'  # checkbox-blank-outline
ICONCHECK = '󰄵'  # checkbox-marked-outline


class SettingsWindow(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/tmpl/settings.tmpl')

    def __init__(self, app):
        super(SettingsWindow, self).__init__()
        self.app = app
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(f'{APPNAME} Settings')
        self.ids.titlebar.setTitle(f'{APPNAME} Settings')
        self._init_settings_storage()
        self._init_general_preferences()
    
    def show(self):
        """ Show this settings window. """
        self._init_plugins()
        utils.center_window(self)
        self._show_settings_content(GENERAL)
        super(SettingsWindow, self).show()
        
    def _init_settings_storage(self):
        """ Initialize the settings storage file. """
        self.storage = QSettings(QSettings.IniFormat, QSettings.UserScope, APPNAME, APPNAME.lower())
        self.storage.setPath(QSettings.IniFormat, QSettings.UserScope, str(APPDATA))
        log.info(f'Settings storage: {self.storage.fileName()}')

    def _init_general_preferences(self):
        """ Create the general settings widget. """
        widget = generalsettings.SettingsWidget(self.app)
        self._add_settings_content(GENERAL, widget)

    def _init_plugins(self):
        """ Initialize the plugins list and settings content. """
        pluginlist = self.ids.pluginlist
        pluginlist.clear()
        for plugin in self.app.plugins.values():
            item = QtWidgets.QListWidgetItem(f'{plugin.widget.NAME}')
            item.setData(Qt.UserRole, plugin.id)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setSizeHint(QtCore.QSize(80, 30))
            pluginlist.addItem(item)
            self._add_settings_content(plugin.id, plugin.settings)

    def _add_settings_content(self, pluginid, widget):
        """ Add settings content to the window. """
        widget.setObjectName(f'{pluginid}_settings')
        widget.layout().setContentsMargins(0,15,0,20)
        self.ids[widget.objectName()] = widget
        self.ids.content.layout().addWidget(widget)
        widget.hide()

    def _show_settings_content(self, pluginid):
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
                self._show_settings_content(pluginid)
    
    def generalSettingsClicked(self):
        """ Callback when the general settings button is clicked. """
        self._show_settings_content(GENERAL)

    def closeEvent(self, event):
        """ Close this settings window. """
        self.hide()
        event.ignore()

    # def __init__(self, parent=None):
    #     super().__init__(parent)
    #     self.parent = parent
    #     self._settings = QSettings(QSettings.IniFormat, QSettings.UserScope, APPNAME, APPNAME.lower())
    #     self._settings.setPath(QSettings.IniFormat, QSettings.UserScope, str(APPDATA))
    #     log.info(f'Settings location: {self._settings.fileName()}')
    
    # # @QtCore.Property(str, constant=True)
    # # def name(self):
    # #     return "Hi Dad!"
