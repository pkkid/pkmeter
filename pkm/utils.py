# -*- coding: utf-8 -*-
import operator as op
import pkgutil
import re
from pkm import log
from PySide6.QtWidgets import QApplication
from string import Template

REGEX_INT = re.compile(r'^\d+$')
REGEX_FLOAT = re.compile(r'^\d+\.\d+$')
START_LIST, END_LIST, REGEX_LIST = '[', ']', re.compile(r'^\[.*?\]$')
START_TUPLE, END_TUPLE, REGEX_TUPLE = '(', ')', re.compile(r'^\(.*?\)$')
EMPTY_LIST, EMPTY_TUPLE = f'{START_LIST}{END_LIST}', f'{START_TUPLE}{END_TUPLE}'
OPS = {'|':op.or_, '&':op.and_, '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv}


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


def render(tmplstr, context=None):
    """ Read variables from the file. Poor mans template with constants. """
    tmplvars = dict(re.findall(r"\$(\w+)\s*\=\s*'(.+?)'", tmplstr))
    context = context if context else {}
    context.update(tmplvars)
    return Template(tmplstr).substitute(context)


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
    tokens = tokenize_expression(expr)
    tokens = parse_values(tokens, context, call)
    while len(tokens) > 1:
        tokens = [OPS[tokens[1]](tokens[0], tokens[2])] + tokens[3:]
    return tokens[0]


def tokenize_expression(expr):
    """ Tokenize a given expression into a list of tokens. """
    tokens = []
    current_token = ''
    for char in expr:
        if char in OPS.keys():
            if current_token:
                tokens.append(current_token.strip())
                current_token = ''
            tokens.append(char)
            continue
        current_token += char
    if current_token:
        tokens.append(current_token.strip())
    return [t for t in tokens if t]


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
        # Build the object or call the function
        if call and callable(tokens[i]):
            tokens[i] = tokens[i]()
    return tokens
