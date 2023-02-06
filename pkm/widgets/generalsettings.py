# -*- coding: utf-8 -*-
from pkm.qtemplate import QTemplateWidget


class SettingsWidget(QTemplateWidget):
    TMPLSTR = """
      <QWidget layout='QHBoxLayout'>
        <QLabel text='General Preferences'/>
      </QWidget>
    """

    def __init__(self, app, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)
        self.app = app
