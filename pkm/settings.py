# -*- coding: utf-8 -*-
import os
from pkm import APPNAME, log, utils  # noqa
from pkm.qtemplate import QTemplateWidget
from pkm.widgets import generalsettings
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt

GENERAL = 'general'  # General settings pluginid


class SettingsWindow(QTemplateWidget):
    TMPL = os.path.join(os.path.dirname(__file__), 'tmpl', 'settings.tmpl')
    # We need a custom signal for the dropEvent
    # https://stackoverflow.com/a/62986558
    _dropEventSignal = QtCore.Signal()

    def __init__(self, app):
        super(SettingsWindow, self).__init__()
        self.app = app
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(f'{APPNAME} Settings')
        self.ids.titlebar.setTitle(f'{APPNAME} Settings')
        self._init_general_settings()
    
    def show(self):
        """ Show this settings window. """
        self._init_plugins()
        utils.center_window(self)
        super(SettingsWindow, self).show()
        
    def _init_general_settings(self):
        """ Create the general settings widget. """
        settings = generalsettings.SettingsWidget(self.app)
        settings.setObjectName(f'{GENERAL}_settings')
        self.ids[settings.objectName()] = settings
        self.ids.contents.layout().addWidget(settings)

    def _init_plugins(self):
        """ Initialize the plugins list and settings content. """
        pluginlist = self.ids.pluginlist
        pluginlist.clear()
        for plugin in self.app.plugins:
            item = QtWidgets.QListWidgetItem(plugin.widget.NAME)
            item.setData(Qt.UserRole, plugin.id)
            item.setSizeHint(QtCore.QSize(80, 30))
            pluginlist.addItem(item)
            self.ids[plugin.settings.objectName()] = plugin.settings
            self.ids.contents.layout().addWidget(plugin.settings)

    def _show_settings_content(self, pluginid):
        """ Show the specified settings content. """
        # Hide all currently displayed settings
        layout = self.ids.contents.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            item.widget().setVisible(False)
        # Display the newly selected plugin settings
        self.ids[f'{pluginid}_settings'].setVisible(True)
        # If the pluginid is general, delselect all items in the
        # QListWidget and set the button to be highlighted
        if pluginid == GENERAL:
            self.ids.pluginlist.clearSelection()
            utils.setPropertyAndRedraw(self.ids.generalbtn, 'class', 'selected')
        else:
            utils.setPropertyAndRedraw(self.ids.generalbtn, 'class', '')
        log.info(self.ids.generalbtn.property('class'))

    def pluginDropEvent(self, event):
        """ Reorder the plugins. """
        log.info('Reorder the plugins.')
        event.accept()

    def pluginMouseReleaseEvent(self, event):
        """ Callback when a plugin listitem is clicked. """
        items = self.ids.pluginlist.selectedItems()
        if len(items):
            item = self.ids.pluginlist.selectedItems()[0]
            pluginid = item.data(Qt.UserRole)
            self._show_settings_content(pluginid)
            event.accept()
    
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

    # @QtCore.Property(type=list)
    # def monitor_choices(self):
    #     choices = []
    #     for i, screen in enumerate(self.parent.app.screens()):
    #         choices.append({'value':0, 'text':f'#{i} ({screen.name()})'})
    #     return choices

    # @QtCore.Property(type=list)
    # def dock_choices(self):
    #     return ['Left', 'Right']
