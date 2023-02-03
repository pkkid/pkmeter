# -*- coding: utf-8 -*-
from os.path import dirname, join
from pkm import APPNAME
from pkm import log, utils
from pkm.qtemplate import QTemplateWidget
from PySide6.QtCore import Qt


class SettingsWindow(QTemplateWidget):
    TMPL = join(dirname(__file__), 'settings.tmpl')

    def __init__(self, app):
        super(SettingsWindow, self).__init__()
        self.app = app
        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(f'{APPNAME} Settings')
    
    def show(self):
        super(SettingsWindow, self).show()
        utils.center_window(self)
    
    def show_tab(self, index):
        if index < 0: return
        for i in range(self.ids.tabbar.count()):
            if i != index:
                tabtext = self.ids.tabbar.tabText(i)
                self.ids[tabtext.lower()].hide()
        tabtext = self.ids.tabbar.tabText(index)
        self.ids[tabtext.lower()].show()
    
    def close(self):
        self.hide()

    def closeEvent(self, event):
        self.close()
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
