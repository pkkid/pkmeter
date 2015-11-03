# -*- coding: utf-8 -*-
"""
GCal Plugin
Google Calendar Events
"""
import datetime, json, os, webbrowser
from dateutil import tz
from icalendar import Calendar
from PyQt5 import QtWidgets
from pkm import log, utils, SHAREDIR
from pkm.decorators import never_raise
from pkm.exceptions import ValidationError
from pkm.plugin import BasePlugin, BaseConfig
from pkm.filters import register_filter

NAME = 'Google Calendar'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 600
    DELTANONE = datetime.datetime.now()

    @never_raise
    def update(self):
        self.data['events'] = []
        self.tzutc = tz.tzutc()
        self.tzlocal = tz.tzlocal()
        urls, colors = [], {}
        for cal in self._iter_calendars():
            urls.append(cal.url)
            colors[cal.url] = cal.color
        for result in utils.iter_responses(urls, timeout=5):
            response = result.get('response')
            if response:
                ical = Calendar.from_ical(response.read().decode('utf-8'))
                color = colors[result.get('url')]
                self.data['events'] += self._parse_events(ical, color)
        self.data['events'] = sorted(self.data['events'], key=lambda e:e['start'])
        # Calculate time to next event
        now = datetime.datetime.now()
        next = [e for e in self.data['events'] if e['start'] > now][0]['start'] if self.data['events'] else self.DELTANONE
        if next < now + datetime.timedelta(seconds=self.DEFAULT_INTERVAL*1.5): self.data['next'] = 'Now'
        else: self.data['next'] = utils.natural_time(next-now, 1)
        super(Plugin, self).update()

    def _iter_calendars(self):
        for i in range(6):
            baseurl = self.pkmeter.config.get(self.namespace, 'cal%s' % i)
            url = Plugin.build_url(baseurl)
            color = self.pkmeter.config.get(self.namespace, 'color%s' % i)
            if baseurl: yield utils.Bunch({'url':url, 'color':color})

    def _parse_events(self, ical, color):
        events = []
        today = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        title = ical.get('x-wr-calname', ical.get('version', ''))
        for event in ical.walk():
            if event.name == "VEVENT":
                start = self._fix_event_datetime(event.get('dtstart').dt)
                if today <= start <= today + datetime.timedelta(days=14):
                    events.append({
                        'title': event.get('summary'),
                        'calendar': title,
                        'color': color,
                        'start': start,
                        'where': event.get('location'),
                        'status': event.get('description'),
                    })
        return events

    def _fix_event_datetime(self, dt):
        if not isinstance(dt, datetime.datetime):
            return datetime.datetime.combine(dt, datetime.time.min)
        dt = dt.replace(tzinfo=self.tzutc)
        dt = dt.astimezone(self.tzlocal)
        return dt.replace(tzinfo=None)

    @never_raise
    def open_gcal(self, widget):
        url = 'http://google.com/calendar'
        log.info('Opening Google Calendar: %s', url)
        webbrowser.open(url)

    @staticmethod
    def build_url(baseurl):
        today = datetime.datetime.today()
        mindate = today.strftime('%Y-%m-%d')
        maxdate = (today + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        url = '%s?alt=json&singleevents=true&orderby=starttime' % baseurl
        url += '&start-min=%s&start-max=%s' % (mindate, maxdate)
        return url


class Config(BaseConfig):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'gcal_config.html')
    FIELDS = utils.Bunch(BaseConfig.FIELDS,
        cal1={'default': ''}, color1={'default': '#4986E7'},
        cal2={'default': ''}, color2={'default': '#CD74E6'},
        cal3={'default': ''}, color3={'default': '#F83A22'},
        cal4={'default': ''}, color4={'default': '#FFAD46'},
        cal5={'default': ''}, color5={'default': '#7BD148'},
    )

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        self._button = None
        self.colorpicker = self._init_colorpicker()

    def _init_colorpicker(self):
        colorpicker = QtWidgets.QColorDialog()
        colorpicker.finished.connect(self.colorpicker_finished)
        return colorpicker

    def btn_color(self, widget):
        self._button = widget
        self.colorpicker.setCurrentColor(utils.hex_to_qcolor(widget.data.color))
        self.colorpicker.open()

    def colorpicker_finished(self):
        field = self.fields[self._button.id]
        color = self.colorpicker.currentColor().name()
        self._button.set_value(color)
        self._validate(field)

    def _validate_cal(self, field, value):
        if not value:
            field.help.setText(field.help_default)
            return value
        url = Plugin.build_url(value)
        response = utils.http_request(url, timeout=2).get('response')
        if not response:
            raise ValidationError('No response from Google.')
        ical = Calendar.from_ical(response.read().decode('utf-8'))
        title = ical.get('x-wr-calname', ical.get('version', ''))
        if not title:
            raise ValidationError('Invalid response from Google.')
        field.help.setText(title)
        return value

    def validate_cal1(self, field, value):
        return self._validate_cal(field, value)

    def validate_cal2(self, field, value):
        return self._validate_cal(field, value)

    def validate_cal3(self, field, value):
        return self._validate_cal(field, value)

    def validate_cal4(self, field, value):
        return self._validate_cal(field, value)

    def validate_cal5(self, field, value):
        return self._validate_cal(field, value)


@register_filter()
def gcal_dtstr(value):
    # Select format based on for how far away event is
    today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    tomorrow = today + datetime.timedelta(days=1)
    nextweek = today + datetime.timedelta(days=7)
    if value >= nextweek: dtstr = value.strftime('%b %d')
    elif value >= tomorrow: dtstr = value.strftime('%a %I:%M%p')
    else: dtstr = value.strftime(' %I:%M%p')
    # Replace a few things to make it simpler
    dtstr = dtstr.replace(' 0',' ').replace(':00','')
    dtstr = dtstr.replace('AM','a').replace('PM','p')
    dtstr = dtstr.replace('12a', 'All day' if value < tomorrow else '')
    return dtstr.strip()
