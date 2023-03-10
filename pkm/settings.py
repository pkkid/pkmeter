# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import log, utils  # noqa
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt


class SettingsWindow(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/settings.tmpl')

    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.app = QtCore.QCoreApplication.instance()
        self.appsettings = self.ids.appsettings
        self._initDataTable()
    
    def _initDataTable(self):
        # Configure the datatable options
        self.ids.datatable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ids.datatable.setHorizontalHeaderLabels(['Variable', 'Value', 'Type   '])
        self.ids.datatable.horizontalHeader().resizeSection(0, 170)
        self.ids.datatable.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.ids.datatable.horizontalHeader().setHighlightSections(False)
        self.ids.datatable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        self.ids.datatable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.ids.datatable.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.ids.datatable.verticalHeader().setVisible(False)
        self.ids.datatable.verticalHeader().setDefaultSectionSize(19)
        self.ids.datatable.setWordWrap(False)
        # Create the datatable update timer
        self.dataTableTimer = QtCore.QTimer()
        self.dataTableTimer.timeout.connect(self.updateDataTable)
        self.dataTableTimer.start(1000)

    def close(self, event):
        """ Close this settings window. """
        self.hide()
    
    def show(self):
        """ Show this settings window. """
        self.updateComponentList(None)
        utils.centerWindow(self)
        super(SettingsWindow, self).show()

    def settingsButtonClicked(self):
        componentid = self.sender().objectName()[:-3]
        self.updateContent(componentid)

    def componentSelected(self, item):
        componentid = item.data(Qt.UserRole)
        pluginid = self.ids.pluginlist.currentData()
        self.updateContent(componentid, pluginid)

    def updateComponentList(self, pluginid):
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
    
    def updateContent(self, componentid, pluginid=None):
        if self._loading: return
        # Remove Highlight on all sidepanel items
        utils.setPropertyAndRedraw(self.ids.appsettingsbtn, 'class', '')
        utils.setPropertyAndRedraw(self.ids.datastorebtn, 'class', '')
        utils.setPropertyAndRedraw(self.ids.pluginlist, 'class', '')
        utils.removeChildren(self.ids.content)
        # Highlight the new sidepanel item and show updated settings
        if pluginid:
            plugin = self.app.plugins[pluginid]
            component = plugin.components[componentid]
            settings = component.settings
            button = self.ids.pluginlist
            title = f'{plugin.name} {component.name.replace(" Settings","")} Settings'
        else:
            settings = self.ids[componentid]
            button = self.ids[f'{componentid}btn']
            title = settings.property('title')
            self.ids.componentlist.clearSelection()
        utils.setPropertyAndRedraw(button, 'class', 'selected')
        self.ids.contentheader.setText(title)
        self.ids.content.layout().addWidget(settings)
        settings.setVisible(True)
        self.ids.content.update()
    
    def updateDataTable(self):
        if not self.ids.datastore.isVisible(): return
        metrics = self.app.data.listMetrics()
        self.ids.datatable.setRowCount(len(metrics))
        for row in range(len(metrics)):
            for col in range(3):
                item = QtWidgets.QTableWidgetItem(metrics[row][col], 0)
                self.ids.datatable.setItem(row, col, item)
