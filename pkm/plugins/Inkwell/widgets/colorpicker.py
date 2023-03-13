# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import log, utils  # noqa
from pkm.qtemplate import QTemplateWidget
from PySide6.QtCore import Signal


class ColorPicker(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/colorpicker.tmpl')

    def show(self):
        """ Show this settings window. """
        utils.centerWindow(self)
        super(ColorPicker, self).show()


class ColorSlider(QTemplateWidget):
    TMPLSTR = """
      <QWidget class='colorslider' layout='QHBoxLayout()' padding='0' spacing='20'>
        <QSlider id='slider' args='(Qt.Horizontal)'>
          <Connect valueChanged='_valueChanged'/>
        </QSlider>
        <QSpinBox id='spinbox' fixedWidth='60'>
          <Connect valueChanged='_valueChanged'/>
        </QSpinBox>
      </QWidget>
    """
    valueChanged = Signal(int)

    def __init__(self, *args, **kwargs):
        super(ColorSlider, self).__init__(*args, **kwargs)
        self._value = None
    
    def setRange(self, minValue, maxValue):
        self.ids.slider.setMinimum(minValue)
        self.ids.slider.setMaximum(maxValue)
        self.ids.spinbox.setRange(minValue, maxValue)

    def setValue(self, value):
        self.ids.slider.setValue(value)
        self.ids.spinbox.setValue(value)
    
    def _valueChanged(self, value):
        if value != self._value:
            self._value = value
            self.setValue(value)
            self.valueChanged.emit(value)


