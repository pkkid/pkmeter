# -*- coding: utf-8 -*-
# Simple Qt Markup Language
# This will convert a sqml file to its equivilent pyside6 Qt widgets. Rather
# than create QtQuick Controls, this will create the more native QtWidgets
# Because of this, I believe the markup to be more powerful than qml, and much
# less verbose than QT Creator .ui files. However note, it's also a bit quick
# and dirty in some places.
import inspect, re
from PySide6 import QtCore  # noqa
from PySide6 import QtWidgets  # noqa
from xml.etree import ElementTree
from pkm import log

QTCORE = dict(inspect.getmembers(QtCore, inspect.isclass))
QTWIDGETS = dict(inspect.getmembers(QtWidgets, inspect.isclass))
QOBJECTS = {k:v for k,v in {**QTCORE, **QTWIDGETS}.items() if k.startswith('Q')}

REGEX_INT = re.compile(r'^\d+$')
REGEX_FLOAT = re.compile(r'^\d+\.\d+$')
REGEX_LIST = re.compile(r'^\[.+?\]$')


class SimpleObject:
    
    def __init__(self, filepath):
        self.ids = {}
        self.elem = self._read_tmpl(filepath)
        self.qobj = self._walk_elem(self.elem)
    
    def _read_tmpl(self, filepath):
        with open(filepath) as handle:
            return ElementTree.fromstring(handle.read())
    
    def _walk_elem(self, elem, parent=None, indent=0):
        qobj = QOBJECTS[elem.tag](parent=parent)
        log.debug(f'{" "*indent}{qobj.__class__.__name__}')
        self._apply_attrs(qobj, elem, indent)
        if parent is not None:
            parent.layout().addWidget(qobj)
        for echild in elem:
            self._walk_elem(echild, qobj, indent+2)
        return qobj
    
    def _apply_attrs(self, qobj, elem, indent=0):
        for attr, valuestr in elem.attrib.items():
            value = self._parse_value(valuestr)
            setattr = f'set{attr[0].upper()}{attr[1:]}'
            if hasattr(qobj, setattr):
                log.debug(f'{" "*indent}{setattr}({valuestr})')
                if isinstance(value, list):
                    getattr(qobj, setattr)(*value)
                else:
                    getattr(qobj, setattr)(value)
            
    def _parse_value(self, value):
        if value in QOBJECTS: return QOBJECTS[value]()
        if value.lower() in ['true']: return True
        if value.lower() in ['false']: return False
        if value.lower() in ['none']: return None
        if re.findall(REGEX_INT, value): return int(value)
        if re.findall(REGEX_FLOAT, value): return float(value)
        if re.findall(REGEX_LIST, value):
            result = list(self._parse_value(x) for x in value.strip('[]').split(','))
            return result
        return value
