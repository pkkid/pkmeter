# -*- coding: utf-8 -*-
"""
PKMeter Template
"""
import re
from pkm import utils
from pkm.filters import filters


class Template:
    TOKEN_START = '{{'
    TOKEN_END = '}}'
    REGEX = re.compile('%s.+?%s' % (TOKEN_START, TOKEN_END))
    
    def __init__(self, tmplstr, callback):
        self.tmplstr = tmplstr          # Full template string
        self.callback = callback        # Callback for apply
        self.variables = []             # List of variables in template
        self.namespaces = set()         # List of namespaces in template
        self._parse()

    def __repr__(self):
        return "<Template:%s>" % self.tmplstr

    def _parse(self):
        tmplstrs = re.findall(self.REGEX, self.tmplstr)
        for tmplstr in tmplstrs:
            varstr = tmplstr[len(self.TOKEN_START):-len(self.TOKEN_END)]
            variable = Variable(varstr)
            self.variables.append(variable)
            self.namespaces.add(variable.namespace)

    def apply(self, data):
        value = self.tmplstr
        for variable in self.variables:
            replacefrom = '%s%s%s' % (self.TOKEN_START, variable.varstr, self.TOKEN_END)
            replaceto = variable.get_value(data)
            if replaceto is None: replaceto = ''
            value = value.replace(replacefrom, str(replaceto))
        self.callback(value)


class TruthTemplate:
    AND_SEPARATOR = ' and '

    def __init__(self, tmplstr, callback):
        self.tmplstr = tmplstr          # Full template string
        self.callback = callback        # Callback for apply
        self.variables = []             # List of variables in template
        self.namespaces = set()         # List of namespaces in template
        self._parse()

    def _parse(self):
        tmplstrs = self.tmplstr.split(self.AND_SEPARATOR)
        for varstr in tmplstrs:
            variable = Variable(varstr)
            self.variables.append(variable)
            self.namespaces.add(variable.namespace)

    def apply(self, data):
        values = [v.get_value(data) for v in self.variables]
        value = values[0] if len(values) == 1 else all(values)
        self.callback(data, value)
        

class Variable:
    FILTER_SEPARATOR = '|'

    def __init__(self, varstr, callback=None):
        self.varstr = varstr            # Full variable string (without {{}})
        self.callback = callback        # Callback for apply
        self.varpath = None             # Variable path
        self.namespace = None           # Variable namespace
        self.filters = []               # Filters to apply
        self._parse()

    def __repr__(self):
        return '<Variable:%s>' % self.varstr

    def _parse(self):
        if self.FILTER_SEPARATOR in self.varstr:
            self.varpath, filterstrs = self.varstr.split(self.FILTER_SEPARATOR, 1)
            filterstrs = filterstrs.split(self.FILTER_SEPARATOR)
            self.filters = [Filter(filterstr) for filterstr in filterstrs]
        else:
            self.varpath = self.varstr
        self.namespace = self.varpath.split('.')[0]

    def get_value(self, data):
        value = utils.rget(data, self.varpath)
        for tfilter in self.filters:
            value = tfilter.apply(value)
        return value

    def apply(self, data):
        value = self.get_value(data)
        self.callback(data, value)


class Filter:
    ARGUMENT_SEPARATOR = ':'

    def __init__(self, filterstr):
        self.filterstr = filterstr
        self.filter = None
        self.arg = None
        self._parse()

    def __repr__(self):
        return '<Filter:%s>' % self.filterstr

    def _parse(self):
        filtername = self.filterstr
        if self.ARGUMENT_SEPARATOR in self.filterstr:
            filtername, arg = self.filterstr.split(self.ARGUMENT_SEPARATOR, 1)
            self.arg = arg.strip('"\'')
        self.filter = filters.get(filtername)
        if not self.filter:
            raise Exception('Unknown filter: %s' % filtername)

    def apply(self, value):
        if self.arg:
            return self.filter(value, self.arg)
        return self.filter(value)
