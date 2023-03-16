# -*- coding: utf-8 -*-
from pkm import log
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt
from qtemplate import QTemplateWidget
from qtemplate.helpers.draggable import DraggableMixin


class DataSource:
    """ Base Data Source used to update data in the DataStore object. """
    
    def __init__(self, component):
        self.plugin = component.plugin                  # Plugin
        self.component = component                      # Plugin component
        self.app = QtCore.QCoreApplication.instance()   # QtCore application
        self.interval = 1000                            # Interval to update the data
        self.timer = None                               # QTimer used to update the data
        self.watchers = []                              # Desktop widgets watching this datasource

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


class DesktopWidget(DraggableMixin, QTemplateWidget):
    """ Base Desktop Widget used to display components on the Desktop. """
    DEFAULT_LAYOUT_MARGINS = (30,30,30,30)
    DEFAULT_LAYOUT_SPACING = 0

    def __init__(self, component):
        self.plugin = component.plugin                  # Plugin
        self.component = component                      # Plugin component
        self.app = QtCore.QCoreApplication.instance()   # QtCore application
        QTemplateWidget.__init__(self)                  # Init QTemplate
        DraggableMixin.__init__(self)                   # Init Draggable
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
        pos = self.component.getSetting('pos', (0,0))
        self.move(pos[0], pos[1])
    
    def _initRightclickMenu(self):
        """ Add right click context menu. """
        self.addAction(QtGui.QAction('Preferences', self, triggered=self.app.settings.show))
        self.addAction(QtGui.QAction('Quit', self, triggered=self.app.quit))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def widgetMoved(self, pos):
        """ Save the new location when the widget is moved. """
        self.component.saveSetting('pos', [pos.x(), pos.y()])


class SettingsWidget(QTemplateWidget):
    """ Base Settings Widget used to display plugin or components settings. """
    
    def __init__(self, component):
        self.plugin = component.plugin                  # Plugin
        self.component = component                      # Plugin component
        self.app = QtCore.QCoreApplication.instance()   # QtCore application
        QTemplateWidget.__init__(self)                  # Init QTemplate
        self.initSettings()                             # Init settings

    def initSettings(self):
        pass
    
    def getSetting(self, name, default=None):
        """ Get the specified settings value. """
        return self.component.getSetting(name, default)

    def getValue(self, name, default=None):
        """ Get the specified datastore value for this namespace. """
        return self.component.getValue(name, default)

    def saveSetting(self, name, value):
        """ Save the specified settings value to disk. """
        return self.component.saveSetting(name, value)

    def setValue(self, name, value):
        """ Set the spcified datastore value for this namespace. """
        return self.component.setValue(name, value)


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
