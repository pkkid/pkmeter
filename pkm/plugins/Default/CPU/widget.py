# -*- coding: utf-8 -*-
from pkm.deskwidget import DeskWidget


class DesktopWidget(DeskWidget):
    NAME = 'CPU'
    TMPLSTR = """
      <QWidget layout='QHBoxLayout'>
        <QLabel text='CPU Widget'/>
      </QWidget>
    """
