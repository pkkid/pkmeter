# -*- coding: utf-8 -*-
from pkm.qtemplate import QTemplateWidget


class SettingsWidget(QTemplateWidget):
    TMPLSTR = """
      <QWidget layout='QHBoxLayout'>
        <QLabel text='CPU Settings'/>
      </QWidget>
    """

    def __init__(self, app, plugin, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)
        self.app = app
        self.plugin = plugin
