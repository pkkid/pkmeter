# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm.deskwidget import DeskWidget
from pkm.qtemplate import QTemplateWidget


class DesktopWidget(DeskWidget):
    TMPL = normpath(f'{dirname(__file__)}/clock.tmpl')
    NAME = 'Clock'


class SettingsWidget(QTemplateWidget):
    TMPLSTR = """
      <QWidget layout='QHBoxLayout'>
        <QLabel text='Clock Settings'/>
      </QWidget>
    """

    def __init__(self, plugin, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)
        self.plugin = plugin
