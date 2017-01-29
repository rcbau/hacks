#!/usr/bin/python

# Lookup the weather for a given latitude and longitude from wunderground.com

import calendar
import json
import os
import pygame
import pygame.display
import pygame.font
import pygame.image
import pygame.surface
import requests
import six
import sys

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

with open(os.path.expanduser('~/.weather'), 'r') as f:
    conf = json.loads(f.read())


def extract_field(j, field_path):
    if len(field_path) == 1:
        return j[field_path[0]]

    return extract_field(j[field_path[0]], field_path[1:])


def fetch_icon(url):
    filename = url.split('/')[-1]
    img_filename = os.path.join('iconcache', filename)
    if not os.path.exists(img_filename):
        print 'Fetching %s' % url
        response = requests.get(url, verify = True)
        with open(img_filename, 'wb') as f:
            f.write(response.content)
    return img_filename


X_MARGIN = 5
Y_MARGIN = 5


if __name__ == '__main__':
    conf['output_filename'] = 'output.png'
    if len(sys.argv) > 1:
        conf['location'] = sys.argv[1]
        conf['output_filename'] = 'output-%s.png' % sys.argv[1]

    pygame.init()

    outimg = pygame.Surface((320, 196), pygame.SRCALPHA)
    outimg.fill((255, 255, 255))

    small_font = pygame.font.Font('fonts/Montserrat-Regular.ttf', 15)
    big_font = pygame.font.Font('fonts/Montserrat-Bold.ttf', 45)

    registry = CollectorRegistry()
    Gauge('job_last_success_unixtime', 'Last time the weather job ran',
          registry=registry).set_to_current_time()

    # Find weather stations near that location
    url = ('http://api.wunderground.com/api/%(apikey)s/geolookup/q/'
           '%(location)s.json' % conf)
    print 'Fetching %s' % url
    response = requests.get(url, verify = True)

    geolookup = json.loads(response.text)
    conf['locurl'] = geolookup['location']['l']

    # Grab the readings from the closest
    url = ('http://api.wunderground.com/api/%(apikey)s/conditions'
           '%(locurl)s.json' % conf)
    print 'Fetching %s' % url
    response = requests.get(url, verify = True)

    weather = json.loads(response.text)
    weather = weather['current_observation']

    # Print out the fields we care about
    fields = [['feelslike_c'],
              ['precip_1hr_metric'],
              ['precip_today_metric'],
              ['relative_humidity'],
              ['temp_c'],
              ['wind_gust_kph'],
              ['wind_kph'],
              ['icon_url']]
    now = {}
    for field in fields:
        value = extract_field(weather, field)

        now['/'.join(field)] = value

        # Mungle some values to work in prometheus
        if isinstance(value, six.text_type) and value.endswith('%'):
            value = float(value[:-1]) / 100.0

        if isinstance(value, six.text_type):
            try:
                value = float(value)
            except:
                pass

        if isinstance(value, float) or isinstance(value, int):
            Gauge('_'.join(field), '', registry=registry).set(value)

    now['icon'] = fetch_icon(now['icon_url'])

    # Get a 10 day forecast as well
    url = ('http://api.wunderground.com/api/%(apikey)s/forecast10day'
           '%(locurl)s.json' % conf)
    print 'Fetching %s' % url
    response = requests.get(url, verify = True)

    forecast = json.loads(response.text)
    forecast = forecast['forecast']['simpleforecast']['forecastday']

    fields = [['date', 'day'], ['date', 'month'], ['high', 'celsius'],
              ['icon_url'], ['low', 'celsius'], ['pop']]
    dayforecast = {}
    for day in forecast:
        dayforecast[day['period']] = {}
        for field in fields:
            dayforecast[day['period']]['/'.join(field)] = \
                extract_field(day, field)
        dayforecast[day['period']]['icon'] = \
            fetch_icon(dayforecast[day['period']]['icon_url'])

    print 'Now: %s %skph %s humidity' %(now['temp_c'], now['wind_kph'],
                                        now['relative_humidity'])
    img = pygame.image.load(now['icon'])
    outimg.blit(img, (X_MARGIN, Y_MARGIN))

    label = big_font.render('%s' % now['temp_c'], 1, (0, 0, 0))
    outimg.blit(label, (55 + X_MARGIN, Y_MARGIN - 5))

    label = small_font.render('%s humidity' % now['relative_humidity'],
                              1, (0, 0, 0))
    outimg.blit(label, (160 + X_MARGIN, Y_MARGIN + 3))

    label = small_font.render('%s kph wind' % now['wind_kph'], 1, (0, 0, 0))
    outimg.blit(label, (160 + X_MARGIN, Y_MARGIN + 23))

    for day in range(1, 4):
        print '%s %s: %s to %s with %s%% rain' %(
            dayforecast[day]['date/day'],
            calendar.month_name[dayforecast[day]['date/month']][0:3],
            dayforecast[day]['low/celsius'],
            dayforecast[day]['high/celsius'],
            dayforecast[day]['pop'])

        img = pygame.image.load(dayforecast[day]['icon'])
        outimg.blit(img, (((day - 1) * 90) + X_MARGIN, 50 + Y_MARGIN))

        label = small_font.render(
            '%s %s' %(dayforecast[day]['date/day'],
                      calendar.month_name[dayforecast[day]['date/month']][0:3]),
            1, (0, 0, 0))
        outimg.blit(label, (((day - 1) * 90) + X_MARGIN, 100 + Y_MARGIN))

        label = small_font.render(
            '%s-%s %s%%' %(dayforecast[day]['low/celsius'],
                           dayforecast[day]['high/celsius'],
                           dayforecast[day]['pop']),
            1, (0, 0, 0))
        outimg.blit(label, (((day - 1) * 90) + X_MARGIN, 100 + Y_MARGIN + 20))

    label = small_font.render('Data from wunderground.com', 1, (0, 0, 0))
    outimg.blit(label, (X_MARGIN, Y_MARGIN + 160))

    pygame.image.save(outimg, conf['output_filename'])

    push_to_gateway('localhost:9091', job='weather', registry=registry)
