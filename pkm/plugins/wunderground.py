# -*- coding: utf-8 -*-
"""
Weather Underground
Fetch current weather from api.wunderground.com
"""
import json, os, webbrowser
from pkm import SHAREDIR, log, utils
from pkm.decorators import never_raise, threaded_method
from pkm.exceptions import ValidationError
from pkm.plugin import BasePlugin, BaseConfig
from pkm.filters import register_filter

NAME = 'Weather Underground'
UPDATE_URL = 'http://api.wunderground.com/api/%(apikey)s/conditions/forecast10day/astronomy/q/%(location)s.json'
QUERY_URL = 'http://autocomplete.wunderground.com/aq?query=%(query)s'
#WEBSITE_URL = 'http://www.wunderground.com/cgi-bin/findweather/getForecast?query=%(location)s'
ICON_NA = 'na'
ICON_CODES = {
    'chanceflurries': {'day':41, 'night':46},
    'chancerain': {'day':39, 'night':45},
    'chancesleet': {'day':18, 'night':18},
    'chancesnow': {'day':41, 'night':46},
    'chancetstorms': {'day':37, 'night':47},
    'clear': {'day':32, 'night':31},
    'cloudy': {'day':26, 'night':26},
    'flurries': {'day':13, 'night':13},
    'fog': {'day':20, 'night':20},
    'hazy': {'day':22, 'night':21},
    'mostlycloudy': {'day':28, 'night':27},
    'mostlysunny': {'day':34, 'night':33},
    'partlycloudy': {'day':30, 'night':29},
    'partlysunny': {'day':30, 'night':29},
    'sleet': {'day':18, 'night':18},
    'rain': {'day':12, 'night':12},
    'snow': {'day':16, 'night':16},
    'sunny': {'day':32, 'night':31},
    'tstorms': {'day':4, 'night':4},
}


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 600

    @threaded_method
    def enable(self):
        apikey = self.pkmeter.config.get(self.namespace, 'apikey')
        self.location = self.pkmeter.config.get(self.namespace, 'location', 'autoip')
        if not apikey:
            log.warning('Wunderground apikey not specified.')
            return self.disable()
        self.update_url = UPDATE_URL % {'apikey':apikey, 'location':self.location}
        super(Plugin, self).enable()

    @never_raise
    def update(self):
        response = utils.http_request(self.update_url).get('response')
        if response:
            self.data = json.loads(response.read().decode('utf-8'))
        super(Plugin, self).update()

    @never_raise
    def open_wunderground(self, widget):
        url = utils.rget(self.data, 'current_observation.ob_url', 'http://www.wunderground.com')
        #url = WEBSITE_URL % {'location':self.location}
        log.info('Opening WUnderground page: %s', url)
        webbrowser.open(url)


class Config(BaseConfig):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'wunderground_config.html')
    FIELDS = utils.Bunch(BaseConfig.FIELDS, apikey={}, query={},
        location = {'default':'autoip'},
    )

    def validate_apikey(self, field, value):
        if not value:
            return value
        url = UPDATE_URL % {'apikey':value, 'location':'autoip'}
        response = utils.http_request(url, timeout=2).get('response')
        if not response:
            raise ValidationError('No response from Weather Underground.')
        content = json.loads(response.read().decode('utf-8'))
        if 'response' not in content:
            raise ValidationError('Invalid response from Weather Underground.')
        if 'current_observation' not in content:
            raise ValidationError('Invalid API key specified.')
        return value

    def validate_query(self, field, value):
        if not value or value == 'autoip':
            self.fields.location.value = 'autoip'
            field.help.setText(field.help_default)
            return value
        url = QUERY_URL % {'query':value}
        response = utils.http_request(url, timeout=2).get('response')
        if not response:
            raise ValidationError('No response from Weather Underground.')
        content = json.loads(response.read().decode('utf-8'))
        if not content.get('RESULTS'):
            raise ValidationError('Unable to determine specified location.')
        result = content['RESULTS'][0]
        self.fields.location.value = result['ll'].replace(' ',',')
        field.help.setText(result['name'])
        return value


@register_filter()
def wunderground_iconcode(icon):
    if icon not in ICON_CODES:
        return ICON_NA
    daynight = 'night' if icon.startswith('nt_') else 'day'
    return '%02d' % ICON_CODES[icon][daynight]


@register_filter()
def mod_12(value):
    return utils.to_int(value, 0) % 12
