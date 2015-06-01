# -*- coding: utf-8 -*-
"""
Picasa Web Albums
Picasa photoalbum display
"""
import json, os, random, time, webbrowser
from pkm import log, utils, SHAREDIR
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin, BaseConfig

NAME = 'Picasa'
ALBUMS_URL = 'http://picasaweb.google.com/data/feed/api/user/%(username)s?alt=json'
PHOTOS_URL = 'http://picasaweb.google.com/data/feed/api/user/%(username)s/albumid/%(albumid)s?alt=json'
ALBUMS_UPDATE_INTERVAL = 1800


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 30

    @threaded_method
    def enable(self):
        self.username = self.pkmeter.config.get(self.namespace, 'username', '')
        if not self.username:
            log.warning('Username not specified.')
            return self.disable()
        self.albums_url = ALBUMS_URL % {'username':self.username}
        self.ignores = self.pkmeter.config.get(self.namespace, 'ignores', '')
        self.ignores = list(filter(None, self.ignores.split('\n')))
        self.last_albums_update = 0
        super(Plugin, self).enable()

    @never_raise
    def update(self):
        if self.last_albums_update <= time.time() - ALBUMS_UPDATE_INTERVAL:
            self.update_albums()
        self.data['album'] = self.choose_random_album()
        self.data['photo'] = self.choose_random_photo(self.data['album'])
        super(Plugin, self).update()

    def update_albums(self):
        albums = []
        response = utils.http_request(self.albums_url).get('response')
        if response:
            content = json.loads(response.read().decode('utf-8'))
            self.data['user'] = {}
            self.data['user']['id'] = utils.rget(content, 'feed.gphoto$user.$t')
            self.data['user']['name'] = utils.rget(content, 'feed.gphoto$nickname.$t')
            for entry in utils.rget(content, 'feed.entry', []):
                title = utils.rget(entry, 'title.$t')
                numphotos = utils.rget(entry, 'gphoto$numphotos.$t')
                if title and numphotos and not self._is_ignored(title):
                    album = {}
                    album['id'] = entry['gphoto$id']['$t']
                    album['title'] = title.split(' - ')[-1]
                    album['date'] = title.split(' - ')[0]
                    album['photos'] = numphotos
                    albums.append(album)
        self.last_albums_update = int(time.time())
        self.data['albums'] = albums

    def choose_random_album(self):
        counter = 0
        numphotos = sum([album['photos'] for album in self.data['albums']])
        diceroll = random.randrange(numphotos)
        for album in self.data['albums']:
            counter += album['photos']
            if counter >= diceroll: break
        return album

    def choose_random_photo(self, album):
        photo = {}
        photos_url = PHOTOS_URL % {'username':self.username, 'albumid':album['id']}
        response = utils.http_request(photos_url).get('response')
        if response:
            content = json.loads(response.read().decode('utf-8'))
            numphotos = utils.rget(content, 'feed.gphoto$numphotos.$t')
            if numphotos:
                diceroll = random.randrange(numphotos)
                entry = utils.rget(content, 'feed.entry')[diceroll]
                photo['id'] = entry['gphoto$id']['$t']
                photo['url'] = entry['content']['src']
                photo['title'] = utils.rget(entry, 'title.$t')
                photo['summary'] = utils.rget(entry, 'summary.$t')
                photo['timestamp'] = utils.rget(entry, 'gphoto$timestamp.$t')
                photo['published'] = utils.rget(entry, 'published.$t')
                photo['width'] = utils.rget(entry, 'gphoto$width.$t')
                photo['height'] = utils.rget(entry, 'gphoto$height.$t')
                photo['size'] = int(utils.rget(entry, 'gphoto$size.$t', 0))
                photo['credit'] = ', '.join([item['$t'] for item in utils.rget(entry, 'media$group.media$credit')])
                for tag, value in utils.rget(entry, 'exif$tags').items():
                    tagstr = tag.replace('exif$', '')
                    photo[tagstr] = value['$t']
        return photo

    def _is_ignored(self, title):
        if self.ignores:
            for ignore in self.ignores:
                if ignore.lower() in title.lower():
                    return True
        return False

    @never_raise
    def open_current_image(self, widget):
        url = 'https://plus.google.com/photos/%(userid)s/albums/%(albumid)s/%(photoid)s' % {
            'userid': self.data['user']['id'],
            'albumid': self.data['album']['id'],
            'photoid': self.data['photo']['id'],
        }
        log.info('Opening Picasa Image: %s', url)
        webbrowser.open(url)

    @never_raise
    def open_albums(self, widget):
        url = 'https://plus.google.com/photos/%s/albums' % self.data['user']['id']
        log.info('Opening Picasa Albums: %s', url)
        webbrowser.open(url)


class Config(BaseConfig):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'picasa_config.html')
    FIELDS = utils.Bunch(BaseConfig.FIELDS, username={}, ignores={})
