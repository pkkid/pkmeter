# -*- coding: utf-8 -*-
"""
PKMeter Widgets
"""
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from pkm import pkcharts, pkmixins, utils
from pkm.decorators import threaded_method

WIDGETS = {
    'widget': lambda *args: PKWidget(*args),
    'hframe': lambda *args: PKHFrame(*args),
    'label': lambda *args: PKLabel(*args),
    'linechart': lambda *args: pkcharts.PKLineChart(*args),
    'piechart': lambda *args: pkcharts.PKPieChart(*args),
    'pushbutton': lambda *args: PKPushButton(*args),
    'textedit': lambda *args: PKTextEdit(*args),
    'toggleswitch': lambda *args: PKToggleSwitch(*args),
    'vbarchart': lambda *args: pkcharts.PKVBarChart(*args),
    'vframe': lambda *args: PKVFrame(*args),
}


class PKWidget(QtWidgets.QWidget, pkmixins.LayoutMixin):

    def __init__(self, etree, control, parent=None):
        QtWidgets.QWidget.__init__(self)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.initsize = None
        pkmixins.LayoutMixin._init(self, etree, control, parent)

    def attribute_size(self, value):
        values = [int(x) for x in value.split(',')]
        self.setFixedSize(*values)

    def attribute_initsize(self, value):
        self.initsize = [int(x) for x in value.split(',')]
        self.resize(*self.initsize)


class PKDeskWidget(PKWidget, pkmixins.DraggableMixin):

    def __init__(self, etree, style, pkmeter, parent=None):
        PKWidget.__init__(self, etree, pkmeter, parent)
        self.pkmeter = pkmeter
        self.setStyleSheet(style)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint |
            Qt.NoDropShadowWindowHint |
            Qt.CustomizeWindowHint)
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self._init_menu()
        pkmixins.DraggableMixin.__init__(self)

    def _init_menu(self):
        self.addAction(QtWidgets.QAction('About PKMeter', self, triggered=self.pkmeter.about.show))
        self.addAction(QtWidgets.QAction('Preferences', self, triggered=self.pkmeter.config.show))
        self.addAction(QtWidgets.QAction('Quit', self, triggered=self.pkmeter.quit))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def position(self):
        return '%s,%s' % (self.x(), self.y())

    def setPosition(self, position):
        self.move(*[int(x) for x in position.split(',')])

    def show(self):
        self.setWindowOpacity(0)
        self.fade_in()
        return super(PKDeskWidget, self).show()

    @threaded_method
    def fade_in(self):
        time.sleep(1)
        for i in range(0, 101, 5):
            self.setWindowOpacity(i * 0.01)
            self.update()
            time.sleep(0.02)


class PKHFrame(QtWidgets.QFrame, pkmixins.StashMixin, pkmixins.LayoutMixin):

    def __init__(self, etree, control, parent=None):
        QtWidgets.QFrame.__init__(self)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        pkmixins.StashMixin._init(self)
        pkmixins.LayoutMixin._init(self, etree, control, parent)

    def paintEvent(self, event):
        QtWidgets.QFrame.paintEvent(self, event)
        return self._paint_frame(event)


class PKLabel(QtWidgets.QLabel, pkmixins.LayoutMixin):
    ALIGN = {'left':Qt.AlignLeft, 'right':Qt.AlignRight, 'center':Qt.AlignHCenter}

    def __init__(self, etree, control, parent=None):
        QtWidgets.QLabel.__init__(self)
        pkmixins.LayoutMixin._init(self, etree, control, parent)

    def attribute_text(self, value):
        self.setText(value)

    def attribute_align(self, value):
        self.setAlignment(self.ALIGN[value.lower()])

    def attribute_wrap(self, value):
        self.setWordWrap(value.lower() in ['true','t','1'])


class PKPushButton(QtWidgets.QPushButton, pkmixins.LayoutMixin):
    DEFAULT_COLOR = '#ffffff'  # For color buttons

    def __init__(self, etree, control, parent=None):
        QtWidgets.QPushButton.__init__(self)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        pkmixins.LayoutMixin._init(self, etree, control, parent)

    def attribute_text(self, value):
        self.setText(value)

    def get_value(self):
        if self.data.color:
            return self.data.color
        return self.text()

    def set_value(self, value):
        if self.data.color:
            self.data.color = value or self.DEFAULT_COLOR
            style = 'background-color: %s;' % self.data.color
            return self.layout().itemAt(0).widget().setStyleSheet(style)
        return self.setText(value)


class PKTextEdit(QtWidgets.QTextEdit, pkmixins.LayoutMixin):
    """ QTextEdit that sends editingFinished event when text changed and focus lost.
        https://gist.github.com/hahastudio/4345418
    """
    editingFinished = QtCore.pyqtSignal()

    def __init__(self, etree, control, parent=None):
        QtWidgets.QTextEdit.__init__(self)
        self._changed = False
        self.setTabChangesFocus(True)
        self.textChanged.connect(self._handle_text_changed)
        pkmixins.LayoutMixin._init(self, etree, control, parent)

    def _handle_text_changed(self):
        self._changed = True

    def focusOutEvent(self, event):
        if self._changed:
            self.editingFinished.emit()
        super(PKTextEdit, self).focusOutEvent(event)

    def get_value(self):
        return self.toPlainText()

    def setTextChanged(self, state=True):
        self._changed = state

    def setHtml(self, html):
        QtWidgets.QTextEdit.setHtml(self, html)
        self._changed = False

    def setText(self, text):
        QtWidgets.QTextEdit.setText(self, text)
        self._changed = False

    def set_value(self, value):
        return self.setText(value)


class PKToggleSwitch(QtWidgets.QFrame, pkmixins.LayoutMixin):
    editingFinished = QtCore.pyqtSignal(name='editingFinished')

    def __init__(self, etree, control, parent=None):
        QtWidgets.QPushButton.__init__(self)
        self.enabled = False                                # Holds switch state
        self.bgcolor_slider = utils.window_bgcolor()        # Background color of the slider
        pkmixins.LayoutMixin._init(self, etree, control, parent)

    def mouseReleaseEvent(self, event):
        self.set_value(not self.get_value())
        self.editingFinished.emit()

    def paintEvent(self, event):
        QtWidgets.QFrame.paintEvent(self, event)
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        if self.enabled: self.paint_slider_on(painter)
        else: self.paint_slider_off(painter)
        painter.end()

    def paint_slider_on(self, painter):
        swidth = int((self.width() / 2) - 2)
        sheight = int(self.height() - 2)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(60,90,150,200)))
        painter.drawRoundedRect(self.contentsRect(), 3, 3)
        painter.setBrush(QtGui.QBrush(self.bgcolor_slider))
        painter.drawRoundedRect(swidth+3, 1, swidth, sheight, 2, 2)
        painter.setPen(QtGui.QColor(255,255,255,220))
        painter.drawText(2, 1, swidth, sheight, Qt.AlignCenter | Qt.AlignVCenter, 'On')

    def paint_slider_off(self, painter):
        swidth = int((self.width() / 2) - 2)
        sheight = int(self.height() - 2)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0,50)))
        painter.drawRoundedRect(self.contentsRect(), 3, 3)
        painter.setBrush(QtGui.QBrush(self.bgcolor_slider))
        painter.drawRoundedRect(3, 1, swidth, sheight, 2, 2)
        painter.setPen(QtGui.QColor(0,0,0,150))
        painter.drawText(swidth+3, 1, swidth, sheight, Qt.AlignCenter | Qt.AlignVCenter, 'Off')

    def get_value(self):
        return self.enabled

    def set_value(self, enabled=True):
        self.enabled = enabled
        self.update()


class PKVFrame(QtWidgets.QFrame, pkmixins.StashMixin, pkmixins.LayoutMixin):

    def __init__(self, etree, control, parent=None):
        QtWidgets.QFrame.__init__(self)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        pkmixins.StashMixin._init(self)
        pkmixins.LayoutMixin._init(self, etree, control, parent)

    def paintEvent(self, event):
        QtWidgets.QFrame.paintEvent(self, event)
        return self._paint_frame(event)


def widget_factory(qwidget):
    class PKWidgetFactory(qwidget, pkmixins.LayoutMixin):
        def __init__(self, etree, control, parent=None):
            qwidget.__init__(self)
            self.setObjectName(qwidget.__name__)
            self.setLayout(QtWidgets.QVBoxLayout())
            self.layout().setContentsMargins(0,0,0,0)
            self.layout().setSpacing(0)
            pkmixins.LayoutMixin._init(self, etree, control, parent)

        def get_value(self):
            for attr in ('toPlainText', 'text'):
                callback = getattr(self, attr, None)
                if callback: return callback()
            raise Exception('Unable to get value.')

        def set_value(self, value):
            for attr in ('setPlainText', 'setText'):
                callback = getattr(self, attr, None)
                if callback: return callback(str(value))
            raise Exception('Unable to get value.')

        def attribute_placeholder(self, value):
            self.setPlaceholderText(value)

    return PKWidgetFactory
