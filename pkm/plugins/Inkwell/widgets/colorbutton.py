# -*- coding: utf-8 -*-
# https://www.pythonguis.com/widgets/qcolorbutton-a-color-selector-tool-for-pyqt/
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt, Signal


class ColorButton(QtWidgets.QPushButton):
    """ Custom Qt Widget to show a chosen color.
        Left-clicking the button shows the color-chooser, while
        right-clicking resets the color to None (no-color).
    """
    colorChanged = Signal(object)

    def __init__(self, *args, color=None, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)
        self._color = None                          # Current selected color
        self._default = color                       # Default color
        self._showAlpha = False                     # Show alpha channel
        self._showButtons = True                    # Show buttons
        self.pressed.connect(self.onColorPicker)
        self.setProperty('class', 'colorbutton')
        self.setColor(self._default)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color)
        if self._color:
            self.setStyleSheet(f'[class=colorbutton] {{ background-color: {self._color}; }}')
        else:
            self.setStyleSheet('')
    
    def setShowAlpha(self, value):
        self._showAlpha = value
    
    def setShowButtons(self, value):
        self._showButtons = value

    def color(self):
        return self._color

    def onColorPicker(self):
        """ Show color-picker dialog to select color.
            Qt will use the native dialog by default.
        """
        dlg = QtWidgets.QColorDialog(self)
        dlg.setOption(QtWidgets.QColorDialog.DontUseNativeDialog)
        if not self._showButtons: dlg.setOption(QtWidgets.QColorDialog.NoButtons)
        if self._showAlpha: dlg.setOption(QtWidgets.QColorDialog.ShowAlphaChannel)
        dlg.setStyleSheet('QColorDialog { background-color: #222222; }')
        dlg.currentColorChanged.connect(lambda c: self.setColor(dlg.currentColor().name()))
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))
        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(self._default)
        return super(ColorButton, self).mousePressEvent(e)
