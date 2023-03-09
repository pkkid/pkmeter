# -*- coding: utf-8 -*-
from collections import defaultdict, namedtuple
from pkm import log, utils

Sync = namedtuple('Sync', 'qtmpl, expr, context, callback')


class DataStore(utils.Bunch):
    """ Datastore used to auto update widget values. """

    def __init__(self, *args, **kwargs):
        super(DataStore, self).__init__(*args, **kwargs)
        self._registry = defaultdict(list)  # Dict of {token: [Callbacks]}
    
    def register(self, qtmpl, token, callback, expr, context):
        """ Register a new value to this DataStore. """
        log.debug(f'Registering {token} -> {callback.__self__.__class__.__name__}.{callback.__name__}()')
        self._registry[token].append(Sync(qtmpl, expr, context, callback))

    def listMetrics(self):
        """ Retutns a flattened list containing (key, value, type) for
            all values in this DataStore. """
        return utils.flattenDataTree(self)
    
    def printValues(self):
        """ Pretty print the values to console. """
        for row in self.listMetrics():
            print(row)

    def setValue(self, item, value):
        """ Update the specified value. This will additionally look up any registered
            sync values, and execute its callback function with the new data in place.
        """
        utils.rset(self, item, value)
        for token in sorted(k for k in self._registry.keys() if k.startswith(item)):
            for sync in self._registry[token]:
                value = sync.qtmpl._apply(sync.expr, sync.context, sync.callback)
    
    
