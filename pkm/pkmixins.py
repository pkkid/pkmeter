# -*- coding: utf-8 -*-
"""
PKMeter Mixins
"""
import json, pkm, re, time, urllib
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from pkm import log, utils
from pkm.decorators import threaded_method
from pkm.exceptions import ParseError
from pkm.template import Template, TruthTemplate, Variable
from xml.etree import ElementTree


class DraggableMixin(object):

    def __init__(self):
        self.mouseClickPos = None
        self.widgetClickPos = None

    def mousePressEvent(self, event):
        self.mouseclickpos = event.globalPos()
        self.widgetclickpos = self.pos()

    def mouseMoveEvent(self, event):
        if self.mouseclickpos:
            delta = event.globalPos() - self.mouseclickpos
            self.move(self.widgetclickpos + delta)

    def mouseReleaseEvent(self, event):
        self.mouseclickpos = None
        self.widgetclickpos = None


class LayoutMixin:
    _click = QtCore.pyqtSignal(object)
    _dblclick = QtCore.pyqtSignal(object)
    ATTRIBUTES = []

    def _init(self, etree, control, parent=None):
        self.etree = etree                          # Element tree to parse
        self.control = control                      # Control class (for callback connect)
        self.parent = parent                        # Parent widget
        self.id = None                              # ID of this widget (if specified)
        self.data = utils.Bunch()                   # Metadata to append to object
        self.actions = []                           # List of actions
        self.manifest = utils.Bunch()               # Dict of element ids
        self.bgimage = None                         # Background image
        self.bgpos = (0,0)                          # Background position 'x,y' or 'center,top' etc..
        self.bgsize = 'fit'                         # Background size 'x,y' or 'fit'
        self.bgfade = 0                             # Fade bgimage when changed (0 to disable)
        self.bgopacity = 1.0                        # Current bgopacity (used during transition)
        self.click_enabled = False                  # Set True when click event enabled
        self.dblclick_enabled = False               # Set True when dblclick event enabled
        self.installEventFilter(self)               # Capture events for interactions
        self._init_attributes()                     # Process all attributes (and actions)
        self.children = self._append_children()     # Build all Chiuldren
        if parent is not None:
            parent.layout().addWidget(self)

    def _init_attributes(self):
        for attr, value in self.etree.attrib.items():
            callback = getattr(self, 'attribute_%s' % attr)
            assert callback, 'Unsupported attribute: %s' % attr
            if attr == 'iter':
                self.actions.append(Variable(value, callback))
            elif attr == 'showif':
                self.actions.append(TruthTemplate(value, callback))
            elif re.findall(Template.REGEX, value):
                self.actions.append(Template(value, callback))
            else:
                callback(value)

    def _append_children(self):
        children = []
        for echild in self.etree:
            if echild.tag == 'stretch':
                self.layout().addStretch(int(echild.attrib.get('ratio', 1)))
                continue
            elif echild.tag == 'spacing':
                self.layout().addSpacing(int(echild.attrib.get('size', 1)))
                continue
            child = self._get_child_widget(echild, self.control)
            children.append(child)
            self.actions += child.actions
            self.manifest.update(child.manifest)
        return children

    def _get_child_widget(self, echild, control):
        childcls = pkm.pkwidgets.WIDGETS.get(echild.tag)
        if not childcls:
            qwidget = getattr(QtWidgets, echild.tag, None)
            childcls = pkm.pkwidgets.widget_factory(qwidget) if qwidget else None
        if not childcls:
            raise ParseError('Unknown element type: %s' % echild.tag)
        return childcls(echild, self.control, self)

    def _paint_frame(self, event):
        if self.bgimage:
            pixmap = self._build_pixmap(self.bgimage)
            # Check we need to resize the bgimage
            if self.bgsize:
                bgsize = self.bgsize
                if self.bgsize == 'fit':
                    bgsize = self.size()
                pixmap = pixmap.scaled(bgsize, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Calculate the x,y position
            x,y = self.bgpos
            if self.bgpos:
                if x == 'left': x = 0
                elif x == 'center': x = (self.width() / 2) - (pixmap.width() / 2)
                elif x == 'right': x = self.width() - pixmap.width()
                if y == 'top': y = 0
                elif y == 'center': y = (self.height() / 2) - (pixmap.height() / 2)
                elif y == 'bottom': y = self.height() - pixmap.height()
            # Draw the pixmap
            painter = QtGui.QPainter(self)
            painter.setOpacity(self.bgopacity)
            painter.drawPixmap(int(x), int(y), pixmap)

    def _build_pixmap(self, input):
        if isinstance(self.bgimage, bytes):
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(self.bgimage)
        else:
            pixmap = QtGui.QPixmap(self.bgimage)
        return pixmap

    def assert_widget(self, widgets, attr):
        if not any([isinstance(self, wt) for wt in widgets]):
            raise ParseError("Can not set attribute '%s' on widget %s" % (attr, self.__class__.__name__))

    @threaded_method
    def attribute_bgimage(self, value):
        # If http fetch and store image bytes,
        # otherwise store resource location string.
        if value.startswith('http'):
            log.debug('Opening URL: %s', value)
            response = urllib.request.urlopen(value)
            value = response.read()
        # Exit out if image hasnt changed
        if value == self.bgimage:
            return
        # Fade out (if self.bgfade set)
        if self.bgfade:
            framerate = self.bgfade / 40.0
            if self.bgimage:
                for i in range(100, -1, -5):
                    self.bgopacity = i * 0.01
                    self.update()
                    time.sleep(framerate)
            else:
                self.bgopacity = 0
                #self.update()
        # Set the new bgimage
        self.bgimage = value
        self.update()
        # Fade in (if self.bgfade set)
        if self.bgfade:
            for i in range(5, 101, 5):
                time.sleep(framerate)
                self.bgopacity = i * 0.01
                self.update()

    def attribute_bgpos(self, value):
        try:
            x,y = value.lower().split(',')
            x = x if x in ['left', 'center', 'right'] else int(x)
            y = y if y in ['top', 'center', 'bottom'] else int(y)
            self.bgpos = (x,y)
        except:
            log.exception('Invalid background position: %s', value)

    def attribute_bgsize(self, value):
        try:
            bgsize = value.lower()
            self.bgsize = bgsize if bgsize == 'fit' else QtCore.QSize(*map(int, bgsize.split(',')))
        except:
            log.exception('Invalid background size: %s', value)

    def attribute_bgfade(self, value):
        try:
            self.bgfade = float(value)
        except:
            log.exception('Invalid bgfade value: %s', value)

    def attribute_click(self, value):
        callback = utils.rget(self.control, value)
        if not callback:
            raise Exception('Invalid click callback: %s' % value)
        self.click_enabled = True
        self._click.connect(callback)

    def attribute_dblclick(self, value):
        callback = utils.rget(self.control, value)
        if not callback:
            raise Exception('Invalid dblclick callback: %s' % value)
        self.dblclick_enabled = True
        self._dblclick.connect(callback)

    def attribute_data(self, value):
        self.data.update(json.loads(value))

    def attribute_id(self, value):
        self.id = value
        self.manifest[value] = self

    def attribute_name(self, value):
        self.setObjectName(value)

    def attribute_style(self, value):
        return self.setStyleSheet(value)

    def attribute_tooltip(self, value):
        tooltip = []
        for line in value.split('\\n'):
            line = line.replace('{', '<').replace('}', '>')
            tooltip.append(line.strip())
        self.setToolTip('\n'.join(tooltip))
        self.setToolTipDuration(60000)

    def attribute_echo(self, value):
        self.assert_widget([QtWidgets.QLineEdit], 'echo')
        modes = {
            'normal': QtWidgets.QLineEdit.Normal,
            'noecho': QtWidgets.QLineEdit.NoEcho,
            'password': QtWidgets.QLineEdit.Password,
            'passwordechoonedit': QtWidgets.QLineEdit.PasswordEchoOnEdit,
        }
        if value not in modes:
            raise ParseError('Unknown echo mode: %s' % value)
        self.setEchoMode(modes[value.lower()])

    def eventFilter(self, widget, event):
        if self.click_enabled and event.type() == QtCore.QEvent.MouseButtonPress and event.button() == 1:
            self._click.emit(self)
            return True
        elif self.dblclick_enabled and event.type() == QtCore.QEvent.MouseButtonDblClick and event.button() == 1:
            self._dblclick.emit(self)
            return True
        return QtWidgets.QWidget.eventFilter(self, widget, event)


class StashMixin:
    """ Mixin to stash contents asside for loops or if statements. """
    ATTRS = ['iter', 'showif']

    def _init(self):
        self.itermax = None
        self.subtree = None
        self.subwidgets = []

    def _append_children(self):
        if not any([self.etree.attrib.get(attr) for attr in self.ATTRS]):
            return LayoutMixin._append_children(self)
        # Build the subtree Element
        self.subtree = ElementTree.Element('hframe')
        self.subtree.set('name', 'IterItem')
        for echild in self.etree:
            self.subtree.append(echild)
        # Build the child for if statements
        if self.etree.attrib.get('showif'):
            subwidget = self._build_subwidget('ShowIf')
            self.actions += subwidget.actions
            self.layout().takeAt(0).widget()

    def attribute_showif(self, data, value):
        if value and not self.layout().count():
            self.layout().addWidget(self.subwidgets[0])
        elif not value and self.layout().count():
            self.layout().takeAt(0).widget()
            timer = QtCore.QTimer()
            timer.singleShot(10, self.control.resize_to_min)

    def attribute_itermax(self, value):
        self.itermax = int(value)

    def attribute_iter(self, data, value):
        count = 0
        length = len(value) if value else 0
        for i in range(length):
            count += 1
            subwidget = self._get_subwidget(i)
            data['this'] = value[i]
            for action in subwidget.actions:
                action.apply(data)
            if self.itermax and i >= self.itermax-1:
                break
        for subwidget in self.subwidgets[count:]:
            utils.remove_widget(subwidget)
        self.subwidgets = self.subwidgets[:count]
        timer = QtCore.QTimer()
        timer.singleShot(10, self.control.resize_to_min)

    def _get_subwidget(self, index):
        if index < len(self.subwidgets):
            return self.subwidgets[index]
        return self._build_subwidget('IterItem')

    def _build_subwidget(self, name):
        PKHFrame = pkm.pkwidgets.PKHFrame
        PKVFrame = pkm.pkwidgets.PKVFrame
        widgetcls = PKHFrame if isinstance(self, PKHFrame) else PKVFrame
        subwidget = widgetcls(self.subtree, self.control, self)
        subwidget.setObjectName(name)
        self.subwidgets.append(subwidget)
        self.layout().addWidget(subwidget)
        return subwidget
