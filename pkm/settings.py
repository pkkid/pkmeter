# -*- coding: utf-8 -*-
from os.path import dirname, join
from pkm import APPNAME
from pkm import log, utils
from pkm.qtemplate import QTemplateWidget
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem


class SettingsWindow(QTemplateWidget):
    TMPL = join(dirname(__file__), 'tmpl', 'settings.tmpl')

    def __init__(self, app):
        super(SettingsWindow, self).__init__()
        self.app = app
        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(f'{APPNAME} Settings')
    
    def toggle_listwidget(self):
        listname = self.sender().property('toggle')
        qlist = self.ids[listname]
        currentlyexpanded = True  # qlist.maximumHeight > 0
        log.info(listname)
        if currentlyexpanded:
            qlist.setMaximumHeight(0)
        else:
            qlist.setMaximumHeight(999)

    def show(self):
        super(SettingsWindow, self).show()
        utils.center_window(self)
    
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


# from PySide6.QtWidgets import *
# # Create a list widget with 3 different expandable sections, each with 3 list items inside
# mylist = QListWidget()
# item = QListWidgetItem('Section 1', mylist)
# # Call setExpandable on the item
# item.setExpandable(True)
# # Create child 1
# child1 = QListWidgetItem('Value 1', mylist)
# # Set the parent of child 1 to item
# child1.setParent(item)
# # Create child 2
# child2 = QListWidgetItem('Value 2', mylist)
# # Set parent of child 2 to item
# child2.setParent(item)
# # Create child 3
# child3 = QListWidgetItem('Value 3', mylist
# # Set the parent of child 3 to item
# child3.setParent(item)
 
# # Create a second list item
# item2 = QListWidgetItem('Section 2', mylist)
# # Call setExpandable on the item
# item2.setExpandable(True)
# # Create child 4
# child4 = QListWidgetItem('Value 4', mylist)
# # Set the parent of child 4 to item2
# child4.setParent(item2)
# # Create child 5
# child5 = QListWidgetItem('Value 5', mylist)
# # Set the parent of child 5 to item2
# child5.setParent(item2)
# # Create child 6
# child6 = QListWidgetItem('Value 6', mylist)
# # Set the parent of child 6 to item2
# child6.setParent(item2)
 
# # Create a third list item
# item3 = QListWidgetItem('Section 3', mylist)
# # Call setExpandable on the item
# item3.setExpandable(True)
# # Create child 7
# child7 = QListWidgetItem('Value 7', mylist)
# # Set the parent of child 7 to item3
# child7.setParent(item3)
# # Create child 8
# child8 = QListWidgetItem('Value 8', mylist)
# # Set the parent of child 8 to item2
# child8.setParent(item3)
# # Create child 9
# child9 = QListWidgetItem('Value 9', mylist)
# # Set the parent of child 9 to item3
# child9.setParent(item3)
 
# # Show the list
# mylist.show()

