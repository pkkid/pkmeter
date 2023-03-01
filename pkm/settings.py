# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import CONFIG_STORAGE
from pkm import log, utils  # noqa
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt


class SettingsWindow(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/tmpl/settings.tmpl')

    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.app = QtCore.QCoreApplication.instance()
        self.appsettings = self.ids.appsettings
        self.storage = CONFIG_STORAGE
        # Add Shadow to contentwrap
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setColor(QtGui.QColor(0, 0, 0, 127))
        shadow.setBlurRadius(8)
        shadow.setOffset(-5, 0)
        self.ids.contentwrap.setGraphicsEffect(shadow)
    
    def close(self, event):
        """ Close this settings window. """
        self.hide()
    
    def show(self):
        """ Show this settings window. """
        self.updateComponentList('default')
        utils.centerWindow(self)
        super(SettingsWindow, self).show()
    
    def showAppSettings(self):
        """ Callback when Application Settings is clicked. """
        self.updateContent()

    def updateComponentList(self, pluginid=None):
        if self._loading: return
        self.ids.componentlist.clear()
        if str(pluginid) not in self.app.plugins:
            pluginid = self.ids.pluginlist.currentData()
        for component in self.app.plugins[pluginid].components.values():
            item = QtWidgets.QListWidgetItem(f'{component.name}')
            item.setData(Qt.UserRole, component.id)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setSizeHint(QtCore.QSize(80, 30))
            if component.widget is not None:
                item.setCheckState(Qt.Checked)
            self.ids.componentlist.addItem(item)
    
    def updateContent(self, item=None):
        if self._loading: return
        # Figure out which settings to display and update appsettingsbtn
        settings = self.ids.appsettings
        if item is not None:
            pid = self.ids.pluginlist.currentData() if item else None
            cid = item.data(Qt.UserRole) if item else None
            plugin = self.app.plugins[pid]
            component = self.app.plugins[pid].components[cid]
            settings = component.settings
            utils.setPropertyAndRedraw(self.ids.appsettingsbtn, 'class', '')
            title = f'{plugin.name} {component.name.replace(" Settings","")}'
            title += ' Settings' if 'Settings' not in title else ''
            self.ids.contentheader.setText(title)
        else:
            self.ids.componentlist.clearSelection()
            self.ids.contentheader.setText('Application Settings')
            utils.setPropertyAndRedraw(self.ids.appsettingsbtn, 'class', 'selected')
        # Hide current settings and show the new ones
        utils.removeChildren(self.ids.content)
        if settings is not None:
            self.ids.content.layout().addWidget(settings)
            settings.setVisible(True)
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
