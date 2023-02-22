# -*- coding: utf-8 -*-
from pkm import log


class Draggable:

    def __init__(self):
        log.info('Draggable.__init__()')
        self._dragMousePos = None
        self._dragWidgetPos = None

    def mousePressEvent(self, event):
        self._dragMousePos = event.globalPos()
        self._dragWidgetPos = self.pos()

    def mouseMoveEvent(self, event):
        if self._dragMousePos:
            delta = event.globalPos() - self._dragMousePos
            self.move(self._dragWidgetPos + delta)
                
    def mouseReleaseEvent(self, event):
        if self._dragMousePos and hasattr(self, 'widgetMoved'):
            self.widgetMoved(self.pos())
        self._dragMousePos = None
        self._dragWidgetPos = None
