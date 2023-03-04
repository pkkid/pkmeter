# -*- coding: utf-8 -*-
import datetime
from os.path import dirname, normpath
from pkm import base


class DataSource(base.DataSource):
    
    def update(self):
        now = datetime.datetime.now()
        self.setValue('datetime', now)


class DesktopWidget(base.DesktopWidget):
    TMPL = normpath(f'{dirname(__file__)}/clock.tmpl')


class SettingsWidget(base.SettingsWidget):
    TMPLSTR = """
      <QWidget layout='QHBoxLayout()'>
        <QLabel text='Clock Settings'/>
      </QWidget>
    """
