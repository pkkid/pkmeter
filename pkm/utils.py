# -*- coding: utf-8 -*-
import pkgutil
import re
from pkm import log
from PySide6.QtWidgets import QApplication
from string import Template

REGEX_INT = re.compile(r'^\d+$')
REGEX_FLOAT = re.compile(r'^\d+\.\d+$')
REGEX_STRING = re.compile(r'^".+?"$')
START_LIST, END_LIST, REGEX_LIST = '[', ']', re.compile(r'^\[.*?\]$')
START_TUPLE, END_TUPLE, REGEX_TUPLE = '(', ')', re.compile(r'^\(.*?\)$')
EMPTY_LIST, EMPTY_TUPLE = f'{START_LIST}{END_LIST}', f'{START_TUPLE}{END_TUPLE}'
OPS = {
    '&': lambda a, b: a & b,
    '|': lambda a, b: a | b,
    '||': lambda a, b: a or b,
}


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


def evaluate(expr, context=None, call=True):
    """ Evaluate a given expression and return the result. Supports the operators
        and, or, add, sub, mul, div. Attempts to infer values types based on simple
        rtegex patterns. Supports types None, Bool, Int, Float. Will reference
        context and replace strings with their context counterparts. Order of
        operations is NOT supported.
    """
    if re.findall(REGEX_LIST, expr):
        if expr == EMPTY_LIST: return list()
        return list(evaluate(x.strip(), context) for x in expr.strip('[]').split(','))
    if re.findall(REGEX_TUPLE, expr):
        if expr == EMPTY_TUPLE: return tuple()
        return tuple(evaluate(x.strip(), context) for x in expr.strip('()').split(','))
    tokens = tokenize(expr, OPS)
    tokens = parse_values(tokens, context, call)
    while len(tokens) > 1:
        tokens = [OPS[tokens[1]](tokens[0], tokens[2])] + tokens[3:]
    return tokens[0]


def tokenize(expr, ops=OPS):
    """ Tokenize a given expression into a list of tokens. """
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


def parse_values(tokens, context=None, call=True):
    """ Parse the values of a list of tokens and return the updated list. """
    context = context or {}
    for i in range(len(tokens)):
        if tokens[i].split('.')[0] in context:
            tokens[i] = rget(context, tokens[i])
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
