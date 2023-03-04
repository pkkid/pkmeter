# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import utils
from pkm.base import QTemplateTag
from PySide6 import QtCore, QtGui, QtWidgets


class DropShadow(QTemplateTag):
    """ Applies a dropshadow to the parent element. """
    
    def __init__(self, qtmpl, elem, parent, context, *args):
        # Read the args (x, y, blur, opacity{0-255})
        x = args[0] if len(args) >= 1 else 0
        y = args[1] if len(args) >= 2 else 0
        blur = args[2] if len(args) >= 3 else 0
        opacity = args[3] if len(args) >= 4 else 255
        # Create the shadow effect and apply it to parent
        # We save the effect object to parent so it's not garbage collected
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setOffset(x, y)
        shadow.setBlurRadius(blur)
        shadow.setColor(QtGui.QColor(0, 0, 0, opacity))
        parent.setGraphicsEffect(shadow)
        parent._dropshadow = shadow  # icky
        # Set grandparent's margins to allow space for dropshadow
        parent.parent().setContentsMargins(*[max(x,y)+blur]*4)


class Repeater(QTemplateTag):
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


class StyleSheet(QTemplateTag):
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
