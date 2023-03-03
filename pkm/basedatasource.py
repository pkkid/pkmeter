# -*- coding: utf-8 -*-
from pkm import log, utils
from PySide6 import QtCore


class BaseDataSource:
    
    def __init__(self, component):
        super(BaseDataSource, self).__init__()
        self.plugin = component.plugin                  # Plugin
        self.component = component                      # Plugin component
        self.app = QtCore.QCoreApplication.instance()   # QtCore application
        self.interval = 1000                            # Interval to update the data
        self.timer = None                               # QTimer used to update the data
        self.watchers = []                              # Desktop widgets watching this datasource
    
    def start(self):
        if self.timer is None:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update)
            self.update()
        log.info(f'Starting {self.component.id} datasource with interval {self.interval}ms')
        self.timer.start(self.interval)

    def stop(self):
        self.timer.stop()

    def update(self):
        log.warning(f'{self.plugin.id} timer running with no update() function.')
    
    def getValue(self, name, default=None):
        datapath = f'{self.component.namespace}.{name}'
        utils.rget(self.app.data, datapath, default=default)

    def setValue(self, name, value):
        datapath = f'{self.component.namespace}.{name}'
        self.app.data.setValue(datapath, value)
