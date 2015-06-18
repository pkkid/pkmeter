# -*- coding: utf-8 -*-
"""
Sonarr
Coming Soon
"""
import json, os, webbrowser
from datetime import datetime, timedelta
from pkm import log, utils, SHAREDIR
from pkm.decorators import never_raise, threaded_method
from pkm.exceptions import ValidationError
from pkm.filters import register_filter
from pkm.plugin import BasePlugin, BaseConfig

NAME = 'Sonarr'
UPDATE_URL = '%(host)s/api/calendar?apikey=%(apikey)s&end=%(end)s'
DATE_FORMAT = '%Y-%m-%d'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 60

    @threaded_method
    def enable(self):
        self.host = self.pkmeter.config.get(self.namespace, 'host', '').lstrip('/')
        self.apikey = self.pkmeter.config.get(self.namespace, 'apikey')
        if not self.host:
            log.warning('Sonarr host not specified.')
            return self.disable()
        if not self.apikey:
            log.warning('Sonarr apikey not specified.')
            return self.disable()
        self.ignores = self.pkmeter.config.get(self.namespace, 'ignores', '')
        self.ignores = list(filter(None, self.ignores.split('\n')))
        super(Plugin, self).enable()

    @never_raise
    def update(self):
        endstr = (datetime.now() + timedelta(days=14)).strftime(DATE_FORMAT)
        update_url = UPDATE_URL % {'host':self.host, 'apikey':self.apikey, 'end':endstr}
        response = utils.http_request(update_url).get('response')
        if response:
            content = json.loads(response.read().decode('utf-8'))
            self.data['shows'] = content
        super(Plugin, self).update()

    @never_raise
    def open_sonarr(self, widget):
        log.info('Opening Sonarr: %s', self.host)
        webbrowser.open(self.host)


class Config(BaseConfig):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'sonarr_config.html')
    FIELDS = utils.Bunch(BaseConfig.FIELDS, host={}, apikey={}, ignores={})

    def validate_host(self, field, value):
        if not value:
            return value
        url = UPDATE_URL % {'host':value, 'apikey':1234, 'end':'2000-01-01'}
        response = utils.http_request(url, timeout=2)
        if utils.rget(response, 'error.code') != 401:
            raise ValidationError('Host not reachable.')
        return value

    def validate_apikey(self, field, value):
        if not value:
            return value
        host = self.fields.host.value
        if host is None:
            host = self.pkconfig.get(self.namespace, 'host')
        url = UPDATE_URL % {'host':host, 'apikey':value, 'end':'2000-01-01'}
        response = utils.http_request(url, timeout=2).get('response')
        if utils.rget(response, 'error.code') == 401:
            raise ValidationError('Invalid API key specified.')
        content = json.loads(response.read().decode('utf-8'))
        if not isinstance(content, list):
            raise ValidationError('Invalid response from server.')
        return value


@register_filter()
def sonarr_airtime(show):
    try:
        airdatestr = '%s %s' % (show['airDate'], show['series']['airTime'])
        airdate = datetime.strptime(airdatestr, '%Y-%m-%d %H:%M')
        print((airdate - datetime.now()).days)
        if (airdate - datetime.now()).days < 7:
            today = datetime.now().strftime('%a')
            datestr = airdate.strftime('%a %-I:%M%p').replace(':00', '')
            datestr = datestr.replace('AM','a').replace('PM','p')
            return datestr.replace(today, 'Today')
        return airdate.strftime('%b %-d')
    except:
        return None
