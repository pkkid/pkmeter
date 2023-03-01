# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import log
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
    
    def update(self):
        log.info(f'Updating {self.component.id} data.')
