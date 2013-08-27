#!/usr/bin/python

# Read irc logs from our private channel and post them to our wiki

import json
import os
import re
import sys
import textwrap
import wiki


with open(os.path.expanduser('~/.mediawiki'), 'r') as f:
    conf = json.loads(f.read())

day_re = re.compile('^--- Day changed (.*)$')
human_re = re.compile('.*<([^>]+)>.*')


if __name__ == '__main__':
    w = wiki.Wiki(conf['url'], conf['username'], conf['password'])

    day = None
    days = []
    content = []

    with open(os.path.expanduser(conf['logpath']), 'r') as f:
        l = f.readline()
        while l:
            if l.startswith('--- '):
                m = day_re.match(l)
                if m:
                     if content:
                         title = 'rcbau irc log for %s' % day
                         w.post_page(title, ''.join(content))
                         days.append(title)
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
        title = 'rcbau irc log for %s' % day
        w.post_page(title, ''.join(content))
        days.append(title)

    if days:
        w.post_page('rcbau irc log index',
                    '* [[%s]]' % ']]\n* [['.join(days))
