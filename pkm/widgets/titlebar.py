# -*- coding: utf-8 -*-
from pkm.qtemplate import QTemplateWidget


class TitleBar(QTemplateWidget):
    """ Window titlebar with custom styles. """
    TMPLSTR = r"""
      <QWidget layout='QHBoxLayout' id='titlebar' layout.contentsMargins='[0,0,0,10]' layout.spacing='8'>
        <QLabel id='appicon'/>
        <QLabel id='title' />
        <Stretch />
        <QPushButton text='󰅖'>
          <Connect clicked='close'/>
        </QPushButton>
      </QWidget>
    """

    def __init__(self, *args, **kwargs):
        super(TitleBar, self).__init__(*args, **kwargs)
        self.mousepos = None
        self.widgetpos = None
    
    def setTitle(self, title):
        self.ids.title.setText(title)

    def close(self):
        self.parent().parent().close()

    def mousePressEvent(self, event):
        self.mousepos = event.globalPos()
        self.widgetpos = self.parent().parent().pos()

    def mouseMoveEvent(self, event):
        if self.mousepos:
            delta = event.globalPos() - self.mousepos
            self.parent().parent().move(self.widgetpos + delta)

    def mouseReleaseEvent(self, event):
        self.mousepos = None
        self.widgetpos = None
