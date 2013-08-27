#!/usr/bin/python

# Read irc logs from our private channel and post them to our wiki

import json
import os
import random

from simplemediawiki import MediaWiki


with open(os.path.expanduser('~/.mediawiki'), 'r') as f:
    conf = json.loads(f.read())

wiki = MediaWiki(conf['url'])


def make_wiki_login_call(packet):
    packet.update({'lgname': conf['username'],
                   'lgpassword': conf['password']})
    return wiki.call(packet)

def post_page(title, text):
    page_token = wiki.call({'action': 'query',
                            'prop': 'info',
                            'titles': title,
                            'intoken': 'edit'})
    pages = page_token['query']['pages']
    page_id = pages.keys()[0]

    response = wiki.call({'action': 'edit',
                          'minor': True,
                          'bot': True,
                          'title': title,
                          'text': json.dumps(text).replace('\\n', '\n')[1:-1],
                          'token': pages[page_id]['edittoken']})
    if not 'nochange' in response['edit']:
        print 'Modified %s' % title


def get_page(title):
    response = wiki.call({'action': 'query',
                          'titles': title,
                          'prop': 'revisions',
                          'rvprop': 'content'})
    pages = response['query']['pages']
    page_id = pages.keys()[0]
    return pages[page_id]['revisions'][0]['*']


if __name__ == '__main__':
    login = make_wiki_login_call({'action': 'login'})
    token = make_wiki_login_call({'action': 'login',
                                  'lgtoken': login['login']['token']})

    possible = get_page('Possible future wiki logos').split('\n')
    random.shuffle(possible)

    if possible:
        new_logo = possible[0]
        main_page = get_page('Main Page').split('\n')
        archive = get_page('Former wiki logos').split('\n')
        archive.append(main_page[0])

        # Do the updates
        post_page('Possible future wiki logos', '\n'.join(possible[1:]))
        post_page('Former wiki logos', '\n'.join(archive))

        main_page = '%s\n%s' %(new_logo, '\n'.join(main_page[1:]))
        post_page('Main Page', main_page)
