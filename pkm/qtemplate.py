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

1. If the attribute is "args", the value(s) will be parsed and passed
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
from copy import deepcopy
from os.path import basename, normpath
from pkm import APPNAME, ROOT, log, utils
from pkm.datastore import DataStore
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt
from xml.etree import ElementTree

_GLOBAL_CONTEXT = {}  # Shared context for all QTemplateWidgets


class QTemplateWidget(QtWidgets.QWidget):
    """ My interpreation of a less verbose Qt Template language. """
    TMPL = None  # filepath of tmpl file to load
    TMPLSTR = None   # string template (if not using a file)
    DEFAULT_LAYOUT_MARGINS = None  # default values for qobj.layout().setContentsMargins()
    DEFAULT_LAYOUT_SPACING = None  # default values for qobj.layout().setSpacing()
    
    def __init__(self, *args, **kwargs):
        super(QTemplateWidget, self).__init__(*args, **kwargs)
        self._current = None          # Current elem, attr, qobj applying attrs
        self._data = DataStore()      # Data store can register and apply updates to the ui
        self.ids = utils.Bunch()
        self.load_template()
        
    def load_template(self, filepath=TMPL):
        """ Reads the template and walks the xml tree to build the Qt UI. """
        if self.TMPL is not None:
            log.debug(f'Reading {basename(self.TMPL)} for {self.__class__.__name__}')
            root = ElementTree.parse(self.TMPL).getroot()
        elif self.TMPLSTR is not None:
            log.debug(f'Reading template for {self.__class__.__name__}')
            root = ElementTree.fromstring(self.TMPLSTR)
        context = self._init_context()
        self._walk_elem(root, context=context)

    def _init_context(self):
        """ Create a lookup to convert xml string to Qt objects. """
        global _GLOBAL_CONTEXT
        if not _GLOBAL_CONTEXT:
            log.debug('Building QTemplateWidget context')
            _GLOBAL_CONTEXT = {'APPNAME':APPNAME, 'Qt':Qt}
            # Load everything within a few modules
            modules = [QtGui, QtWidgets]
            modules += utils.load_modules(normpath(f'{ROOT}/pkm/widgets'))
            for module in modules:
                members = dict(inspect.getmembers(module, inspect.isclass))
                _GLOBAL_CONTEXT.update({k:v for k,v in members.items()})
        return dict(**_GLOBAL_CONTEXT, **{'data':self.data})
    
    @property
    def data(self):
        """ Special data property that can be used in the context that
            registers the current self._obj to be updated each time the
            data attribute value changes.
        """
        log.info('READING DATA')
        if self._current:
            elem, attr, qobj = self._current
            log.info(f'register {elem}, {attr}, {elem.attrib[attr]}, {qobj}')
            # self._data.register()
        return self._data
    
    def _walk_elem(self, elem, parent=None, context=None, indent=0):
        if self._tag_qobject(elem, parent, context, indent): return    # <QWidget attr='value' />
        if self._tag_repeater(elem, parent, context, indent): return   # Check this is a repeater
        if self._tag_set(elem, parent, context, indent): return        # <set attr='value' />; no children
        if self._tag_add(elem, parent, context, indent): return        # add<Tag>(attr=value)
        if self._tag_spacing(elem, parent, context, indent): return    # <spacing size='1' />; no children
        if self._tag_stretch(elem, parent, context, indent): return    # <stretch ratio='1' />; no children
        if self._tag_connect(elem, parent, context, indent): return    # <connect slot='callback' />; no children
        raise Exception(f'Unknown tag "{elem.tag}" in element {parent.__class__.__name__}.')
    
    def _tag_repeater(self, elem, parent, context, indent):
        if elem.tag == 'Repeater':
            qobj = Repeater(self, elem, parent, context)
            qobj.createChildren(indent)
            return True

    def _tag_qobject(self, elem, parent, context, indent):
        """ Creates a QObject and appends it to the layout of parent. """
        if elem.tag in context:
            qcls = utils.rget(context, elem.tag)
            args = self._attr_args(elem, context, indent)
            qobj = self if parent is None else qcls(*args, parent=parent)
            log.debug(f'{" "*indent}{qobj.__class__.__name__}')
            self._apply_attrs(qobj, elem, context, indent+1)
            if parent is not None:
                parent.layout().addWidget(qobj)
            # Keep iterating the template
            for echild in elem:
                self._walk_elem(echild, qobj, context, indent+1)
            return True
    
    def _tag_add(self, elem, parent, context, indent):
        """ Check we're adding an attribute to the parent. """
        addfunc = f'add{elem.tag}'
        if hasattr(parent, addfunc):
            args = self._attr_args(elem, context, indent)
            log.debug(f'{" "*indent}{addfunc}(*{args})')
            getattr(parent, addfunc)(*args)
            return True

    def _tag_set(self, elem, parent, context, indent):
        """ Reads attributes of a Set tag and applies values by calling
            set<attr>(<value>) on the parent Qt object.
        """
        if elem.tag.lower() == 'set':
            self._apply_attrs(parent, elem, context, indent)
            return True
    
    def _tag_spacing(self, elem, parent, context, indent):
        """ Adds a stretch tag to the layout, pushing other content away. """
        if elem.tag == 'Spacing':
            args = self._attr_args(elem, context, indent)
            log.debug(f'{" "*indent}Spacing')
            parent.layout().addSpacing(*args)
            return True

    def _tag_stretch(self, elem, parent, context, indent):
        """ Adds a stretch tag to the layout, pushing other content away. """
        if elem.tag == 'Stretch':
            args = self._attr_args(elem, context, indent)
            log.debug(f'{" "*indent}Stretch')
            parent.layout().addStretch(*args)
            return True
    
    def _tag_connect(self, elem, parent, context, indent):
        """ Reads attributes of a Connect tag, and sets the callback
            for the specified attribute name to self.<value>().
        """
        if elem.tag == 'Connect':
            for attr, valuestr in elem.attrib.items():
                callback = utils.rget(self, valuestr)
                try:
                    # First try connecting to a signal event using via
                    # parent.<signal>.connect(callback)
                    getattr(parent, attr).connect(callback)
                except AttributeError:
                    # If the above fails, we can connect to an event handler
                    # using a temporary function to ensure we always call the
                    # original event handler before calling our own callabck
                    if not attr.endswith('Event'): raise
                    def _eventHandler(*args, **kwargs):  # noqa
                        getattr(super(parent.__class__, parent), attr)(*args, **kwargs)
                        callback(*args, **kwargs)
                    setattr(parent, attr, _eventHandler)
            return True

    def _apply_attrs(self, qobj, elem, context, indent=0):
        """ Applies attributes of elem to qobj. """
        for attr, valuestr in elem.attrib.items():
            if attr == 'args': continue
            value = self._evaluate(valuestr, context)
            if self._attr_id(qobj, elem, attr, value, context, indent): continue      # id='myobject'
            if self._attr_layout(qobj, elem, attr, value, context, indent): continue  # layout.<attr>='value'
            if self._attr_set(qobj, elem, attr, value, context, indent): continue     # attr='value'
            raise Exception(f"Unknown attribute '{attr}' on element {elem.tag}.")

    def _attr_args(self, elem, context, indent):
        args = elem.attrib.get('args', '()')
        args = self._evaluate(args, context)
        return [args] if not isinstance(args, (list,tuple)) else args

    def _attr_id(self, qobj, elem, attr, value, context, indent):
        """ Saves a reference to qobj as self.ids.<value> """
        if attr.lower() == 'id':
            log.debug(f'{" "*indent}setObjectName({value})')
            qobj.setObjectName(value)
            self.ids[value] = qobj
            return True
    
    def _attr_layout(self, qobj, elem, attr, value, context, indent):
        """ Sets the layout or layout.property(). Also reads the DEFAULT_LAYOUT_*
            properties on the class and applies those if specified.
        """
        if attr == 'layout':
            self._attr_set(qobj, elem, attr, value, context, indent)
            if self.DEFAULT_LAYOUT_MARGINS is not None:
                qobj.layout().setContentsMargins(*self.DEFAULT_LAYOUT_MARGINS)
            if self.DEFAULT_LAYOUT_SPACING is not None:
                qobj.layout().setSpacing(self.DEFAULT_LAYOUT_SPACING)
            return True
        if attr.startswith('layout.'):
            return self._attr_set(qobj.layout(), elem, attr[7:], value, context, indent)

    def _attr_set(self, qobj, elem, attr, value, context, indent):
        """ Calls set<attr>(<value>) on the qbject. """
        setattr = f'set{attr[0].upper()}{attr[1:]}'
        if hasattr(qobj, setattr):
            log.debug(f'{" "*indent}{setattr}')
            if isinstance(value, (list, tuple)):
                getattr(qobj, setattr)(*value)
                return True
            getattr(qobj, setattr)(value)
            return True
    
    def _evaluate(self, expr, context):
        """  Evaluate a given expression and return the result. """
        return utils.evaluate(expr, context=context, call=True)


class Repeater:
    """ Widget-like object used for repeatng child elements in QTemplate. """

    def __init__(self, qtmpl, elem, parent, context):
        self.qtmpl = qtmpl
        self.elem = elem
        self.parent = parent
        self.context = context
    
    def createChildren(self, indent=None):
        varname = self.elem.attrib['var']
        valuestr = self.elem.attrib['for']
        value = self.qtmpl._evaluate(valuestr, self.context)
        iter = range(value) if isinstance(value, int) else value
        for x in iter:
            for echild in self.elem:
                subcontext = dict(**self.context, **{varname:x})
                self.qtmpl._walk_elem(echild, self.parent, subcontext, indent)
