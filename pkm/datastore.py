# -*- coding: utf-8 -*-
from collections import defaultdict, namedtuple
from pkm import log

Callback = namedtuple('Callback', ('obj', 'method', 'default'))


class DataStore(dict):

    def __init__(self, *args, **kwargs):
        super(DataStore, self).__init__(*args, **kwargs)
        self._registry = defaultdict(list)  # List of Callbacks

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataStore, cls).__new__(cls, *args, **kwargs)
        return cls.instance
    
    def register(self, obj, method, item, value, default=None):
        log.info(f'register({item}, {value})')

    def update(self, item, value):
        super(DataStore, self).__setattr__(item, value)
        log.info(f'update({item}, {value})')
