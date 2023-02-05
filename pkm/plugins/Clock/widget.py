# -*- coding: utf-8 -*-
from pkm.widgets.desktopwidget import DesktopWidget


class DesktopWidget(DesktopWidget):
    NAME = 'Clock'
    TMPLSTR = """
      <QWidget layout='QHBoxLayout'>
        <QLabel text='Clock Widget'/>
      </QWidget>
    """
