# -*- coding: utf-8 -*-
from os.path import dirname, join
from pkm import APPNAME
from pkm import log, utils  # noqa
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt


class SettingsWindow(QTemplateWidget):
    TMPL = join(dirname(__file__), 'tmpl', 'settings.tmpl')
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
        
    def _init_pluginlist(self):
        pluginlist = self.ids.pluginlist
        pluginlist.clear()
        # pluginlist.dropEvent = self.reorder_plugins
        for name, plugin in self.app.plugins.items():
            item = QtWidgets.QListWidgetItem(name)
            item.setSizeHint(QtCore.QSize(80, 30))
            pluginlist.addItem(item)
    
    def pluginDropEvent(self, event):
        """ Reorder the plugins. """
        log.info('Reorder the plugins.')
        event.accept()

    def pluginMouseReleaseEvent(self, event):
        """ Display the selected plugin settings. """
        log.info('Display the selected plugin settings.')
        log.info(self.ids.pluginlist.selectedItems()[0].text())
        log.info(event)
        event.accept()
    
    def generalSettingsClicked(self):
        log.info('Display General Settings.')

    def show(self):
        """ Show this settings window. """
        self._init_pluginlist()
        utils.center_window(self)
        super(SettingsWindow, self).show()

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
