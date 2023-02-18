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
from os.path import basename
from pkm import log, plugins, utils
from pkm.datastore import DataStore
from PySide6 import QtWidgets
from xml.etree import ElementTree

# Define tokens for parsing values in templates
REGEX_INT = re.compile(r'^\d+$')
REGEX_FLOAT = re.compile(r'^\d+\.\d+$')
REGEX_STRING = re.compile(r'^".+?"$')
START_LIST, END_LIST, REGEX_LIST = '[', ']', re.compile(r'^\[.*?\]$')
START_TUPLE, END_TUPLE, REGEX_TUPLE = '(', ')', re.compile(r'^\(.*?\)$')
EMPTY_LIST, EMPTY_TUPLE = f'{START_LIST}{END_LIST}', f'{START_TUPLE}{END_TUPLE}'
OPS = {
    '&': lambda a, b: a & b,
    '+': lambda a, b: a + b,
    '|': lambda a, b: a | b,
    '||': lambda a, b: a or b,
}


class QTemplateWidget(QtWidgets.QWidget):
    """ My interpreation of a less verbose Qt Template language. """
    TMPL = None  # filepath of tmpl file to load
    TMPLSTR = None   # string template (if not using a file)
    DEFAULT_LAYOUT_MARGINS = None  # default values for qobj.layout().setContentsMargins()
    DEFAULT_LAYOUT_SPACING = None  # default values for qobj.layout().setSpacing()
    
    def __init__(self, *args, **kwargs):
        super(QTemplateWidget, self).__init__(*args, **kwargs)
        self.data = DataStore()         # Data store can register and apply updates to the ui
        self.ids = utils.Bunch()
        self._loading = True            # Set False after initial objects loaded
        self._initData()
        self._load()

    def _initData(self):
        """ Abstract method to initia DataStore with items. """
        pass

    def _load(self, filepath=TMPL):
        """ Reads the template and walks the xml tree to build the Qt UI. """
        if self.TMPL is not None:
            log.debug(f'Reading {basename(self.TMPL)} for {self.__class__.__name__}')
            root = ElementTree.parse(self.TMPL).getroot()
        elif self.TMPLSTR is not None:
            log.debug(f'Reading template for {self.__class__.__name__}')
            root = ElementTree.fromstring(self.TMPLSTR)
        context = dict(**plugins.widgets(), **{'self':self})
        self._walk(root, context=context)
        self._loading = False
        self.data._loading = None
    
    def _walk(self, elem, parent=None, context=None, indent=0):
        if self._tagQobject(elem, parent, context, indent): return    # <QWidget attr='value' />
        if self._tagRepeater(elem, parent, context, indent): return   # Check this is a repeater
        if self._tagSet(elem, parent, context, indent): return        # <set attr='value' />; no children
        if self._tagAdd(elem, parent, context, indent): return        # add<Tag>(attr=value)
        if self._tagConnect(elem, parent, context, indent): return    # <connect slot='callback' />; no children
        raise Exception(f'Unknown tag "{elem.tag}" in element {parent.__class__.__name__}.')
    
    def _tagRepeater(self, elem, parent, context, indent):
        if elem.tag == Repeater.__name__:
            qobj = Repeater(self, elem, parent, context)
            self._applyAttrs(qobj, elem, context, indent+1)
            return True

    def _tagQobject(self, elem, parent, context, indent):
        """ Creates a QObject and appends it to the layout of parent. """
        if elem.tag in context:
            qcls = utils.rget(context, elem.tag)
            args = self._attrArgs(elem, context, indent)
            qobj = self if parent is None else qcls(*args, parent=parent)
            log.debug(f'{" "*indent}{qobj.__class__.__name__}')
            self._applyAttrs(qobj, elem, context, indent+1)
            if parent is not None:
                parent.layout().addWidget(qobj)
            # Keep iterating the template
            for echild in elem:
                self._walk(echild, qobj, context, indent+1)
            return True
    
    def _tagAdd(self, elem, parent, context, indent):
        """ Check we're adding an attribute to the parent. """
        addfunc = f'add{elem.tag}'
        callback = getattr(parent, addfunc, getattr(parent.layout(), addfunc, None))
        if callback:
            args = self._attrArgs(elem, context, indent)
            log.debug(f'{" "*indent}{addfunc}(*{args})')
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
            if attr == 'args': continue
            if attr.startswith('_'): continue
            value = self._evaluate(valuestr, context)
            if self._attrId(qobj, elem, attr, context, value, indent): continue      # id='myobject'
            if self._attrLayout(qobj, elem, attr, context, value, indent): continue  # layout.<attr>='value'
            if self._attrSet(qobj, elem, attr, context, value, indent): continue     # attr='value'
            raise Exception(f"Unknown attribute '{attr}' on element {elem.tag}.")

    def _attrArgs(self, elem, context, indent):
        args = elem.attrib.get('args', '()')
        args = self._evaluate(args, context)
        return [args] if not isinstance(args, (list,tuple)) else args

    def _attrId(self, qobj, elem, attr, context, value, indent=0):
        """ Saves a reference to qobj as self.ids.<value> """
        if attr.lower() == 'id':
            log.debug(f'{" "*indent}setObjectName({value})')
            qobj.setObjectName(value)
            self.ids[value] = qobj
            return True
    
    def _attrLayout(self, qobj, elem, attr, context, value, indent=0):
        """ Sets the layout or layout.property(). Also reads the DEFAULT_LAYOUT_*
            properties on the class and applies those if specified.
        """
        if attr == 'layout':
            self._attrSet(qobj, elem, attr, context, value, indent=0)
            if self.DEFAULT_LAYOUT_MARGINS is not None:
                qobj.layout().setContentsMargins(*self.DEFAULT_LAYOUT_MARGINS)
            if self.DEFAULT_LAYOUT_SPACING is not None:
                qobj.layout().setSpacing(self.DEFAULT_LAYOUT_SPACING)
            return True
        if attr.startswith('layout.'):
            return self._attrSet(qobj.layout(), elem, attr[7:], context, value, indent)

    def _attrSet(self, qobj, elem, attr, context, value, indent=0):
        """ Calls set<attr>(<value>) on the qbject. """
        setattr = f'set{attr[0].upper()}{attr[1:]}'
        if self._loading:
            self.data._loading = self, qobj, elem, attr, context
        if hasattr(qobj, setattr):
            log.debug(f'{" "*indent}{setattr}({elem.attrib.get(attr,"")})')
            if isinstance(value, (list, tuple)):
                getattr(qobj, setattr)(*value)
                return True
            getattr(qobj, setattr)(value)
            return True

    def _evaluate(self, expr, context=None, call=True):
        """ Evaluate a given expression and return the result. Supports the operators
            and, or, add, sub, mul, div. Attempts to infer values types based on simple
            rtegex patterns. Supports types None, Bool, Int, Float. Will reference
            context and replace strings with their context counterparts. Order of
            operations is NOT supported.
        """
        if re.findall(REGEX_LIST, expr):
            if expr == EMPTY_LIST: return list()
            return list(self._evaluate(x.strip(), context) for x in expr.strip('[]').split(','))
        if re.findall(REGEX_TUPLE, expr):
            if expr == EMPTY_TUPLE: return tuple()
            return tuple(self._evaluate(x.strip(), context) for x in expr.strip('()').split(','))
        tokens = utils.tokenize(expr, OPS)
        tokens = self._parseValues(tokens, context, call)
        while len(tokens) > 1:
            tokens = [OPS[tokens[1]](tokens[0], tokens[2])] + tokens[3:]
        return tokens[0]
    
    def _parseValues(self, tokens, context=None, call=True):
        """ Parse the values of a list of tokens and return the updated list. """
        context = context or {}
        for i in range(len(tokens)):
            if tokens[i].split('.')[0] in context:
                tokens[i] = utils.rget(context, tokens[i])
            elif tokens[i].lower() in ('yes', 'true'): tokens[i] = True
            elif tokens[i].lower() in ('no', 'false'): tokens[i] = False
            elif tokens[i].lower() in ('null', 'none'): tokens[i] = None
            elif re.findall(REGEX_INT, tokens[i]): tokens[i] = int(tokens[i])
            elif re.findall(REGEX_FLOAT, tokens[i]): tokens[i] = float(tokens[i])
            elif re.findall(REGEX_STRING, tokens[i]): tokens[i] = tokens[i][1:-1]
            # Build the object or call the function
            if call and callable(tokens[i]):
                tokens[i] = tokens[i]()
        return tokens


class Repeater:
    """ Widget-like object used for repeatng child elements in QTemplate.
        <Repeater for='i in 3'>...</Repeater>
    """

    def __init__(self, qtmpl, elem, parent, context):
        self.qtmpl = qtmpl          # Ref to parent QTemplateWidget object
        self.elem = elem            # Current etree item to render children
        self.parent = parent        # Parent qobj to add children to
        self.context = context      # Context for building the children
    
    def setFor(self, valuestr):
        """ Rebuild the children elements on the parent. """
        # Delete all children of the parent
        utils.deleteChildren(self.parent)
        # Build the new template objects
        varname, iterstr = [x.strip() for x in valuestr.split(' in ')]
        value = self.qtmpl._evaluate(iterstr, self.context)
        if isinstance(value, str):
            raise Exception(f"Lookup iterstr '{iterstr}' failed.")
        iter = range(value) if isinstance(value, int) else value
        for item in iter:
            for echild in self.elem:
                subcontext = dict(**self.context, **{varname:item})
                self.qtmpl._walk(echild, self.parent, subcontext)
