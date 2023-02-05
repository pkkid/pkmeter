# -*- coding: utf-8 -*-
from pkm.widgets.desktopwidget import DesktopWidget


class DesktopWidget(DesktopWidget):
    NAME = 'CPU'
    TMPLSTR = """
      <QWidget layout='QHBoxLayout'>
        <QLabel text='CPU Widget'/>
      </QWidget>
    """
