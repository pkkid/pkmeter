# -*- coding: utf-8 -*-
from pkm.deskwidget import DeskWidget


class DesktopWidget(DeskWidget):
    NAME = 'Clock'
    TMPLSTR = """
      <QWidget layout='QHBoxLayout'>
        <QLabel text='Clock Widget'/>
      </QWidget>
    """
