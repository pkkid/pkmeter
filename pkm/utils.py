# -*- coding: utf-8 -*-
import pkgutil
from pkm import log
from PySide6.QtWidgets import QApplication


class Bunch(dict):
    """ Allows dot notation to set and get dict values. """
    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            return None

    def __setattr__(self, item, value):
        return self.__setitem__(item, value)


def center_window(window):
    """ Move the specified widget to the center of the screen. """
    screen = QApplication.primaryScreen()
    screen_rect = screen.availableGeometry()
    window_rect = window.geometry()
    x = (screen_rect.width() - window_rect.width()) / 2
    y = (screen_rect.height() - window_rect.height()) / 2
    window.move(x, y)


def clean_name(name):
    """ Clean the specified name of non-variable characters. """
    return "".join(c for c in name.lower() if c.isalnum() or c == "_")


def load_modules(dirpath):
    """ Load and return modules in the specified directory. """
    modules = []
    for loader, name, ispkg in pkgutil.iter_modules([dirpath]):
        try:
            modules.append(loader.find_module(name).load_module(name))
        except Exception as err:
            log.warn('Error loading module %s: %s', name, err)
            log.debug(err, exc_info=1)
    return modules


def setPropertyAndRedraw(qobj, name, value):
    """ After setting a property on a QtWidget, redraw it. """
    qobj.setProperty(name, value)
    qobj.style().unpolish(qobj)
    qobj.style().polish(qobj)
    qobj.update()


def rget(obj, attrstr, default='_raise', delim='.'):
    """ Recursively get a value from a nested dictionary. """
    try:
        parts = attrstr.split(delim, 1)
        attr = parts[0]
        attrstr = parts[1] if len(parts) == 2 else None
        if isinstance(obj, dict): value = obj[attr]
        elif isinstance(obj, list): value = obj[int(attr)]
        elif isinstance(obj, tuple): value = obj[int(attr)]
        elif isinstance(obj, object): value = getattr(obj, attr)
        if attrstr: return rget(value, attrstr, default, delim)
        return value
    except Exception:
        if default == '_raise': raise
        return default


# def get_workareas(app):
#     # https://stackoverflow.com/a/52698010
#     dw = app.desktop()  # dw = QDesktopWidget() also works if app is created
#     taskbar_height = dw.screenGeometry().height() - dw.availableGeometry().height()
