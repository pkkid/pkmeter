# -*- coding: utf-8 -*-
import re
import sass
from collections import OrderedDict
from pkm import log
from PySide6 import QtGui
from PySide6.QtWidgets import QApplication


class Bunch(OrderedDict):
    """ Allows dot notation to set and get dict values. """
    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            return None

    def __setattr__(self, item, value):
        return self.__setitem__(item, value)


def centerWindow(qobj):
    """ Move the specified widget to the center of the screen. """
    geometry = qobj.frameGeometry()
    screen = QApplication.screenAt(QtGui.QCursor.pos())
    centerpos = screen.geometry().center()
    geometry.moveCenter(centerpos)
    qobj.move(geometry.topLeft())


def deleteChildren(qobj):
    """ Delete all children of the specified QObject. """
    if hasattr(qobj, 'clear'):
        return qobj.clear()
    layout = qobj.layout()
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget: widget.deleteLater()
        else: deleteChildren(item.layout())


def flattenDataTree(root, path=''):
    """ Given a nested data object, return a flat list of values
        containing (path, value, type).
    """
    if getattr(root, 'items', None) is None:
        return [(path, str(root), typeStr(root))]
    values = []
    for key, value in root.items():
        if key.startswith('_'): continue
        subpath = f'{path}.{key}'.lstrip('.')
        vtype = typeStr(value)
        if isinstance(value, dict):
            values += flattenDataTree(value, subpath)
        elif isinstance(value, (tuple, list)):
            # valuestr = f'<{vtype}: {len(value)} items>'
            # values.append((subpath, valuestr, vtype))
            if len(str(value)) <= 20:
                values.append((subpath, str(value), vtype))
                continue
            for i in range(len(value)):
                values += flattenDataTree(value[i], f'{subpath}.{i}')
        else:
            values.append((subpath, str(value), vtype))
    return sorted(values, key=lambda x: x[0])


def parseValue(value):
    """ Takes a best guess converting to a value from a string. """
    if isinstance(value, list):
        return [parseValue(x) for x in value]
    if value.lower() in ['true']: return True
    if value.lower() in ['false']: return False
    if value.lower() in ['none']: return None
    if re.findall(r'^\d+$', value): return int(value)
    if re.findall(r'^\d+\.\d+$', value): return float(value)
    if re.findall(r'^\[.*?\]$', value):
        return list(parseValue(x.strip()) for x in value.strip('[]').split(','))
    return value


def removeChildren(qobj):
    """ Remove all children in the spcified QObject. """
    layout = qobj.layout()
    for i in reversed(range(layout.count())):
        widget = layout.itemAt(i).widget()
        if widget is not None:
            widget.setVisible(False)
            layout.removeWidget(widget)


def rget(obj, attrstr, default=None, delim='.'):
    """ Recursively get a value from a nested dictionary. """
    try:
        attr, *substr = attrstr.split(delim, 1)
        if isinstance(obj, dict):
            if attr == 'keys()': value = obj.keys()
            elif attr == 'values()': value = obj.values()
            else: value = obj[attr]
        elif isinstance(obj, list): value = obj[int(attr)]
        elif isinstance(obj, tuple): value = obj[int(attr)]
        elif isinstance(obj, object): value = getattr(obj, attr)
        if substr: return rget(value, '.'.join(substr), default, delim)
        return value
    except Exception as err:
        log.warning(err, exc_info=True)
        return default


def rset(obj, attrstr, value, delim='.'):
    """ Recursively set a value to a nested dictionary. """
    parts = attrstr.split(delim, 1)
    attr = parts[0]
    attrstr = parts[1] if len(parts) == 2 else None
    if attrstr and attr not in obj:
        obj[attr] = Bunch() if isinstance(obj, Bunch) else {}
    if attrstr:
        return rset(obj[attr], attrstr, value)
    obj[attr] = value


def setPropertyAndRedraw(qobj, name, value=None):
    """ After setting a property on a QtWidget, redraw it. """
    if value is None and hasattr(qobj, name): delattr(qobj, name)
    elif value is not None: qobj.setProperty(name, value)
    qobj.style().unpolish(qobj)
    qobj.style().polish(qobj)
    qobj.update()


def setStyleSheet(qobj, filepath, context=None, outline=False):
    """ Load the specified stylesheet via libsass and add it to qobj. """
    styles = open(filepath).read()
    styles = sass.compile(string=styles)
    if outline:
        styles += 'QWidget { border:1px solid rgba(255,0,0,0.3) !important; }'
    qobj.setStyleSheet(styles)


def typeStr(value):
    """ Return the type of value as a string. """
    return re.findall(r"(\w+?)\'", str(type(value)))[0].lower()
