# -*- coding: utf-8 -*-
from pkm import log
from pkm.qtemplate import QTemplateWidget
from PySide6.QtCore import QTimer


class BaseDataSource(QTemplateWidget):
    
    def __init__(self, component):
        super(BaseDataSource, self).__init__()
        self.plugin = component.plugin      # Plugin
        self.component = component          # Plugin component
        self.interval = 1000                # Interval to update the data
        self.timer = None                   # QTimer used to update the data
        self.watchers = []                  # Desktop widgets watching this datasource
    
    def start(self):
        if self.timer is None:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update)
        self.timer.start(self.interval)

    def stop(self):
        self.timer.stop()

    def update(self):
        log.warning(f'{self.plugin.id} timer running with no update() function.')
