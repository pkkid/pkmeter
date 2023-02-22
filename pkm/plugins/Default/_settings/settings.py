# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import log, utils  # noqa
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtCore


class SettingsWidget(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/settings.tmpl')

    def __init__(self, plugin, *args, **kwargs):
        self.plugin = plugin
        super(SettingsWidget, self).__init__(*args, **kwargs)
    
    def _initData(self):
        monitors = []
        app = QtCore.QCoreApplication.instance()
        for i, screen in enumerate(app.screens()):
            monitor = utils.Bunch()
            monitor.value = i
            monitor.text = f'#{i} ({screen.name()})'
            monitors.append(monitor)
        self.data.update('generalsettings.monitors', monitors)

    def _widthChanged(self, value):
        """ Save new monitor value. """
        log.info(f'_widthChanged({value=})')
