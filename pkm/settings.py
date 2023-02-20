# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import CONFIG_STORAGE, log, utils
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt

GENERALSETTINGS = 'default.generalsettings'


class SettingsWindow(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/tmpl/settings.tmpl')

    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.app = QtCore.QCoreApplication.instance()
        self.storage = CONFIG_STORAGE
    
    def show(self):
        """ Show this settings window. """
        self._initPlugins()
        utils.centerWindow(self)
        self._swapContent(GENERALSETTINGS)
        super(SettingsWindow, self).show()

    def _initPlugins(self):
        """ Initialize the plugins list and settings content. """
        pluginlist = self.ids.pluginlist
        pluginlist.clear()
        for plugin in self.app.plugins.values():
            self._addSettingsContent(plugin.id, plugin.settings)
            if plugin.id != GENERALSETTINGS:
                item = QtWidgets.QListWidgetItem(f'{plugin.name}')
                item.setData(Qt.UserRole, plugin.id)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                item.setSizeHint(QtCore.QSize(80, 30))
                pluginlist.addItem(item)

    def _addSettingsContent(self, pluginid, widget):
        """ Add settings content to the window. """
        widget.setObjectName(f'{pluginid}_settings')
        widget.layout().setContentsMargins(0,15,0,20)
        self.ids[widget.objectName()] = widget
        self.ids.content.layout().addWidget(widget)
        widget.hide()

    def _swapContent(self, pluginid):
        """ Show the specified settings content. """
        # Hide all currently displayed settings
        layout = self.ids.content.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            item.widget().setVisible(False)
        utils.setPropertyAndRedraw(self.ids.generalbtn, 'class', '')
        # Display the newly selected plugin settings
        title = f'{self.app.plugins[pluginid].name} Settings'
        self.ids.plugintitle.setText(title)
        self.ids[f'{pluginid}_settings'].setVisible(True)
        # If the pluginid is general settings, delselect all items in the
        # QListWidget and set the button to be highlighted
        if pluginid == GENERALSETTINGS:
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
                self._swapContent(pluginid)
    
    def generalSettingsClicked(self):
        """ Callback when the general settings button is clicked. """
        self._swapContent(GENERALSETTINGS)

    def closeEvent(self, event):
        """ Close this settings window. """
        self.hide()
        event.ignore()
