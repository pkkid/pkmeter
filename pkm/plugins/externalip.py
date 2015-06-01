# -*- coding: utf-8 -*-
"""
Plex Server
Who is watching what?
"""
import os, re
from pkm import utils, SHAREDIR
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin, BaseConfig

NAME = 'External IP'
REGEX_IP = '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
DEFUALT_URL = 'http://checkip.dyndns.org'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 900

    @threaded_method
    def enable(self):
        self.update_url = self.pkmeter.config.get(self.namespace, 'url', DEFUALT_URL)
        super(Plugin, self).enable()

    @never_raise
    def update(self):
        response = utils.http_request(self.update_url).get('response')
        if response:
            content = response.read().decode('utf-8')
            matches = re.findall(REGEX_IP, content)
            self.data['ip'] = matches[0] if matches else ''
        super(Plugin, self).update()


class Config(BaseConfig):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'externalip_config.html')
    FIELDS = utils.Bunch(BaseConfig.FIELDS,
        url = {'default': DEFUALT_URL}
    )
