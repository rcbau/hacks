#!/usr/bin/python

# Turn a trello export into a nice report of all the things we've done

import json
import sys

with open('/tmp/input.json') as f:
    j = json.loads(f.read())

done_id = None
for l in j['lists']:
    if l['name'] == 'Done':
        done_id = l['id']

person = {}
for member in j['members']:
    person[member['id']] = member['fullName']

done_by = {}
for card in  j['cards']:
    if card['closed']:
        continue
    
    if card['idList'] == done_id:
        who = []
        for member in card['idMembers']:
            who.append(person[member])
        who = ', '.join(who)

        done_by.setdefault(who, [])
        done_by[who].append(card['name'])

for doer in sorted(done_by.keys()):
    print doer
    for work in done_by[doer]:
        print '    - %s' % work
    print
