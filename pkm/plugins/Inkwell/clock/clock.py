# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm.basedatasource import BaseDataSource
from pkm.basesettings import BaseSettings
from pkm.basewidget import BaseWidget


class DesktopWidget(BaseWidget):
    TMPL = normpath(f'{dirname(__file__)}/clock.tmpl')


class SettingsWidget(BaseSettings):
    TMPLSTR = """
      <QWidget layout='QHBoxLayout'>
        <QLabel text='Clock Settings'/>
      </QWidget>
    """


class DataSource(BaseDataSource):
    pass
