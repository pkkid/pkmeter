# -*- coding: utf-8 -*-
from PySide6 import QtWidgets
from PySide6.QtCore import Qt


class TitleBar(QtWidgets.QWidget):
    """ Allows dragging the parent window. """

    def __init__(self, window, *args, **kwargs):
        super(TitleBar, self).__init__(*args, **kwargs)
        self.setProperty('class', 'titlebar')
        self._dragMousePos = None
        self._dragWidgetPos = None
        self.window = window

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragMousePos = event.globalPos()
            self._dragWidgetPos = self.window.pos()

    def mouseMoveEvent(self, event):
        if self._dragMousePos:
            delta = event.globalPos() - self._dragMousePos
            self.window.move(self._dragWidgetPos + delta)

    def mouseReleaseEvent(self, event):
        self._dragMousePos = None
        self._dragWidgetPos = None
