#!/usr/bin/python

# Read irc logs from our private channel and post them to our wiki

import datetime
import json
import os
import random
import sys
import wiki


with open(os.path.expanduser('~/.mediawiki'), 'r') as f:
    conf = json.loads(f.read())['ircbot']


if __name__ == '__main__':
    w = wiki.Wiki(conf['url'], conf['username'], conf['password'])

    main_page = w.get_page('Main Page').split('\n')
    archive = w.get_page('Former wiki logos').split('\n')
    archive.append(main_page[0].replace('|right]]', ']]'))

    for extension in ['png', 'jpg', 'jpeg', 'gif']:
        today_title = ('File:%s.%s'
                       %(datetime.datetime.now().strftime('%Y%m%d'),
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
        possible = w.get_page(possible_page).split('\n')
        random.shuffle(possible)

        if len(possible) > 0:
            new_logo = possible[0]
        else:
            print 'No memes! Error time.'
            possible_page = 'Error logos'
            possible = w.get_page(possible_page).split('\n')
            random.shuffle(possible)
            new_logo = possible[0]

    new_logo = new_logo.replace(']]', '|right]]')
    if possible_page:
        w.post_page(possible_page, '\n'.join(possible[1:]))
    w.post_page('Former wiki logos', '\n'.join(archive))

    main_page = '%s\n%s' %(new_logo, '\n'.join(main_page[1:]))
    w.post_page('Main Page', main_page)
