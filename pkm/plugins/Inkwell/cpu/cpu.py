# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm.basesettings import BaseSettings
from pkm.basewidget import BaseWidget


class DesktopWidget(BaseWidget):
    TMPL = normpath(f'{dirname(__file__)}/cpu.tmpl')
    

class SettingsWidget(BaseSettings):
    TMPLSTR = """
      <QWidget layout='QHBoxLayout'>
        <QLabel text='CPU Settings'/>
      </QWidget>
    """
