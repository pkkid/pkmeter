# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import CONFIG_STORAGE, log, utils
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt


class SettingsWindow(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/tmpl/settings.tmpl')

    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.app = QtCore.QCoreApplication.instance()
        self.appsettings = self.ids.appsettings
        self.storage = CONFIG_STORAGE
    
    def closeEvent(self, event):
        """ Close this settings window. """
        self.hide()
        event.ignore()
    
    def generalSettingsClicked(self):
        """ Callback when the general settings button is clicked. """
        pass
        # self._swapContent(GENERALSETTINGS)

    def show(self):
        """ Show this settings window. """
        self.updateComponentList('default')
        utils.centerWindow(self)
        # self.updateContent(GENERALSETTINGS)
        super(SettingsWindow, self).show()

    def updateComponentList(self, pluginid=None):
        if self._loading: return
        self.ids.componentlist.clear()
        if str(pluginid) not in self.app.plugins:
            pluginid = self.ids.pluginlist.currentData()
        for component in self.app.plugins[pluginid].components.values():
            item = QtWidgets.QListWidgetItem(f'{component.name}')
            item.setData(Qt.UserRole, component.varname)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            if component.widget is not None:
                item.setCheckState(Qt.Checked)
            item.setSizeHint(QtCore.QSize(80, 30))
            self.ids.componentlist.addItem(item)
    
    def updateContent(self, pluginid=None, componentid=None):
        if self._loading: return
        if str(pluginid) not in self.app.plugins:
            pluginid = self.ids.pluginlist.currentData()
        if str(componentid) not in self.app.plugins[pluginid].components:
            item = self.ids.componentlist.currentItem()
            componentid = item.data(Qt.UserRole)
        # Hide currently displayed settings
        content = self.ids.content
        utils.removeChildren(content)
        # Insert the new component settings
        plugin = self.app.plugins[pluginid]
        component = plugin.components[componentid]
        if component.settings is not None:
            content.layout().addWidget(component.settings)
            component.settings.setVisible(True)
        self.ids.content.update()

    # def _swapContent(self, pluginid):
    #     """ Show the specified settings content. """
    #     # Hide all currently displayed settings
    #     layout = self.ids.content.layout()
    #     for i in range(layout.count()):
    #         item = layout.itemAt(i)
    #         item.widget().setVisible(False)
    #     utils.setPropertyAndRedraw(self.ids.generalbtn, 'class', '')
    #     # Display the newly selected plugin settings
    #     title = f'{self.app.plugins[pluginid].name} Settings'
    #     self.ids.plugintitle.setText(title)
    #     self.ids[f'{pluginid}_settings'].setVisible(True)
    #     # If the pluginid is general settings, delselect all items in the
    #     # QListWidget and set the button to be highlighted
    #     if pluginid == GENERALSETTINGS:
    #         self.ids.pluginlist.clearSelection()
    #         utils.setPropertyAndRedraw(self.ids.generalbtn, 'class', 'selected')

    # def _addSettingsContent(self, pluginid, widget):
    #     """ Add settings content to the window. """
    #     widget.setObjectName(f'{pluginid}_settings')
    #     widget.layout().setContentsMargins(0,15,0,20)
    #     self.ids[widget.objectName()] = widget
    #     self.ids.content.layout().addWidget(widget)
    #     widget.hide()
