# -*- coding: utf-8 -*-
from pkm import log  # noqa
from PySide6.QtCore import Qt


class Draggable:

    def __init__(self):
        self._dragMousePos = None
        self._dragWidgetPos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragMousePos = event.globalPos()
            self._dragWidgetPos = self.pos()

    def mouseMoveEvent(self, event):
        if self._dragMousePos:
            delta = event.globalPos() - self._dragMousePos
            self.move(self._dragWidgetPos + delta)
                
    def mouseReleaseEvent(self, event):
        if self._dragMousePos:
            delta = event.globalPos() - self._dragMousePos
            if (delta.x() != 0 or delta.y() != 0) and hasattr(self, 'widgetMoved'):
                self.widgetMoved(self.pos())
        self._dragMousePos = None
        self._dragWidgetPos = None
