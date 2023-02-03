# -*- coding: utf-8 -*-
from os.path import dirname, join
from pkm import log
from pkm.qtemplate import QTemplateWidget


class SettingsWindow(QTemplateWidget):
    TMPL = join(dirname(__file__), 'settings.tmpl')

    def __init__(self, app):
        super(SettingsWindow, self).__init__()
        self.app = app

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
