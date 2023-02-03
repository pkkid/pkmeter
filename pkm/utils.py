# -*- coding: utf-8 -*-


class Bunch(dict):
    """ Allows dot notation to set and get dict values. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


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
