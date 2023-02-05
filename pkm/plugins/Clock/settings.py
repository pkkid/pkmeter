# -*- coding: utf-8 -*-
from pkm.qtemplate import QTemplateWidget


class SettingsWidget(QTemplateWidget):
    TMPLSTR = """
      <QWidget layout='QHBoxLayout'>
        <QLabel text='Clock Settings'/>
      </QWidget>
    """
