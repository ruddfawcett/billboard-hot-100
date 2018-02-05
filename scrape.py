#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib.request as urllib2
import pandas as pd

from datetime import datetime, timedelta
from bs4 import BeautifulSoup

'''
String is in format Y-m-d (2018-02-03). Should be a Saturday.
'''
def str_to_date(s):
    return datetime.strptime(s, '%Y-%m-%d').date()

def date_to_str(date):
    return date.strftime('%Y-%m-%d')

def sanitize(s):
    if '-' in s:
        return -1
    return int(s)

def billboard_top_100(week):
    page = urllib2.urlopen(URL.format(date_to_str(week)))
    soup = BeautifulSoup(page, 'lxml')
    chart = []

    for row in soup.findAll('article', {'class': 'chart-row'}):
        metadata = row.find('div', {'class': 'chart-row__title'})

        title = metadata.find('h2', {'class': 'chart-row__song'}).text
        artist = metadata.find('a', {'class': 'chart-row__artist'})
        artist_text = ''

        if artist is None:
            artist = metadata.find('span', {'class': 'chart-row__artist'})
            artist_text = artist.text
        else:
            artist_text = artist.text

        pos = sanitize(row.find('div', {'class': 'chart-row__rank'}).find('span', {'class': 'chart-row__current-week'}).text)
        last_pos = sanitize(row.find('div', {'class': 'chart-row__last-week'}).find('span', {'class': 'chart-row__value'}).text)
        peak_pos = sanitize(row.find('div', {'class': 'chart-row__top-spot'}).find('span', {'class': 'chart-row__value'}).text)
        streak = sanitize(row.find('div', {'class': 'chart-row__weeks-on-chart'}).find('span', {'class': 'chart-row__value'}).text)

        song = {
            'title': title.replace('\n', ''),
            'artist': artist_text.replace('\n', ''),
            'pos': pos,
            'last_pos': last_pos,
            'peak_pos': peak_pos,
            'streak': streak,
        }

        chart.append(song)

    return chart

URL = "https://www.billboard.com/charts/hot-100/{0}"

def scrape(start_date):
    try:
        while True:
            chart = billboard_top_100(start_date)
            chart_db = pd.DataFrame(chart, columns=chart[0].keys())
            chart_db.set_index('pos', inplace=True)
            chart_db.to_csv('charts/{0}.csv'.format(date_to_str(start_date)))

            print('Downloaded Billboard Hot 100 for week of {0}.'.format(start_date))

            start_date = start_date - timedelta(days=7)
    except Exception as e:
        print(e)
        print('RESTART FROM THIS DATE: {0}...'.format(start_date))

scrape(str_to_date('2018-02-03'))
