# -*- coding: utf-8 -*-
"""
PKMeter Utilites
"""
import datetime, os, re, socket, struct, xmltodict
import shlex, subprocess, threading, queue
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError
from PyQt5 import QtGui, QtWidgets
from pkm import log

DICTTYPES = ['dict', 'ordereddict']
LISTTYPES = ['list', 'set', 'tuple']
SECONDS = (('years',31556926), ('months',2629744), ('weeks',604800),
           ('days',86400), ('hours',3600), ('min',60), ('sec',1))


class Bunch(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def get_stdout(command):
    log.debug('Running command: %s' % command)
    result = subprocess.check_output(shlex.split(command))
    return result.decode('utf8')


def find_parent(widget, id):
    widget = widget.parent
    while widget and widget.id != id:
        widget = widget.parent
    if not widget:
        raise Exception("Parent widget with id '%s' not found." % id)
    return widget


def flatten_datatree(root, path):
    if not getattr(root, 'items', None):
        return [(path, str(root), value_type(root))]
    flatlist = []
    for key, value in root.items():
        subpath = '%s.%s' % (path, key)
        vtype = value_type(value)
        if vtype in DICTTYPES:
            flatlist += flatten_datatree(value, subpath)
        elif vtype in LISTTYPES:
            valuestr = '<%s: %s items>' % (vtype, len(value))
            flatlist.append((subpath, valuestr, vtype))
            for i in range(len(value)):
                flatlist += flatten_datatree(value[i], '%s.%s' % (subpath, i))
        else:
            flatlist.append((subpath, str(value), vtype))
    return sorted(flatlist, key=lambda x: x[0])


def hex_to_qcolor(hexstr):
    hexstr = hexstr.lstrip('#')
    if len(hexstr) == 6:
        return QtGui.QColor(*struct.unpack('BBB', bytes.fromhex(hexstr)))
    elif len(hexstr) == 8:
        return QtGui.QColor(*struct.unpack('BBBB', bytes.fromhex(hexstr)))
    raise Exception('Invalid hexstr format: %s' % hexstr)


def addr_to_ip(addr):
    try:
        socket.inet_aton(addr)
        return True
    except socket.error:
        return False


def http_request(url, data=None, timeout=30):
    log.debug("Requesting URL: %s" % url)
    data = urlencode(data).encode('utf8') if data else None
    try:
        response = urlopen(url, data=data, timeout=timeout)
        return {'success':True, 'response':response, 'url':url}
    except (URLError, socket.timeout) as err:
        log.error("Error requesting URL: %s; %s" % (url, err))
        return {'success':False, 'error':err, 'url':url}


def iter_responses(urls, data=None, timeout=30):
    responses = queue.Queue()
    threads = []
    _req = lambda url, data, timeout: responses.put(http_request(url, data, timeout))
    for url in urls:
        threads.append(threading.Thread(target=_req, args=(url, data, timeout)))
        threads[-1].daemon = True
        threads[-1].start()
    for thread in threads:
        thread.join()
    responses.put(None)
    for response in iter(responses.get, None):
        yield response


def name(module):
    return getattr(module, 'NAME', namespace(module))


def namespace(module):
    if isinstance(module, str):
        return module
    return os.path.basename(module.__file__).split('.')[0]


def natural_time(timedelta, precision=2, default='NA'):
    # Convert timedelta to seconds
    remaining = timedelta
    if isinstance(timedelta, datetime.timedelta):
        remaining = (timedelta.days * 86400) + timedelta.seconds
    # Create and return the natural string
    rtnvals = []
    for name, seconds in SECONDS:
        if remaining > seconds * 2:
            value = int(float(remaining) / float(seconds))
            remaining = remaining - (value * seconds)
            rtnvals.append('%s %s' % (value, name))
            precision -= 1
        if precision <= 0 or remaining <= 0:
            break
    if not rtnvals:
        rtnvals.append('0 %s' % SECONDS[-1][0])
    rtnval = ', '.join(rtnvals)
    return rtnval


def percent(numerator, denominator, precision=2, maxval=999.9, default=0.0):
    if not denominator:
        return default
    return min(maxval, round((numerator / float(denominator)) * 100.0, precision))


def remove_children(widget):
    remove_widget(widget, False)


def remove_widget(widget, delete=True):
    item = widget.layout().takeAt(0)
    while item:
        subwidget = item.widget()
        if subwidget: subwidget.setParent(None)
        item = widget.layout().takeAt(0)
    if delete:
        widget.setParent(None)


def rget(obj, attrstr, default=None, delim='.'):
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
    except:
        return default


def rset(obj, attrstr, value, delim='.'):
    parts = attrstr.split(delim, 1)
    attr = parts[0]
    attrstr = parts[1] if len(parts) == 2 else None
    if attr not in obj: obj[attr] = {}
    if attrstr: rset(obj[attr], attrstr, value, delim)
    else: obj[attr] = value


def to_int(value, default=None):
    try:
        return int(value)
    except:
        return default


def value_type(value):
    return re.findall(r"(\w+?)\'", str(type(value)))[0].lower()


def window_bgcolor():
    tmp = QtWidgets.QWidget()
    return tmp.palette().color(QtGui.QPalette.Window)


def xml_to_dict(xml, listpaths=None, **kwargs):
    listpaths = listpaths or []
    opts = dict(
        attr_prefix = '',
        dict_constructor = dict,
        postprocessor = lambda p,k,d: (k.split(':')[1] if ':' in k else k,d)
    )
    opts.update(kwargs)
    content = xmltodict.parse(xml, **opts)
    for listpath in listpaths:
        pathdata = rget(content, listpath, [])
        pathdata = pathdata if isinstance(pathdata, list) else [pathdata]
        rset(content, listpath, pathdata)
    return content
