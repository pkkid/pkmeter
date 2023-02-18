# -*- coding: utf-8 -*-
import re
from pkm import log
from PySide6.QtWidgets import QApplication
from string import Template


class Bunch(dict):
    """ Allows dot notation to set and get dict values. """
    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            return None

    def __setattr__(self, item, value):
        return self.__setitem__(item, value)


def centerWindow(window):
    """ Move the specified widget to the center of the screen. """
    screen = QApplication.primaryScreen()
    screen_rect = screen.availableGeometry()
    window_rect = window.geometry()
    x = (screen_rect.width() - window_rect.width()) / 2
    y = (screen_rect.height() - window_rect.height()) / 2
    window.move(x, y)


def setPropertyAndRedraw(qobj, name, value):
    """ After setting a property on a QtWidget, redraw it. """
    qobj.setProperty(name, value)
    qobj.style().unpolish(qobj)
    qobj.style().polish(qobj)
    qobj.update()


def deleteChildren(qobj):
    """ Delete all children of the specified QObject. """
    if hasattr(qobj, 'clear'):
        return qobj.clear()
    layout = qobj.layout()
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
        else:
            deleteChildren(item.layout())


def render(tmplstr, context=None):
    """ Read variables from the file. Poor mans template with constants. """
    tmplvars = dict(re.findall(r"\$(\w+)\s*\=\s*'(.+?)'", tmplstr))
    context = context if context else {}
    context.update(tmplvars)
    return Template(tmplstr).substitute(context)


def rget(obj, attrstr, default=None, delim='.'):
    """ Recursively get a value from a nested dictionary. """
    try:
        parts = attrstr.split(delim, 1)
        attr = parts[0]
        substr = parts[1] if len(parts) == 2 else None
        if isinstance(obj, dict): value = obj[attr]
        elif isinstance(obj, list): value = obj[int(attr)]
        elif isinstance(obj, tuple): value = obj[int(attr)]
        elif isinstance(obj, object): value = getattr(obj, attr)
        if substr: return rget(value, substr, default, delim)
        return value
    except Exception as err:
        log.warning(err)
        return default


def rset(obj, attrstr, value, delim='.'):
    """ Recursively set a value to a nested dictionary. """
    parts = attrstr.split(delim, 1)
    attr = parts[0]
    attrstr = parts[1] if len(parts) == 2 else None
    if attrstr and not isinstance(getattr(obj, attr), Bunch):
        obj[attr] = Bunch()
    if attrstr:
        rset(obj[attr], attrstr, value)
        return
    obj[attr] = value


def tokenize(expr, ops):
    """ Tokenize a given expression into a list of tokens.
        expr (str): The expression to tokenize.
        ops (dict{op:func}): Dict of operator strings and their resolving function.
    """
    tokens = []
    token, i = '', 0
    while i < len(expr):
        for op in sorted(ops, key=len, reverse=True):
            if expr[i:].startswith(op):
                tokens.append(token)
                tokens.append(op)
                token = ''
                i += len(op)
                continue
        token += expr[i]
        i += 1
    if token:
        tokens.append(token.strip())
    return [t.strip() for t in tokens if t]
