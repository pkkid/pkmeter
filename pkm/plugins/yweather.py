# -*- coding: utf-8 -*-
"""
Yahoo Weather
Fetch current weather from Yahoo!
"""
import re
from pkm import utils
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin, BaseConfig
from pkm.filters import register_filter

NAME = 'Yahoo! Weather'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 600
    UPDATE_URL = "http://xml.weather.yahoo.com/forecastrss/%(location)s_%(tempunit)s.xml"

    @threaded_method
    def enable(self):
        tempunit = self.pkmeter.config.get('pkmeter', 'tempunit', 'f')
        location = self.pkmeter.config.get(self.namespace, 'location', 'USMA0443')
        self.update_url = self.UPDATE_URL % {'location':location, 'tempunit':tempunit}
        super(Plugin, self).enable()

    @never_raise
    def update(self):
        response = utils.http_request(self.update_url).get('response')
        if response:
            contents = utils.xml_to_dict(response.read().decode('utf-8'))
            self.data = utils.rget(contents, 'rss.channel', {})
        super(Plugin, self).update()


class Config(BaseConfig):
    pass


@register_filter()
def yweather_updated(value):
    if value is None: return ''
    matches = re.findall('(\w+),.*?(\d+:\d+)\s*([apm]{2})', value)
    return '%s %s%s' % matches[0] if matches else value
