# -*- coding: utf-8 -*-
"""
Plugin Abstract Class
"""
import os, threading, time
from pkm import SHAREDIR
from pkm import log, utils
from pkm.decorators import never_raise, threaded_method
from pkm.exceptions import ValidationError
from pkm.pkwidgets import PKVFrame
from PyQt5 import QtCore
from xml.etree import ElementTree


class BasePlugin(threading.Thread):
    DEFAULT_INTERVAL = 60

    def __init__(self, pkmeter, *args, **kwargs):
        super(BasePlugin, self).__init__(*args, **kwargs)
        self.daemon = True                                          # Set as daemon thread
        self.name = utils.name(self.__module__)                     # Name of this Plugin
        self.namespace = utils.namespace(self.__module__)           # Namespace of this Plugin
        self.pkmeter = pkmeter                                      # Reference to PKMeter
        self.enabled = False                                        # False if plugin disabled
        self.interval = self.get_interval()                         # Get the current interval
        self.next_update = time.time()                              # Update immediatly
        self.data = {'interval':self.interval}                      # Data returned to PKMeter

    def enable(self):
        self.interval = self.get_interval()
        self.next_update = time.time()
        self.enabled = self.pkmeter.config.get(self.namespace, 'enabled', True)
        if not self.enabled:
            log.info('%s plugin disabled in preferences.' % self.name)
            return self.disable()
        if self.namespace not in self.pkmeter.actions:
            log.info('%s data not used in layout.' % self.name)
            return self.disable()
        if self.enabled:
            log.info('Enabling plugin %s with interval: %ss', self.name, self.interval)
            BasePlugin.update(self)
        return self.enabled

    def disable(self):
        self.enabled = False
        self.data = {'enabled': False}
        self.pkmeter.plugin_updated.emit(self)
        return False

    def get_interval(self):
        return float(self.pkmeter.config.get(self.namespace, 'interval', self.DEFAULT_INTERVAL))

    def run(self):
        self.enable()
        while True:
            if self.enabled and self.next_update <= time.time():
                self.next_update += self.interval
                self.update()
            time.sleep(0.1)

    @never_raise
    def update(self):
        self.data['enabled'] = self.enabled
        self.data['enabled'] = self.enabled
        self.pkmeter.plugin_updated.emit(self)


class BaseConfig(PKVFrame):
    STATUS_OK = '✔'
    STATUS_ERROR = '✘'
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'default_config.html')
    FIELDS = utils.Bunch(
        enabled = {'default':True},
        interval = {'default':60}
    )

    def __init__(self, pkmeter, pkconfig):
        self.name = utils.name(self.__module__)                     # Name of this Plugin
        self.namespace = utils.namespace(self.__module__)           # Namespace of this Config
        self.template = self._init_template()                       # Template for config settings
        self.fields = utils.Bunch()                                 # Fields in this Config
        PKVFrame.__init__(self, self.template, self)                # Init parent widget
        self.pkmeter = pkmeter                                      # Reference to PKMeter
        self.pkconfig = pkconfig                                    # Reference to Main Config
        self._init_default_interval()
        self._init_fields()

    def _init_template(self):
        with open(self.TEMPLATE) as tmpl:
            template = ElementTree.fromstring(tmpl.read())
        return template

    def _init_default_interval(self):
        if 'interval' in self.FIELDS:
            module = self.pkmeter.modules[self.namespace]
            default_interval = module.Plugin.DEFAULT_INTERVAL
            self.FIELDS.interval['default'] = default_interval

    def _init_fields(self):
        for name, meta in self.FIELDS.items():
            self._init_field(name, meta)

    def _init_field(self, name, meta):
        field = utils.Bunch(meta)                                                   # Convert to Bunch
        field.name = name                                                           # Name of this field
        field.input = self.manifest.get(name)                                       # QT input element
        field.controlgroup = self.manifest.get('controlgroup_%s' % name)            # QT control group
        field.status = self.manifest.get('status_%s' % name)                        # QT status label
        field.help = self.manifest.get('help_%s' % name)                            # QT help label
        field.help_default = field.help.text() if field.help else None              # Default help text
        field.default = field.get('default', '')                                    # Default value
        field.value = self._get_value(field)                                        # Current value (to be saved)
        field.lastchecked = field.value                                             # Last value verified
        field.validator = getattr(self, 'validate_%s' % name, None)                 # Validator callback
        if name in self.manifest:
            if getattr(field.input, 'textEdited', None):
                field.input.textEdited.connect(lambda txt,field=field: self._editing(field, txt))
            if getattr(field.input, 'editingFinished', None):
                field.input.editingFinished.connect(lambda field=field: self._validate(field))
            field.input.set_value(field.value)
        self.fields[name] = field

    def _get_value(self, field):
        from_keyring = field.get('save_to_keyring', False)
        return self.pkconfig.get(self.namespace, field.name, field.default, from_keyring)

    def _editing(self, field, text):
        self._set_field_status(field, '', '')

    @threaded_method
    def _validate(self, field, force=False):
        if not field.input:
            return
        try:
            value = field.input.get_value()
            if field.validator:
                result = field.validator(field, value)
                value = value if result is None else result
                log.info('Validation passed for %s.%s', self.namespace, field.name)
            status = '' if force else self.STATUS_OK
            self._set_field_status(field, status, '')
        except Exception as err:
            log.warn('Validation Error for %s.%s: %s', self.namespace, field.name, err)
            self._set_field_status(field, self.STATUS_ERROR, str(err))
        finally:
            log.info('Setting value %s.%s: %s', self.namespace, field.name, value)
            field.value = value

    def _set_field_status(self, field, status, errmsg):
        if field.controlgroup: field.controlgroup.setToolTip(errmsg)
        if field.status: field.status.setText(status)

    def validate_interval(self, field, value):
        try:
            interval = int(value)
            assert 1 <= interval <= 3600, 'Value out of bounds.'
            return interval
        except:
            raise ValidationError('Interval seconds must be a number 1-3600.')


class EventFilter(QtCore.QObject):

    def __init__(self, callback, *args):
        super(EventFilter, self).__init__()
        self.callback = callback
        self.args = args

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.FocusOut:
            self.callback(*self.args)
        return False
