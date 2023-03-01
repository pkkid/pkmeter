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
import re
from collections import namedtuple
from os.path import abspath, basename, dirname, normpath
from pkm import log, plugins, utils
from pkm.datastore import DataStore
from PySide6 import QtCore, QtWidgets
from xml.etree import ElementTree

# Define entities QTemplateWiget values can parse
Collection = namedtuple('Collection', 'regex, start, end, delim, cast')
Type = namedtuple('Type', 'regex, cast')
COLLECTIONS = [
    Collection(re.compile(r'^\[.*?\]$'), '[', ']', ',', list),
    Collection(re.compile(r'^\(.*?\)$'), '(', ')', ',', tuple),
]
TYPES = [
    Type(re.compile(r'(true|false)', re.IGNORECASE), lambda s: s.lower() == 'true'),
    Type(re.compile(r'(none|null)', re.IGNORECASE), lambda s: None),
    Type(re.compile(r'^\d+$'), int),
    Type(re.compile(r'^\d+\.\d+$'), float),
    Type(re.compile(r'^".+?"$'), lambda s: s[1:-1]),
]
OPERATIONS = {
    '&': lambda a, b: a & b,
    '+': lambda a, b: a + b,
    '|': lambda a, b: a | b,
    '||': lambda a, b: a or b,
}


class QTemplateWidget(QtWidgets.QWidget):
    """ My interpreation of a less verbose Qt Template language. """
    TMPL = None                         # Filepath of tmpl file to load
    TMPLSTR = None                      # String template (if not using a file)
    
    def __init__(self, *args, **kwargs):
        super(QTemplateWidget, self).__init__(*args, **kwargs)
        self.filepath = None            # Filepath of tmpl file (for relative imports)
        self.data = DataStore()         # Datastore can register and apply updates to the ui
        self.ids = utils.Bunch()        # Reference to QObject by id
        self._loading = True            # Set False after initial objects loaded
        self._load()                    # Read the template string and convert to qobjects

    def _load(self):
        """ Reads the template and walks the xml tree to build the Qt UI. """
        if self.TMPL is not None:
            log.debug(f'Reading {basename(self.TMPL)} for {self.__class__.__name__}')
            root = ElementTree.parse(self.TMPL).getroot()
            self.filepath = self.TMPL
        elif self.TMPLSTR is not None:
            log.debug(f'Reading template for {self.__class__.__name__}')
            root = ElementTree.fromstring(self.TMPLSTR)
            self.filepath = abspath(__file__)
        context = dict(self=self, data=self.data)
        self._walk(root, context=context)
        self._loading = False
    
    def _walk(self, elem, parent=None, context=None, indent=0):
        """ Parse the specified element and it's children. """
        log.debug(f'{" "*indent}<{elem.tag} {" ".join(elem.attrib.keys())}>')
        if self._tagQobject(elem, parent, context, indent): return    # <QWidget attr='value' />; then recurse further
        if self._tagCustom(elem, parent, context, indent): return     # Custom tags defined below
        if self._tagSet(elem, parent, context, indent): return        # <set attr='value' />; no children
        if self._tagAdd(elem, parent, context, indent): return        # add<Tag>(attr=value); no children
        if self._tagConnect(elem, parent, context, indent): return    # <connect slot='callback' />; no children
        raise Exception(f'Unknown tag "{elem.tag}" in element {parent.__class__.__name__}.')

    def _tagQobject(self, elem, parent, context, indent):
        """ Creates a QObject and appends it to the layout of parent. """
        qwidgets = plugins.widgets()
        if elem.tag in qwidgets:
            qcls = utils.rget(qwidgets, elem.tag)
            args = self._attrArgs(elem, context, indent)
            qobj = self if parent is None else qcls(*args, parent=parent)
            self._applyAttrs(qobj, elem, context, indent+1)
            if parent is not None:
                parent.layout().addWidget(qobj)
            # Keep iterating the template
            for echild in elem:
                self._walk(echild, qobj, context, indent+1)
            return True
    
    def _tagCustom(self, elem, parent, context, indent):
        """ Repeater element repeats child elements. """
        for cls in Repeater, StyleSheet:
            if elem.tag == cls.__name__:
                args = self._attrArgs(elem, context, indent)
                qobj = cls(self, elem, parent, context, *args)
                self._applyAttrs(qobj, elem, context, indent+1)
                return True
    
    def _tagAdd(self, elem, parent, context, indent):
        """ Check we're adding an attribute to the parent. """
        addfunc = f'add{elem.tag}'
        callback = getattr(parent, addfunc, getattr(parent.layout(), addfunc, None))
        if callback:
            args = self._attrArgs(elem, context, indent)
            callback(*args)
            return True

    def _tagSet(self, elem, parent, context, indent):
        """ Reads attributes of a Set tag and applies values by calling
            set<attr>(<value>) on the parent Qt object.
        """
        if elem.tag.lower() == 'set':
            self._applyAttrs(parent, elem, context, indent)
            return True
    
    def _tagConnect(self, elem, parent, context, indent):
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

    def _applyAttrs(self, qobj, elem, context, indent=0):
        """ Applies attributes of elem to qobj. """
        for attr, valuestr in elem.attrib.items():
            valuestr = valuestr.strip()
            if attr == 'args': continue                                                     # Ignore args; read earlier
            if attr.startswith('_'): continue                                               # Ignore attrs with underscore
            if self._attrId(qobj, elem, attr, valuestr, context, indent): continue          # id='myobject'
            if self._attrPadding(qobj, elem, attr, valuestr, context, indent): continue     # padding=setContentsMargins
            if self._attrSpacing(qobj, elem, attr, valuestr, context, indent): continue     # spacing=layout().setSpacing
            if self._attrLayout(qobj, elem, attr, valuestr, context, indent): continue      # layout.<attr>='value'
            if self._attrSet(qobj, elem, attr, valuestr, context, indent): continue         # attr='value'
            raise Exception(f"Unknown attribute '{attr}' on element {elem.tag}.")

    def _attrArgs(self, elem, context, indent):
        """ Reads the args attribute before creating the qobject. """
        if 'args' in elem.attrib:
            valuestr = elem.attrib['args']
            args = self._evaluate(valuestr, context)
            return [args] if not isinstance(args, (list,tuple)) else args
        return ()

    def _attrId(self, qobj, elem, attr, valuestr, context, indent=0):
        """ Saves a reference to qobj as self.ids.<value> """
        if attr.lower() == 'id':
            qobj.setObjectName(valuestr)
            self.ids[valuestr] = qobj
            return True
    
    def _attrPadding(self, qobj, elem, attr, valuestr, context, indent=0):
        """ Sets contentsMargin on the layout. """
        if attr.lower() == 'padding':
            value = self._evaluate(valuestr, context)
            if isinstance(value, int): value = (value,) * 4
            elif len(value) == 2: value = value * 2
            qobj.layout().setContentsMargins(*value)
            return True
    
    def _attrSpacing(self, qobj, elem, attr, valuestr, context, indent=0):
        """ Sets contentsMargin on the layout. """
        if attr.lower() == 'spacing':
            value = self._evaluate(valuestr, context)
            qobj.layout().setSpacing(value)
            return True
    
    def _attrLayout(self, qobj, elem, attr, valuestr, context, indent=0):
        """ Sets the layout or layout.property(). Also reads the DEFAULT_LAYOUT_*
            properties on the class and applies those if specified.
        """
        if attr == 'layout':
            self._attrSet(qobj, elem, attr, valuestr, context, indent=0)
            return True
        if attr.startswith('layout.'):
            self._attrSet(qobj.layout(), elem, attr[7:], valuestr, context, indent)
            return True

    def _attrSet(self, qobj, elem, attr, valuestr, context, indent=0):
        """ Calls set<attr>(<value>) on the qbject. """
        setattr = f'set{attr[0].upper()}{attr[1:]}'
        if hasattr(qobj, setattr):
            callback = getattr(qobj, setattr)
            self._apply(callback, valuestr, context)
            return True
    
    def _apply(self, callback, valuestr, context):
        """ Apply the specified valuestr to callback. """
        value = self._evaluate(valuestr, context, callback)
        if valuestr.startswith('(') or valuestr.startswith('['):
            return callback(*value)
        return callback(value)

    def _evaluate(self, valuestr, context, callback=None):
        """ Evaluate a given expression and return the result. Supports the operators
            and, or, add, sub, mul, div. Attempts to infer values types based on simple
            rtegex patterns. Supports types None, Bool, Int, Float. Will reference
            context and replace strings with their context counterparts. Order of
            operations is NOT supported.
        """
        for c in COLLECTIONS:
            if re.findall(c.regex, valuestr):
                if valuestr == f'{c.start}{c.end}': return c.cast()
                valuestrs = valuestr.lstrip(c.start).rstrip(c.end).split(c.delim)
                return c.cast(self._evaluate(x.strip(), context, callback) for x in valuestrs)
        tokens = utils.tokenize(valuestr, OPERATIONS)
        self._registerTokens(tokens, valuestr, context, callback)
        values = [self._parse(t, context) for t in tokens]
        while len(values) > 1:
            values = [OPERATIONS[values[1]](values[0], values[2])] + values[3:]
        return values[0]
    
    def _registerTokens(self, tokens, valuestr, context, callback=None):
        """ Check we need to register any of the specified tokens in the datastore. """
        if not self._loading or not callback: return
        tokens = [t[5:] for t in tokens if t.startswith('data.')]
        for token in tokens:
            self.data.register(self, token, callback, valuestr, context)
    
    def _parse(self, token, context=None):
        """ Parse the token string into a value. """
        context = context or {}
        qwidgets = plugins.widgets()
        for lookup in (context, qwidgets):
            if token.split('.')[0] in lookup:
                value = utils.rget(lookup, token)
                return value() if callable(value) else value
        for t in TYPES:
            if re.findall(t.regex, token):
                return t.cast(token)
        return token


class Repeater:
    """ Widget-like object used for repeatng child elements in QTemplate.
        <Repeater for='i' in='3'>...</Repeater>
    """

    def __init__(self, qtmpl, elem, parent, context, *args):
        self.qtmpl = qtmpl          # Ref to parent QTemplateWidget object
        self.elem = elem            # Current etree item to render children
        self.parent = parent        # Parent qobj to add children to
        self.context = context      # Context for building the children
        self.varname = None         # Var name for subcontext
    
    def setFor(self, varname):
        self.varname = varname

    def setIn(self, iterable):
        """ Rebuild the children elements on the parent. """
        if self.varname is None:
            raise Exception('Repeater must specify the attribute for before in.')
        if isinstance(iter, str):
            raise Exception(f"Iterable lookup {iterable} failed.")
        utils.deleteChildren(self.parent)
        for item in iterable:
            for echild in self.elem:
                subcontext = dict(**self.context, **{self.varname:item})
                self.qtmpl._walk(echild, self.parent, subcontext)


class StyleSheet:
    """ Widget-like object used for importing and applying stylesheets.
        <StyleSheet args='<path>' context='<dict>'/>
    """

    def __init__(self, qtmpl, elem, parent, context, *args):
        self.qtmpl = qtmpl          # Ref to parent QTemplateWidget object
        self.elem = elem            # Current etree item to render children
        self.parent = parent        # Parent qobj to add children to
        self.context = context      # Context for building the children
        self.filepath = args[0]     # Relative path to stylesheet (from tmpl)
        if 'context' not in self.elem.attrib:
            self.setContext()

    def setContext(self, context=None):
        context = context or None
        filepath = normpath(f'{dirname(self.qtmpl.filepath)}/{self.filepath}')
        outline = QtCore.QCoreApplication.instance().opts.outline
        utils.setStyleSheet(self.parent, filepath, context, outline)
