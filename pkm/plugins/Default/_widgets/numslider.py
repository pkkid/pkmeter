# -*- coding: utf-8 -*-
from pkm.qtemplate import QTemplateWidget
from PySide6.QtCore import Signal


class NumSlider(QTemplateWidget):
    """ Window titlebar with custom styles. """
    TMPLSTR = r"""
      <QWidget layout='QHBoxLayout' layout.spacing='20'>
        <QSlider id='slider' args='(Qt.Horizontal)'>
          <Connect valueChanged='_valueChanged'/>
        </QSlider>
        <QSpinBox id='spinbox' range='(100,300)' value='180'>
          <Connect valueChanged='_valueChanged'/>
        </QSpinBox>
      </QWidget>
    """
    valueChanged = Signal(int)

    def __init__(self, *args, **kwargs):
        super(NumSlider, self).__init__(*args, **kwargs)
    
    def setRange(self, minValue, maxValue):
        self.ids.slider.setMinimum(minValue)
        self.ids.slider.setMaximum(maxValue)
        self.ids.spinbox.setRange(minValue, maxValue)

    def setValue(self, value):
        self.ids.slider.setValue(value)
        self.ids.spinbox.setValue(value)
    
    def _valueChanged(self, value):
        self.setValue(value)
        self.valueChanged.emit(value)
