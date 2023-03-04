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
import io
import tokenize
from os.path import abspath, basename
from pkm import base, log, plugins, utils
from PySide6 import QtCore, QtWidgets
from xml.etree import ElementTree


class QTemplateWidget(QtWidgets.QWidget):
    """ My interpreation of a less verbose Qt Template language. """
    TMPL = None                         # Filepath of tmpl file to load
    TMPLSTR = None                      # String template (if not using a file)
    
    def __init__(self, *args, **kwargs):
        super(QTemplateWidget, self).__init__(*args, **kwargs)
        self.app = QtCore.QCoreApplication.instance()
        self.filepath = None            # Filepath of tmpl file (for relative imports)
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
        context = dict(self=self)
        self._walk(root, context=context)
        self._loading = False
    
    def _walk(self, elem, parent=None, context=None, indent=0):
        """ Parse the specified element and it's children. """
        if self.app.opts.verbose:
            log.info(f'{" "*indent}<{elem.tag} {" ".join(elem.attrib.keys())}>')
        if self._tagQobject(elem, parent, context, indent): return    # <QWidget attr='value' />; then recurse further
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
            # Check this is a QTemplateTag
            if issubclass(qcls, base.QTemplateTag):
                qobj = qcls(self, elem, parent, context, *args)
                self._applyAttrs(qobj, elem, context, indent+1)
                return True
            # Create and add the QWidget to it's parent layout
            qobj = self if parent is None else qcls(*args, parent=parent)
            self._applyAttrs(qobj, elem, context, indent+1)
            if parent and parent.layout() is not None:
                parent.layout().addWidget(qobj)
            for echild in elem:
                self._walk(echild, qobj, context, indent+1)
            return True
    
    # def _tagCustom(self, elem, parent, context, indent):
    #     """ Repeater element repeats child elements. """
    #     for cls in Repeater, StyleSheet, DropShadow:
    #         if elem.tag == cls.__name__:
    #             args = self._attrArgs(elem, context, indent)
    #             qobj = cls(self, elem, parent, context, *args)
    #             self._applyAttrs(qobj, elem, context, indent+1)
    #             return True
    
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
            for attr, expr in elem.attrib.items():
                callback = utils.rget(self, expr)
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
        for attr, expr in elem.attrib.items():
            expr = expr.strip()
            if attr == 'args': continue                                                     # Ignore args; read earlier
            if attr.startswith('_'): continue                                               # Ignore attrs with underscore
            if self._attrId(qobj, elem, attr, expr, context, indent): continue          # id='myobject'
            if self._attrClass(qobj, elem, attr, expr, context, indent): continue       # class=primarybutton
            if self._attrPadding(qobj, elem, attr, expr, context, indent): continue     # padding=setContentsMargins
            if self._attrSpacing(qobj, elem, attr, expr, context, indent): continue     # spacing=layout().setSpacing
            if self._attrLayout(qobj, elem, attr, expr, context, indent): continue      # layout.<attr>='value'
            if self._attrSet(qobj, elem, attr, expr, context, indent): continue         # attr='value'
            raise Exception(f"Unknown attribute '{attr}' on element {elem.tag}.")

    def _attrArgs(self, elem, context, indent):
        """ Reads the args attribute before creating the qobject. """
        if 'args' in elem.attrib:
            expr = elem.attrib['args']
            args = self._evaluate(expr, context)
            return [args] if not isinstance(args, (list,tuple)) else args
        return ()

    def _attrId(self, qobj, elem, attr, expr, context, indent=0):
        """ Saves a reference to qobj as self.ids.<value> """
        if attr.lower() == 'id':
            qobj.setObjectName(expr)
            self.ids[expr] = qobj
            return True
    
    def _attrClass(self, qobj, elem, attr, expr, context, indent=0):
        """ Saves a reference to qobj as self.ids.<value> """
        if attr.lower() == 'class':
            qobj.setProperty('class', expr)
            return True
    
    def _attrPadding(self, qobj, elem, attr, expr, context, indent=0):
        """ Sets contentsMargin on the layout. """
        if attr.lower() == 'padding':
            value = self._evaluate(expr, context)
            if isinstance(value, int): value = (value,) * 4
            elif len(value) == 2: value = value * 2
            qobj.layout().setContentsMargins(*value)
            return True
    
    def _attrSpacing(self, qobj, elem, attr, expr, context, indent=0):
        """ Sets contentsMargin on the layout. """
        if attr.lower() == 'spacing':
            value = self._evaluate(expr, context)
            qobj.layout().setSpacing(value)
            return True
    
    def _attrLayout(self, qobj, elem, attr, expr, context, indent=0):
        """ Sets the layout or layout.property(). Also reads the DEFAULT_LAYOUT_*
            properties on the class and applies those if specified.
        """
        if attr == 'layout':
            self._attrSet(qobj, elem, attr, expr, context, indent=0)
            return True
        if attr.startswith('layout.'):
            self._attrSet(qobj.layout(), elem, attr[7:], expr, context, indent)
            return True

    def _attrSet(self, qobj, elem, attr, expr, context, indent=0):
        """ Calls set<attr>(<value>) on the qbject. """
        setattr = f'set{attr[0].upper()}{attr[1:]}'
        if hasattr(qobj, setattr):
            callback = getattr(qobj, setattr)
            self._apply(expr, context, callback)
            return True
    
    def _apply(self, expr, context, callback):
        """ Apply the specified expr to callback. """
        value = self._evaluate(expr, context, callback)
        if expr.startswith('(') or expr.startswith('['):
            return callback(*value)
        return callback(value)

    def _evaluate(self, expr, context, callback=None):
        """ Evaluate a given expression and return the result. Supports the operators
            and, or, add, sub, mul, div. Attempts to infer values types based on simple
            rtegex patterns. Supports types None, Bool, Int, Float. Will reference
            context and replace strings with their context counterparts. Order of
            operations is NOT supported.
        """
        try:
            fullcontext = utils.Bunch(**context, **plugins.widgets())
            result = eval(expr, fullcontext)
            if self._loading:
                self._registerTokens(expr, context, callback)
            return result
        except Exception:
            return expr
    
    def _registerTokens(self, expr, context, callback=None):
        """ Check we need to register any of the specified tokens in the datastore. """
        try:
            current = []
            readline = io.BytesIO(expr.encode('utf8')).readline
            for token in tokenize.tokenize(readline):
                if token.type == tokenize.NAME or (token.type == tokenize.OP and token.string == '.'):
                    current.append(token.string)
                elif len(current) >= 3 and current[0] == 'data':
                    token = ''.join(current)[5:]
                    self.app.data._register(self, token, callback, expr, context)
                    current = []
        except Exception:
            log.error(f'Error registering tokens for expr {expr}', exc_info=True)
