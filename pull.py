#!/usr/bin/python

# Download a local copy of the wiki

import json
import os
import wiki


with open(os.path.expanduser('~/.mediawiki'), 'r') as f:
    conf = json.loads(f.read())


if __name__ == '__main__':
    w = wiki.Wiki(conf['url'], conf['username'], conf['password'])

    os.makedirs('.mediawiki')
    for title in w.all_pages():
        print title
        with open(title, 'w') as f:
            f.write(w.get_page(title).encode('ascii', 'replace'))
        with open(os.path.join('.mediawiki', title), 'w') as f:
            f.write(w.get_page(title).encode('ascii', 'replace'))
