#!/usr/bin/python

# Read irc logs from our private channel and post them to our wiki

import datetime
import json
import os
import pytz
import random
import sys
import wiki


with open(os.path.expanduser('~/.mediawiki'), 'r') as f:
    conf = json.loads(f.read())['ircbot']


def filter_files(lines):
    files = []
    for line in lines:
        if line.startswith('[[File:'):
            files.append(line)
    return files


def rotate_logos(w):
    main_page = w.get_page('Main Page').split('\n')
    archive = w.get_page('Former wiki logos').split('\n')
    archive.append(main_page[0].replace('|right]]', ']]'))

    sydney = pytz.timezone('Australia/Sydney')
    now = pytz.utc.localize(datetime.datetime.utcnow())
    sydney_now = now.astimezone(sydney)
    print 'UTC time:    %s' % now
    print 'Sydney time: %s' % sydney_now
    
    for extension in ['png', 'jpg', 'jpeg', 'gif']:
        today_title = ('File:%s.%s'
                       %(sydney_now.strftime('%Y%m%d'),
                         extension))
        print 'Testing for %s' % today_title
        today_meme = w.check_for_page(today_title)
        if today_meme:
            break

    if today_meme:
        print 'There is a programmed meme for today (%s)' % today_title
        new_logo = '[[%s]]' % today_title
        possible_page = None

    else:
        possible_page = 'Possible future wiki logos'
        possible = filter_files(w.get_page(possible_page).split('\n'))
        random.shuffle(possible)

        print 'We have %d memes' % len(possible)
        if len(possible) > 0:
            new_logo = possible[0]
        else:
            print 'No memes! Error time.'
            possible_page = 'Error logos'
            possible = filter_files(w.get_page(possible_page).split('\n'))
            random.shuffle(possible)
            new_logo = possible[0]

    new_logo = new_logo.replace(']]', '|right]]')
    if possible_page:
        w.post_page(possible_page, '\n'.join(possible[1:]))
    w.post_page('Former wiki logos', '\n'.join(archive))

    main_page = '%s\n%s' %(new_logo, '\n'.join(main_page[1:]))
    w.post_page('Main Page', main_page)


def squash_archive(w):
    archive = w.get_page('Former wiki logos').split('\n')
    files = []
    former = ''
    for line in archive:
        if line.startswith('[[File:'):
            files.append(line)
        elif line.startswith('Former wiki logos'):
            former = line

    if len(files) > 10:
        print 'Rotate archive (%d on main page)' % len(files)

        # I bet you this stops working
        upto = int(former.split('|')[-1][:-3].split('-')[1])
        print 'Up to %d' % upto

        while len(files) > 10:
            title = ('Former wiki logos %03d-%03d' % (upto + 1, upto + 10))
            w.post_page(title, '\n'.join(files[:10]))
            former += '; [[%s|%03d-%03d]]' % (title, upto + 1, upto + 10)
            print 'Posted %s' % title
            upto += 10
            files = files[10:]

        w.post_page('Former wiki logos',
                    '%s\n\n%s' % (former, '\n'.join(files)))


if __name__ == '__main__':
    w = wiki.Wiki(conf['url'], conf['username'], conf['password'])
    rotate_logos(w)
    squash_archive(w)
