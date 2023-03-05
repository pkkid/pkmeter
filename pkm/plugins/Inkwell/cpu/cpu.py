# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import base


class DesktopWidget(base.DesktopWidget):
    TMPL = normpath(f'{dirname(__file__)}/cpu.tmpl')
    

class SettingsWidget(base.SettingsWidget):
    TMPLSTR = """
      <QWidget layout='QVBoxLayout()'>
        <QLabel text='CPU Settings'/>
        <Stretch/>
      </QWidget>
    """
