# -*- coding: utf-8 -*-
# Simple Qt Markup Language
# This will convert a sqml file to its equivilent pyside6 Qt widgets. Rather
# than create QtQuick Controls, this will create the more native QtWidgets
# Because of this, I believe the markup to be more powerful than qml, and much
# less verbose than QT Creator .ui files. However note, it's also a bit quick
# and dirty in some places.
import inspect
import re
from os.path import basename, dirname, join, normpath
from pkm import log, utils
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from xml.etree import ElementTree

QTWIDGETS = dict(inspect.getmembers(QtWidgets, inspect.isclass))
QOBJECTS = {k:v for k,v in {**QTWIDGETS}.items() if k.startswith('Q')}

REGEX_INT = re.compile(r'^\d+$')
REGEX_FLOAT = re.compile(r'^\d+\.\d+$')
REGEX_LIST = re.compile(r'^\[.+?\]$')


class QTemplateWidget(QtWidgets.QWidget):
    """ My interpreation of a less verbose Qt Template language. """
    TMPL = None  # filepath of tmpl file to load
    
    def __init__(self):
        super(QTemplateWidget, self).__init__()
        self.ids = utils.Bunch()
        self._read_template()
        
    def _read_template(self):
        """ Reads the template and walks the xml tree to build the Qt UI. """
        log.info(f'Reading template {basename(self.TMPL)}')
        with open(self.TMPL) as handle:
            elem = ElementTree.fromstring(handle.read())
        self._walk_elem(elem)
    
    def _walk_elem(self, elem, parent=None, indent=0):
        # Check this is a known tag
        if self._tag_qobject(elem, parent, indent): return    # <QWidget attr='value' />
        if self._tag_set(elem, parent, indent): return        # <set attr='value' />; no children
        if self._tag_connect(elem, parent, indent): return    # <connect slot='callback' />; no children
        raise Exception(f'Unknown tag {elem.tag}')
        
    def _tag_qobject(self, elem, parent, indent):
        """ Creates a QObject and appends it to the layout of parent. """
        if elem.tag in QOBJECTS:
            qcls = QOBJECTS[elem.tag]
            qobj = self if parent is None else qcls(parent=parent)
            log.debug(f'{" "*indent}{qobj.__class__.__name__}')
            self._apply_attrs(qobj, elem, indent+1)
            if parent is not None:
                parent.layout().addWidget(qobj)
            # Keep iterating the template
            for echild in elem:
                self._walk_elem(echild, qobj, indent+1)
            return True

    def _tag_set(self, elem, parent, indent):
        """ Reads attributes of a Set tag and applies values by calling
            set<attr>(<value>) on the parent Qt object.
        """
        if elem.tag.lower() == 'set':
            self._apply_attrs(parent, elem, indent)
            return True
    
    def _tag_connect(self, elem, parent, indent):
        """ Reads attributes of a Connect tag, and sets the callback
            for the specified attribute name to self.<value>().
        """
        if elem.tag.lower() == 'connect':
            for attr, valuestr in elem.attrib.items():
                callback = getattr(self, valuestr)
                getattr(parent, attr).connect(callback)
            return True

    def _apply_attrs(self, qobj, elem, indent=0):
        """ Applies attributes of elem to qobj. """
        for attr, valuestr in elem.attrib.items():
            value = self._parse_value(valuestr)
            if self._attr_id(qobj, attr, value, valuestr, indent): continue             # id='myobject'
            if self._attr_stylesheet(qobj, attr, value, valuestr, indent): continue     # attr='value'
            if self._attr_set(qobj, attr, value, valuestr, indent): continue            # attr='value'
            raise Exception(f'Unknown attribute {attr} on element {elem.tag}.')

    def _attr_id(self, qobj, attr, value, valuestr, indent):
        """ Saves a reference to qobj as self.ids.<value> """
        if attr.lower() == 'id':
            qobj.setObjectName(value)
            self.ids[value] = qobj
            return True
    
    def _attr_stylesheet(self, qobj, attr, value, valuestr, indent):
        """ Sets a stylesheet on the specified qobj. We treat this one special
            because we have to find the relative path, read the file, and apply
            a simple template langauge to it before applying the stylesheet
            contents to the qobj.
        """
        if attr.lower() == 'stylesheet':
            filepath = normpath(join(dirname(self.TMPL), value))
            with open(filepath) as handle:
                contents = handle.read()
            qobj.setStyleSheet(contents)
            return True

    def _attr_set(self, qobj, attr, value, valuestr, indent):
        """ Calls set<attr>(<value>) on the qbject. """
        setattr = f'set{attr[0].upper()}{attr[1:]}'
        if hasattr(qobj, setattr):
            log.debug(f'{" "*indent}{setattr}({valuestr})')
            if isinstance(value, list):
                getattr(qobj, setattr)(*value)
                return True
            getattr(qobj, setattr)(value)
            return True
    
    def _parse_value(self, value):
        """ Takes a best guess converting a string value from the template
            to a native Python value.
        """
        if value in QOBJECTS: return QOBJECTS[value]()
        if value.startswith('Qt.'): return getattr(Qt, value)
        if value.lower() in ['true']: return True
        if value.lower() in ['false']: return False
        if value.lower() in ['none']: return None
        if re.findall(REGEX_INT, value): return int(value)
        if re.findall(REGEX_FLOAT, value): return float(value)
        if re.findall(REGEX_LIST, value):
            return list(self._parse_value(x) for x in value.strip('[]').split(','))
        return value
