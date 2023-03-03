# -*- coding: utf-8 -*-
from collections import defaultdict, namedtuple
from pkm import log, utils

Sync = namedtuple('Sync', 'qtmpl, callback, expr, context')


class DataStore(utils.Bunch):
    """ Datastore used to auto update widget values. """

    def __init__(self, *args, **kwargs):
        super(DataStore, self).__init__(*args, **kwargs)
        self._registry = defaultdict(list)      # Dict of {token: [Callbacks]}
    
    def register(self, qtmpl, token, callback, expr, context):
        log.debug(f'Registering {token} -> {callback.__self__.__class__.__name__}.{callback.__name__}()')
        self._registry[token].append(Sync(qtmpl, callback, expr, context))

    def setValue(self, item, value):
        utils.rset(self, item, value)
        for token in sorted(k for k in self._registry.keys() if k.startswith(item)):
            for qtmpl, callback, expr, context in self._registry[token]:
                value = qtmpl._apply(callback, expr, context)
