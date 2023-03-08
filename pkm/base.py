# -*- coding: utf-8 -*-
from pkm import log, utils
from pkm.mixins import Draggable
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt
from functools import cached_property


class DataSource:
    """ Base Data Source used to update data in the DataStore object. """
    NAMESPACE = None
    
    def __init__(self, component):
        super(DataSource, self).__init__()
        self.plugin = component.plugin                  # Plugin
        self.component = component                      # Plugin component
        self.app = QtCore.QCoreApplication.instance()   # QtCore application
        self.interval = 1000                            # Interval to update the data
        self.timer = None                               # QTimer used to update the data
        self.watchers = []                              # Desktop widgets watching this datasource
    
    @cached_property
    def namespace(self):
        """ Get the namespace for this DataSource. By default this is
            {pluginid}.{componentid}, but can be overridden by specifying
            self.NAMESPACE. You should only really override the namespace if
            this datasource is more generally useful outside your plugin.
        """
        if self.NAMESPACE:
            return f'{self.NAMESPACE}'
        return f'{self.plugin.id}.{self.component.namespace}'

    def start(self):
        """ Start the update timer. """
        if self.timer is None:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update)
            self.update()
        log.info(f'Starting {self.component.id} datasource with interval {self.interval}ms')
        self.timer.start(self.interval)

    def stop(self):
        """ Stop the update timer. """
        self.timer.stop()

    def update(self):
        """ Update DataSource values. """
        log.warning(f'{self.plugin.id} timer running with no update() function.')


class DesktopWidget(Draggable, QTemplateWidget):
    """ Base Desktop Widget used to display components on the Desktop. """
    DEFAULT_LAYOUT_MARGINS = (30,30,30,30)
    DEFAULT_LAYOUT_SPACING = 0

    def __init__(self, component):
        QTemplateWidget.__init__(self)
        Draggable.__init__(self)
        self.plugin = component.plugin                  # Plugin
        self.component = component                      # Plugin component
        self.app = QtCore.QCoreApplication.instance()   # QtCore application
        self._initWidget()                              # Set window properties
        self._initRightclickMenu()                      # Create right click menu
        
    def _initWidget(self):
        """ Initialize this DesktopWidget. Currently this makes sure the window
            is frameless and set to have a tansparent background. It will also
            position the widget to the last moved location.
        """
        # Set some object attributes
        self.setProperty('class', 'widget')
        self.setProperty('plugin', self.component.plugin.id)
        self.setProperty('component', self.component.id)
        self.setObjectName(self.component.id)
        # Set the QT window flags
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        # Set the window position
        pos = [int(x) for x in self.component.getSetting('pos', '0,0').split(',')]
        self.move(pos[0], pos[1])
    
    def _initRightclickMenu(self):
        """ All DesktopWidgets should have a right click context menu to open
            settings or quit the app.
        """
        self.addAction(QtGui.QAction('Preferences', self, triggered=self.app.settings.show))
        self.addAction(QtGui.QAction('Quit', self, triggered=self.app.quit))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
    
    def widgetMoved(self, pos):
        """ Save the new location when the widget is moved. """
        self.component.saveSetting('pos', f'{pos.x()},{pos.y()}')


class SettingsWidget(QTemplateWidget):
    """ Base Settings Widget used to display plugin or components settings. """
    
    def __init__(self, component):
        super(SettingsWidget, self).__init__()
        self.plugin = component.plugin                  # Plugin
        self.component = component                      # Plugin component
        self.app = QtCore.QCoreApplication.instance()   # QtCore application


class QTemplateTag:
    """ Base QTemplateWidget Tags used to modify the parent QWidget in but does
        not represent a QWidget itself. This allows a plugin developer to extend
        the capacilities of the qtemplate parser.
    """

    def __init__(self, qtmpl, elem, parent, context, *args):
        self.qtmpl = qtmpl          # Ref to parent QTemplateWidget object
        self.elem = elem            # Current etree item to render children
        self.parent = parent        # Parent qobj to add children to
        self.context = context      # Context for building the children
