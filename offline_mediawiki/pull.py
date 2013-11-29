#!/usr/bin/python

# Download a local copy of the wiki

import json
import os
import wiki


with open(os.path.expanduser('~/.mediawiki'), 'r') as f:
    conf = json.loads(f.read())[os.environ['USER']]


if __name__ == '__main__':
    w = wiki.Wiki(conf['url'], conf['username'], conf['password'])

    if not os.path.exists('.mediawiki'):
        os.makedirs('.mediawiki')

    for title in w.all_pages():
        print title
        data = w.get_page(title).encode('ascii', 'replace')
        title = title.replace('/', '!slash!')
        with open(title, 'w') as f:
            f.write(data)
        with open(os.path.join('.mediawiki', title), 'w') as f:
            f.write(data)
