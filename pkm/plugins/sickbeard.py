# -*- coding: utf-8 -*-
"""
Sickbeard
Coming Soon
"""
import json, os, webbrowser
from datetime import datetime
from pkm import log, utils, SHAREDIR
from pkm.decorators import never_raise, threaded_method
from pkm.exceptions import ValidationError
from pkm.plugin import BasePlugin, BaseConfig

NAME = 'Sickbeard'
UPDATE_URL = '%(host)s/api/%(apikey)s/?cmd=future&limit=10'
PING_URL = '%(host)s/api/%(apikey)s/?cmd=sb.ping'
WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']
DATE_FORMAT = '%Y-%m-%d'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 60

    @threaded_method
    def enable(self):
        self.host = self.pkmeter.config.get(self.namespace, 'host', '').lstrip('/')
        apikey = self.pkmeter.config.get(self.namespace, 'apikey')
        if not self.host:
            log.warning('Sickbeard host not specified.')
            return self.disable()
        if not apikey:
            log.warning('Sickbeard apikey not specified.')
            return self.disable()
        self.update_url = UPDATE_URL % {'host':self.host, 'apikey':apikey}
        self.ignores = self.pkmeter.config.get('plexmedia', 'ignores', '')
        self.ignores = list(filter(None, self.ignores.split('\n')))
        super(Plugin, self).enable()

    @never_raise
    def update(self):
        response = utils.http_request(self.update_url).get('response')
        shows = []
        if response:
            content = json.loads(response.read().decode('utf-8'))
            for stype in ('missed','today','soon','later'):
                for show in utils.rget(content, 'data.%s' % stype, []):
                    show['datestr'] = self._datestr(stype, show)
                    show['episode'] = "s%se%s" % (show.get('season',''), show.get('episode',''))
                    if not self._is_ignored(show):
                        shows.append(show)
        self.data['shows'] = shows
        super(Plugin, self).update()

    def _datestr(self, stype, show):
        if stype == 'missed': return 'Missed'
        if stype == 'later': return datetime.strptime(show['airdate'], DATE_FORMAT).strftime("%b %d")
        airday = show['airs'].split(' ', 1)[0][:3]
        airtime = show['airs'].split(' ', 1)[1].replace(':00','')
        airtime = airtime.replace(' AM','a').replace(' PM','p')
        return 'Today %s' % airtime if stype == 'today' else '%s %s' % (airday, airtime)

    def _is_ignored(self, show):
        if self.ignores:
            for ignore in self.ignores:
                if ignore.lower() in show['show_name'].lower():
                    return True
        return False

    @never_raise
    def open_sickbeard(self, widget):
        log.info('Opening Sickbeard: %s', self.host)
        webbrowser.open(self.host)


class Config(BaseConfig):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'sickbeard_config.html')
    FIELDS = utils.Bunch(BaseConfig.FIELDS, host={}, apikey={})

    def validate_host(self, field, value):
        if not value:
            return value
        url = PING_URL % {'host':value, 'apikey':1234}
        response = utils.http_request(url, timeout=2).get('response')
        if not response:
            raise ValidationError('Host not reachable.')
        if response.status != 200:
            raise ValidationError('Invalid response from server: %s' % response.status)
        return value

    def validate_apikey(self, field, value):
        if not value:
            return value
        host = self.fields.host.value
        if host is None:
            host = self.pkconfig.get(self.namespace, 'host')
        url = PING_URL % {'host':host, 'apikey':value}
        response = utils.http_request(url, timeout=2).get('response')
        if not response:
            raise ValidationError('Host not reachable.')
        if response.status != 200:
            raise ValidationError('Invalid response from server: %s' % response.status)
        content = json.loads(response.read().decode('utf-8'))
        if content.get('result') != 'success':
            raise ValidationError('Invalid API key specified.')
        return value
