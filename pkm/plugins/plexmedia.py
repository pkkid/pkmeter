# -*- coding: utf-8 -*-
"""
Plex Server
Who is watching what?
"""
import os
from plexapi.exceptions import NotFound
from plexapi.video import Season
from pkm import log, utils, SHAREDIR
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin, BaseConfig
from pkm.plugins.plexserver import fetch_plex_instance

NAME = 'Plex Media'
UPDATE_URL = '%(plexhost)s/library/recentlyAdded'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 60

    @threaded_method
    def enable(self):
        try:
            self.plex = fetch_plex_instance(self.pkmeter)
            self.ignores = self.pkmeter.config.get(self.namespace, 'ignores', '')
            self.ignores = list(filter(None, self.ignores.split('\n')))
            super(Plugin, self).enable()
        except NotFound:
            log.warning('Plex server not available.')
            return self.disable()

    @never_raise
    def update(self):
        self.data['videos'] = []
        videos = self.plex.library.recentlyAdded()
        videos = sorted(videos, key=lambda v:v.addedAt, reverse=True)
        for video in videos[:10]:
            title = self._video_title(video)
            if self._is_ignored(title):
                continue
            self.data['videos'].append({
                'title': title,
                'type': video.type,
                'added': video.addedAt,
            })
        self.data['videos'] = sorted(self.data['videos'], key=lambda x:x['added'], reverse=True)
        super(Plugin, self).update()

    def _video_title(self, video):
        if video.type == Season.TYPE:
            episode = video.episodes()[-1]
            return '%s s%se%s' % (episode.grandparentTitle, episode.parentIndex, video.leafCount)
        return '%s (%s)' % (video.title, video.year)

    def _is_ignored(self, title):
        if self.ignores:
            for ignore in self.ignores:
                if ignore.lower() in title.lower():
                    return True
        return False


class Config(BaseConfig):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'plexmedia_config.html')
    FIELDS = utils.Bunch(BaseConfig.FIELDS, ignores={})
