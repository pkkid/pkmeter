# -*- coding: utf-8 -*-
"""
Simple Qt Markup Language

A QWidget that can read an xml template file to easily* build the application
structure of other Qt widgets. I created this as I personally the Qt Designer
to be lacking in available widgets, the .qml format was not very friendly to
use, and building apps in straight Python is quite cumbersome.

When reading the .tmpl file, there can only be one top level QWidget defiend.
This is what the main class will be represented as. From there, the following
rules are followed while traversing the XML tree as new elements are found.

TAGS - When a new tag is found, the following are checked:

1. If the tag name matches a QObject in the PySide6.QQtWidgets module, it
   will be created and added to the layout of it's parent element.
2. If the tag name is "Set" it will read the attributes of that element and
   apply all values to the parent qobject.
3. If the tag name matches an "add<Tag>" method on the parent, that function
   will be called on the parent element, using the arg or args attribute to
   determine the arguments. For example: <TabBar><Tab arg='General'></TabBar>
4. If the tag name is "Spacing" or "Stretch", the addSpacing or addStretch will
   be called on the parent layout.
5. If the tag name is Connect, it must be accomonied by an attribute named
   after the signal function to connect from with its value being a dot
   delimited string referring to the function to be called.
   For example: <Connect clicked='app.quit'/>

ATTRIBUTES - When attributes are found, the following are checked:

1. if the attribute is "args", the value(s) will be parsed and passed
   as constructor arguments to the class being created.
2. if the attribute is "id", a reference to the created object will be added to
   self.ids for easier access to it from other Python functions. As well, the
   object.setObjectName will be called to set the object name, allowing you to
   refer to this object in stylesheets.
3. If the attribute follows the format "layout.<attr>", it will attempt the call
   the layout().set<attr>() function on the parent qobject.
4. Finally, we check the the parent qobject has a method definition for
   set<attr>(), and if so it will be called with the attribute values.

VALUES - When values are found there is a best guess made for the type to cast
the string value to. The following types are supported: bool, int, float, list.
If the value looks like a list, each item will also be parsed. The values will
sent to the corresponding function as *args. PySide6.QtCore.Qt objects are also
supported, and can be represented by the string such as "Qt.ApplicationModal".
"""
import inspect
import re
from os.path import basename
from pkm import log, utils
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from xml.etree import ElementTree

QTWIDGETS = dict(inspect.getmembers(QtWidgets, inspect.isclass))
QOBJECTS = {k:v for k,v in {**QTWIDGETS}.items() if k.startswith('Q')}
QOBJECTS['Qt'] = Qt

REGEX_INT = re.compile(r'^\d+$')
REGEX_FLOAT = re.compile(r'^\d+\.\d+$')
REGEX_LIST = re.compile(r'^\[.*?\]$')
TRUEVALUES = ('yes', 'true', '1')


class QTemplateWidget(QtWidgets.QWidget):
    """ My interpreation of a less verbose Qt Template language. """
    TMPL = None  # filepath of tmpl file to load
    DEFAULT_LAYOUT_MARGINS = None  # default values for qobj.layout().setContentsMargins()
    DEFAULT_LAYOUT_SPACING = None  # default values for qobj.layout().setSpacing()
    
    def __init__(self):
        super(QTemplateWidget, self).__init__()
        self.ids = utils.Bunch()
        self.load_template()
        
    def load_template(self, filepath=TMPL):
        """ Reads the template and walks the xml tree to build the Qt UI. """
        log.info(f'Reading template {basename(self.TMPL)}')
        tree = ElementTree.parse(self.TMPL)
        self._walk_elem(tree.getroot())
    
    def _walk_elem(self, elem, parent=None, indent=0):
        # Check this is a known tag
        if self._tag_qobject(elem, parent, indent): return    # <QWidget attr='value' />
        if self._tag_set(elem, parent, indent): return        # <set attr='value' />; no children
        if self._tag_add(elem, parent, indent): return        # add<Tag>(attr=value)
        if self._tag_spacing(elem, parent, indent): return    # <spacing size='1' />; no children
        if self._tag_stretch(elem, parent, indent): return    # <stretch ratio='1' />; no children
        if self._tag_connect(elem, parent, indent): return    # <connect slot='callback' />; no children
        raise Exception(f'Unknown tag "{elem.tag}" in element {parent.__class__.__name__}.')
        
    def _tag_qobject(self, elem, parent, indent):
        """ Creates a QObject and appends it to the layout of parent. """
        if elem.tag in QOBJECTS:
            qcls = utils.rget(QOBJECTS, elem.tag)
            args = self._parse_value(elem.attrib.get('args', '[]'))
            args = [args] if not isinstance(args, list) else args
            qobj = self if parent is None else qcls(*args, parent=parent)
            log.debug(f'{" "*indent}{qobj.__class__.__name__}')
            self._apply_attrs(qobj, elem, indent+1)
            if parent is not None:
                parent.layout().addWidget(qobj)
            # Keep iterating the template
            for echild in elem:
                self._walk_elem(echild, qobj, indent+1)
            return True
    
    def _tag_add(self, elem, parent, indent):
        """ Check we're adding an attribute to the parent. """
        addfunc = f'add{elem.tag}'
        if hasattr(parent, addfunc):
            args = self._parse_value(elem.attrib.get('args', '[]'))
            args = [args] if not isinstance(args, list) else args
            log.debug(f'{" "*indent}{addfunc}(*{args})')
            getattr(parent, addfunc)(*args)
            return True

    def _tag_set(self, elem, parent, indent):
        """ Reads attributes of a Set tag and applies values by calling
            set<attr>(<value>) on the parent Qt object.
        """
        if elem.tag.lower() == 'set':
            self._apply_attrs(parent, elem, indent)
            return True
    
    def _tag_spacing(self, elem, parent, indent):
        """ Adds a stretch tag to the layout, pushing other content away. """
        if elem.tag == 'Spacing':
            size = int(elem.attrib.get('size', 1))
            log.debug(f'{" "*indent}Spacing(size={size})')
            parent.layout().addStretch(size)
            return True

    def _tag_stretch(self, elem, parent, indent):
        """ Adds a stretch tag to the layout, pushing other content away. """
        if elem.tag == 'Stretch':
            ratio = int(elem.attrib.get('ratio', 1))
            log.debug(f'{" "*indent}Stretch(ratio={ratio})')
            parent.layout().addStretch(ratio)
            return True
    
    def _tag_connect(self, elem, parent, indent):
        """ Reads attributes of a Connect tag, and sets the callback
            for the specified attribute name to self.<value>().
        """
        if elem.tag == 'Connect':
            for attr, valuestr in elem.attrib.items():
                callback = utils.rget(self, valuestr)
                getattr(parent, attr).connect(callback)
            return True

    def _apply_attrs(self, qobj, elem, indent=0):
        """ Applies attributes of elem to qobj. """
        for attr, valuestr in elem.attrib.items():
            if attr == 'args': continue
            value = self._parse_value(valuestr)
            if self._attr_id(qobj, attr, value, valuestr, indent): continue             # id='myobject'
            if self._attr_layout(qobj, attr, value, valuestr, indent): continue         # layout.<attr>='value'
            if self._attr_set(qobj, attr, value, valuestr, indent): continue            # attr='value'
            raise Exception(f"Unknown attribute '{attr}' on element {elem.tag}.")

    def _attr_id(self, qobj, attr, value, valuestr, indent):
        """ Saves a reference to qobj as self.ids.<value> """
        if attr.lower() == 'id':
            qobj.setObjectName(value)
            self.ids[value] = qobj
            return True
    
    def _attr_layout(self, qobj, attr, value, valuestr, indent):
        """ Sets the layout or layout.property(). Also reads the DEFAULT_LAYOUT_*
            properties on the class and applies those if specified.
        """
        if attr == 'layout':
            self._attr_set(qobj, attr, value, valuestr, indent)
            if self.DEFAULT_LAYOUT_MARGINS is not None:
                qobj.layout().setContentsMargins(*self.DEFAULT_LAYOUT_MARGINS)
            if self.DEFAULT_LAYOUT_SPACING is not None:
                qobj.layout().setSpacing(self.DEFAULT_LAYOUT_SPACING)
            return True
        if attr.startswith('layout.'):
            return self._attr_set(qobj.layout(), attr[7:], value, valuestr, indent)

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
        if value.split('.')[0] in QOBJECTS:
            value = utils.rget(QOBJECTS, value)
            return value() if callable(value) else value
        # if value.startswith('Qt.'): return getattr(Qt, value[3:])
        if value.lower() in ['true']: return True
        if value.lower() in ['false']: return False
        if value.lower() in ['none']: return None
        if re.findall(REGEX_INT, value): return int(value)
        if re.findall(REGEX_FLOAT, value): return float(value)
        if re.findall(REGEX_LIST, value):
            if value == '[]': return []
            return [self._parse_value(x.strip()) for x in value.strip('[]').split(',')]
        return value
