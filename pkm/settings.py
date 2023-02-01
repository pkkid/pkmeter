# -*- coding: utf-8 -*-
from pkm import APPNAME, APPDATA, log
from PySide2 import QtCore
from PySide2.QtCore import QSettings


class Settings(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._settings = QSettings(QSettings.IniFormat, QSettings.UserScope, APPNAME, APPNAME.lower())
        self._settings.setPath(QSettings.IniFormat, QSettings.UserScope, str(APPDATA))
        log.info(f'Settings location: {self._settings.fileName()}')
    
    # @QtCore.Property(str, constant=True)
    # def name(self):
    #     return "Hi Dad!"

    @QtCore.Property(type=list)
    def monitor_choices(self):
        choices = []
        for i, screen in enumerate(self.parent.app.screens()):
            choices.append({'value':0, 'text':f'#{i} ({screen.name()})'})
        return choices

    @QtCore.Property(type=list)
    def dock_choices(self):
        return ['Left', 'Right']
