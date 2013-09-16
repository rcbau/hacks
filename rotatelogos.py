#!/usr/bin/python

# Read irc logs from our private channel and post them to our wiki

import json
import os
import random
import sys
import wiki


with open(os.path.expanduser('~/.mediawiki'), 'r') as f:
    conf = json.loads(f.read())


if __name__ == '__main__':
    w = wiki.Wiki(conf['url'], conf['username'], conf['password'])

    possible = w.get_page('Possible future wiki logos').split('\n')
    random.shuffle(possible)

    main_page = w.get_page('Main Page').split('\n')
    archive = w.get_page('Former wiki logos').split('\n')
    archive.append(main_page[0])

    if possible:
        new_logo = possible[0]
    else:
        new_logo = '[[File:Trainhassailed.png]]'
        # new_logo = [[File:Meme harder.png]]

    w.post_page('Possible future wiki logos', '\n'.join(possible[1:]))
    w.post_page('Former wiki logos', '\n'.join(archive))

    main_page = '%s\n%s' %(new_logo, '\n'.join(main_page[1:]))
    w.post_page('Main Page', main_page)
