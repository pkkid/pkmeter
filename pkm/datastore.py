# -*- coding: utf-8 -*-
from collections import defaultdict, namedtuple
from pkm import log, utils

Sync = namedtuple('Sync', 'qtmpl, callback, valuestr, context')


class DataStore(dict):
    """ Singleton DataStore """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = dict.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        super(DataStore, self).__init__(*args, **kwargs)
        self._registry = defaultdict(list)      # Dict of {token: [Callbacks]}
    
    def register(self, qtmpl, token, callback, valuestr, context):
        log.debug(f'Registering {token} -> {callback.__self__.__class__.__name__}.{callback.__name__}()')
        self._registry[token].append(Sync(qtmpl, callback, valuestr, context))

    def update(self, item, value):
        log.debug(f'Updating {item} = {value}')
        utils.rset(self, item, value)
        for token in sorted(k for k in self._registry.keys() if k.startswith(item)):
            for qtmpl, callback, valuestr, context in self._registry[token]:
                value = qtmpl._apply(callback, valuestr, context)
