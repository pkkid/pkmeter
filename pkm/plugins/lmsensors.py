# -*- coding: utf-8 -*-
"""
Sensors Plugin

"""
import sensors
from pkm import log
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin, BaseConfig

NAME = 'LmSensors'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 5

    @threaded_method
    def enable(self):
        try:
            sensors.init()
            super(Plugin, self).enable()
        except Exception:
            log.warning('Plex server not available.')
            return self.disable()

    @never_raise
    def update(self):
        self.data = {}
        for chip in sensors.iter_detected_chips():
            chip_name = str(chip).lower()
            adapter_name = chip.adapter_name.lower()
            for atype in ('acpi', 'isa'):
                if atype in chip_name + adapter_name:
                    adapter = {}
                    if atype not in self.data:
                        self.data[atype] = []
                    for feature in chip:
                        label = self._clean_name(feature.label)
                        value = feature.get_value()
                        if value: adapter[label] = value
                        if label == 'temp1': adapter['mb_temperature'] = value
                        if label == 'temp2': adapter['cpu_temperature'] = value
                    self.data[atype].append(adapter)
        super(Plugin, self).update()

    def _clean_name(self, name):
        return str(name).lower().replace('+', '').replace('.', '_').strip().replace(' ', '_')


class Config(BaseConfig):
    pass
