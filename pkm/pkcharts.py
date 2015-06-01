# -*- coding: utf-8 -*-
"""
PKMeter Charts
"""
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from pkm import pkmixins, utils
from pkm.decorators import threaded_method


class PKLineChart(QtWidgets.QFrame, pkmixins.LayoutMixin):

    def __init__(self, etree, control, parent=None):
        QtWidgets.QFrame.__init__(self)
        self.autoscale = True                           # Autoscale max value
        self.bgcolor = QtGui.QColor(255,255,255,10)     # Chart background color
        self.colors = [QtGui.QColor(255,0,0)]           # Chart line colors
        self.interval = None                            # Set update sec for smooth scrolling
        self.maxvalue = 1                               # Max value in dataset
        self.minmax = 1                                 # Minimum max value
        self.pxperpt = 3                                # Pixels per point
        self.showzero = True                            # Plot zero values
        self.data = []
        self.numpoints = None
        self.offset = 0
        pkmixins.LayoutMixin._init(self, etree, control, parent)

    def _init_data(self, values, numpoints):
        self.data = []
        self.numpoints = numpoints
        for i in range(self.numpoints):
            self.data.append([-1] * len(values))

    def attribute_bgcolor(self, value):
        self.bgcolor = utils.hex_to_qcolor(value)

    def attribute_autoscale(self, value):
        self.autoscale = True if value.lower() == 'true' else False

    def attribute_colors(self, value):
        self.colors = [utils.hex_to_qcolor(v) for v in value.split(',')]

    def attribute_interval(self, value):
        self.interval = int(float(value))

    def attribute_minmax(self, value):
        self.minmax = float(value)

    def attribute_pxperpt(self, value):
        self.pxperpt = int(value)

    def attribute_showzero(self, value):
        self.showzero = True if value.lower() == 'true' else False

    @threaded_method
    def attribute_values(self, values):
        if not values: return None
        values = [float(v) for v in values.split(',')]
        self.showit = False
        if len(values) == 2:
            self.showit = True
        numpoints = int(self.width() / self.pxperpt)
        if not self.data or numpoints != self.numpoints:
            self._init_data(values, numpoints)
        self.data = self.data[1:] + [values]
        if self.autoscale:
            self.maxvalue = max([max(x) for x in self.data] + [self.minmax])
            self.setToolTip('Max: %s' % self.maxvalue)
        if self.interval:
            loops = self.interval * 10
            for i in range(loops):
                self.offset = self.pxperpt * (i / float(loops))
                self.update()
                time.sleep(self.interval / float(loops))
        else:
            self.update()

    def paintEvent(self, event):
        if not self.data: return
        QtWidgets.QFrame.paintEvent(self, event)
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # Draw background
        painter.setBrush(QtGui.QBrush(self.bgcolor))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.contentsRect(), 2, 2)
        # Draw the Lines
        for i in range(len(self.data[0])):
            path = None
            pen = QtGui.QPen(self.colors[i % len(self.colors)])
            for j in range(len(self.data)):
                value = self.data[j][i]
                prevvalue = self.data[j-1][i]
                if value == -1 or prevvalue == -1:
                    continue
                if not self.showzero and value <= 0 and prevvalue <= 0:
                    continue
                x1 = (self.pxperpt * (j - 0.5) + self.pxperpt / 4) - self.offset
                x2 = (self.pxperpt * j + self.pxperpt / 4) - self.offset
                y1 = self.height() - int((self.height() - 1) * (prevvalue / self.maxvalue))
                y2 = self.height() - int((self.height() - 1) * (value / self.maxvalue))
                path = path or QtGui.QPainterPath(QtCore.QPointF(x1,y1))
                path.cubicTo(x1, y1, x1, y2, x2, y2)
            if path:
                painter.strokePath(path, pen)
        painter.end()


class PKPieChart(QtWidgets.QFrame, pkmixins.LayoutMixin):

    def __init__(self, etree, control, parent=None):
        QtWidgets.QFrame.__init__(self)
        self.bgcolor = QtGui.QColor(255,255,255,13)     # Chart background color
        self.colors = [QtGui.QColor(255,0,0)]           # Chart line colors
        self.data = []                                  # Current plot data
        pkmixins.LayoutMixin._init(self, etree, control, parent)

    def attribute_bgcolor(self, value):
        self.bgcolor = utils.hex_to_qcolor(value)

    def attribute_colors(self, value):
        self.colors = [utils.hex_to_qcolor(v) for v in value.split(',')]

    def attribute_values(self, values):
        if not values: return None
        self.data = [float(v) for v in values.split(',')]
        self.update()

    def paintEvent(self, event):
        QtWidgets.QFrame.paintEvent(self, event)
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        # Draw the Pie
        rwidth = int(min([self.width(), self.height()]) - 2)
        x = int((self.width() / 2) - (rwidth / 2))
        y = int((self.height() / 2) - (rwidth / 2))
        rect = QtCore.QRect(x, y, rwidth, rwidth)
        angle1 = 0
        for i in range(len(self.data)):
            angle2 = angle1 + (3.6 * self.data[i])
            painter.setBrush(QtGui.QBrush(self.colors[i % len(self.colors)]))
            painter.drawPie(rect, angle1*-16, (angle2-angle1)*-16)
            angle1 = angle2
        # Draw the remainer (background)
        angle2 = 360
        painter.setBrush(QtGui.QBrush(self.bgcolor))
        painter.drawPie(rect, angle1*-16, (angle2-angle1)*-16)
        painter.end()


class PKVBarChart(QtWidgets.QFrame, pkmixins.LayoutMixin):

    def __init__(self, etree, control, parent=None):
        QtWidgets.QFrame.__init__(self)
        self.bgcolor = QtGui.QColor(255,255,255,10)     # Chart background color
        self.colors = [QtGui.QColor(255,0,0)]           # Chart line colors
        self.data = []                                  # Current plot data
        pkmixins.LayoutMixin._init(self, etree, control, parent)

    def attribute_bgcolor(self, value):
        self.bgcolor = utils.hex_to_qcolor(value)

    def attribute_colors(self, value):
        self.colors = [utils.hex_to_qcolor(v) for v in value.split(',')]

    def attribute_values(self, values):
        if not values: return None
        self.data = [float(v) for v in values.split(',')]
        self.update()

    def paintEvent(self, event):
        if not self.data: return
        QtWidgets.QFrame.paintEvent(self, event)
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # Draw background
        painter.setBrush(QtGui.QBrush(self.bgcolor))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.contentsRect(), 2, 2)
        # Draw the bars
        barwidth = (self.width() - 4) / len(self.data)
        for i in range(len(self.data)):
            barheight = int(self.height() * (self.data[i] / 100))
            baroffset = i * barwidth + 2
            painter.setBrush(QtGui.QBrush(self.colors[i % len(self.colors)]))
            painter.drawRoundedRect(baroffset, self.height()-barheight, barwidth, barheight, 1, 1)
        painter.end()
