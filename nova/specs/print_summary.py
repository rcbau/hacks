#!/usr/bin/python


import json
import sys


release = sys.argv[1]

with open('%s.json' % release) as f:
    j = json.loads(f.read())

with open('proposed-%s/__merged__' % release) as f:
    merged = json.loads(f.read())
with open('proposed-%s/__abandoned__' % release) as f:
    abandoned = json.loads(f.read())

for topic in sorted(j):
    if topic == '__ignore__':
        continue
    if topic == '__previously_approved__':
        continue

    print '<br/><br/><b>%s</b><br/><br/>' % topic
    print '<ul>'

    for title in sorted(j[topic]):
        reviews = []
        for review in sorted(j[topic][title]):
            attrs = []
            attr_str = ''

            if review in j['__previously_approved__']:
                attrs.append('fast tracked')
            if review in merged:
                attrs.append('approved')
            if review in abandoned:
                attrs.append('abandoned')
            if attrs:
                attr_str = ' <b>(%s)</b>' % ', '.join(attrs)

            reviews.append('<a href="https://review.openstack.org/#/c/%s">'
                           'review %s</a>%s' %(review, review, attr_str))

        print '<li>%s: %s.' %(title, '; '.join(reviews))

    print '</ul>'
    print
