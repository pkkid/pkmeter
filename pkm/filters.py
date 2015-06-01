# -*- coding: utf-8 -*-
"""
PKMeter Lexer
"""
import datetime, re
from fractions import Fraction
from pkm import utils

BYTES1024 = ((2**50,'PB'), (2**40,'TB'), (2**30,'GB'), (2**20,'MB'), (2**10,'KB'), (1,'B'))
HERTZ = ((10**12,'THz'), (10**9,'GHz'), (10**6,'MHz'), (10**3,'kHz'), (1,'Hz'))
MILLISECONDS = ((604800000,'wks'), (86400000,'days'), (3600000,'hrs'), (60000,'min'), (1000,'sec'), (1,'ms'))
MS = ((604800000,'w'), (86400000,'d'), (3600000,'h'), (60000,'m'), (1000,'s'), (1,'ms'))


filters = {}
def register_filter(name=None):  # NOQA
    def wrap1(func):
        regname = name if name else func.__name__
        filters[regname] = func
        def wrap2(*args, **kwargs):  # NOQA
            return func(*args, **kwargs)
        return wrap2
    return wrap1


def _value_to_str(value, units, precision=0, separator=' '):
    if value is None: return ''
    if isinstance(precision, str): precision = int(precision)
    for div, unit in units:
        if value >= div:
            conversion = round(value / div, int(precision)) if precision else int(value / div)
            return '%s%s%s' % (conversion, separator, unit)
    return '0%s%s' % (separator, unit)


@register_filter()
def bytes_to_str(value, precision=0):
    return _value_to_str(value, BYTES1024, precision)


@register_filter()
def celsius_to_fahrenheit(value):
    return int(value * 9 / 5 + 32)


@register_filter()
def date(value, formatstr='%Y-%m-%d'):
    return value.strftime(formatstr)


@register_filter()
def default(value, default_value):
    return default_value if value is None else value


@register_filter()
def degrees_to_direction(value):
    if value is None: return 'NA'
    directions = ['North', 'NE', 'East', 'SE', 'South', 'SW', 'West', 'NW', 'North']
    return directions[round(float(value) / 45)]


@register_filter()
def fahrenheit_to_celsius(value):
    return int((value - 32) / 1.8)


@register_filter()
def format_date(value, formatstr='%Y-%m-%d %-I:%M %p'):
    if value is None: return ''
    return value.strftime(formatstr)


@register_filter()
def format_timestamp(value, formatstr='%Y-%m-%d %-I:%M %p'):
    if value is None: return ''
    value = utils.to_int(value, 0)
    if value > 9999999999: value /= 1000
    value = datetime.datetime.fromtimestamp(value)
    return value.strftime(formatstr)


@register_filter()
def format_str(value, formatstr):
    return formatstr % value


@register_filter()
def int_comma(value):
    if value is None: return ''
    return '{:,}'.format(value)


@register_filter()
def invert(value):
    return not value


@register_filter()
def join(value, delim=','):
    if value is None: return ''
    return delim.join([str(v) for v in value])


@register_filter()
def length(value):
    if value is None: return 0
    elif isinstance(value, dict): return 1
    return len(value)


@register_filter()
def lower(value):
    if value is None: return ''
    return value.lower()


@register_filter()
def megabytes_to_str(value, precision=0):
    value = value or 0
    return _value_to_str(value * 1048576, BYTES1024, precision)


@register_filter()
def milliseconds_to_str(value, precision=1, separator=' '):
    return _value_to_str(value, MILLISECONDS, precision)


@register_filter()
def pluralize(value, arg=',s'):
    if value is None: return ''
    one, many = arg.split(',')
    count = value if isinstance(value, int) else len(value)
    return one if count == 1 else many


@register_filter('round')
def round_(value, places=0):
    if value is None: return ''
    if places == 0:
        return int(round(value, places))
    return round(value, places)


@register_filter()
def seconds_to_str(value, precision=1):
    return _value_to_str(value*1000, MILLISECONDS, precision)


@register_filter()
def seconds_to_str_short(value, precision=0):
    return _value_to_str(value*1000, MS, precision, separator='')


@register_filter()
def time_ago(value, precision=1):
    if not value: return ''
    seconds = (datetime.datetime.now() - value).total_seconds()
    return seconds_to_str(seconds, precision)


@register_filter()
def timestamp_ago(value, precision=1):
    if value is None: return ''
    value = utils.to_int(value, 0)
    if value > 9999999999: value /= 1000
    value = datetime.datetime.fromtimestamp(value)
    seconds = (datetime.datetime.now() - value).total_seconds()
    return seconds_to_str(seconds, precision)


@register_filter()
def time_ago_short(value, precision=0):
    if not value: return ''
    seconds = (datetime.datetime.now() - value).total_seconds()
    return seconds_to_str_short(seconds, precision)


@register_filter()
def to_fraction(value):
    if not value: return ''
    return str(Fraction(value).limit_denominator())


@register_filter()
def to_int(value, default='na'):
    if value is None: return 0
    match = re.findall('^-*\d+', str(value))
    return int(match[0]) if match else default
