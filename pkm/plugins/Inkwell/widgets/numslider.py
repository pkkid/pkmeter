# -*- coding: utf-8 -*-
from PySide6.QtCore import Signal
from qtemplate import QTemplateWidget


class NumSlider(QTemplateWidget):
    TMPLSTR = r"""
      <QWidget layout='QHBoxLayout()' padding='0' spacing='20'>
        <QSlider id='slider' args='(Qt.Horizontal)'>
          <Connect valueChanged='_valueChanged'/>
        </QSlider>
        <QSpinBox id='spinbox' range='(100,300)' value='180' fixedWidth='60'>
          <Connect valueChanged='_valueChanged'/>
        </QSpinBox>
      </QWidget>
    """
    valueChanged = Signal(int)

    def __init__(self, *args, **kwargs):
        super(NumSlider, self).__init__(*args, **kwargs)
        self.value = None
    
    def setRange(self, minValue, maxValue):
        self.ids.slider.setMinimum(minValue)
        self.ids.slider.setMaximum(maxValue)
        self.ids.spinbox.setRange(minValue, maxValue)

    def setValue(self, value):
        self.ids.slider.setValue(value)
        self.ids.spinbox.setValue(value)

    def _valueChanged(self, value):
        if value != self.value:
            self.value = value
            self.setValue(value)
            self.valueChanged.emit(value)
