#!/usr/bin/python

# Read irc logs from our private channel and post them to our wiki

import json
import os
import re
import sys
import textwrap

from simplemediawiki import MediaWiki


with open(os.path.expanduser('~/.mediawiki'), 'r') as f:
    conf = json.loads(f.read())

wiki = MediaWiki(conf['url'])

day_re = re.compile('^--- Day changed (.*)$')
human_re = re.compile('.*<([^>]+)>.*')

days = []


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
    days.append(title)


if __name__ == '__main__':
    login = make_wiki_login_call({'action': 'login'})
    token = make_wiki_login_call({'action': 'login',
                                  'lgtoken': login['login']['token']})

    day = None
    content = []
    with open(os.path.expanduser(conf['logpath']), 'r') as f:
        l = f.readline()
        while l:
            if l.startswith('--- '):
                m = day_re.match(l)
                if m:
                     if content:
                         post_page('rcbau irc log for %s' % day,
                                   ''.join(content))
                         content = []
                     day = m.group(1)
            elif day:
                lines = textwrap.wrap(l.rstrip(), 120)

                m = human_re.match(l)
                if m and len(m.group(1)) > 1:
                    content.append(' \'\'\'%s\'\'\'\n'
                                   % '\n \'\'\'      '.join(lines))
                elif l[7] == '*':
                    content.append(' \'\'%s\'\'\n'
                                   % '\n \'\'      '.join(lines))
                else:
                    content.append(' %s\n' % '\n       '.join(lines))

            l = f.readline()

    if day and content:
        post_page('rcbau irc log for %s' % day,
                  ''.join(content))

    if days:
        post_page('rcbau irc log index',
                  '* [[%s]]' % ']]\n* [['.join(days))
