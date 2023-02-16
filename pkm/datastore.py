# -*- coding: utf-8 -*-
from collections import defaultdict, namedtuple
from pkm import log, utils

# Needs to match self.data._loading line in qtemplate.py
Sync = namedtuple('Callback', ('qtmpl', 'qobj', 'elem', 'attr', 'context'))


class DataStore(dict):

    def __init__(self, *args, **kwargs):
        super(DataStore, self).__init__(*args, **kwargs)
        self._loading = None                # Current elem, attr, qobj qtemplate is loading
        self._registry = defaultdict(list)  # List of Callbacks
        self._data = utils.Bunch()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataStore, cls).__new__(cls, *args, **kwargs)
        return cls.instance
    
    def __getitem__(self, item):
        if self._loading:
            self.register(Sync(*self._loading))
        return self._data.get(item)
    
    def register(self, sync):
        valuestr = sync.elem.attrib.get(sync.attr, '')
        valuestr = valuestr.split(' in ')[1] if ' in ' in valuestr else valuestr
        tokens = utils.tokenize(valuestr)
        tokens = [t[5:] for t in tokens if t.startswith('data.')]
        for token in tokens:
            log.info(f'register[{token}].append({sync.elem.tag}, {sync.attr})')
            self._registry[token].append(sync)

    def update(self, item, value):
        log.info(f'update({item}, {value})')
        utils.rset(self._data, item, value)
        keys = sorted(k for k in self._registry.keys() if k.startswith(item))
        for key in keys:
            for qtmpl, qobj, elem, attr, context in self._registry[key]:
                valuestr = elem.attrib[attr]
                value = qtmpl._evaluate(valuestr, context)
                qtmpl._attrSet(qobj, elem, attr, context, value)