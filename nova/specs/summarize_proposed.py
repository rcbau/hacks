#!/usr/bin/python

import json
import os
import sys


print 'Which release are we talking about here?'
release = sys.stdin.readline().rstrip()


json_filename = '%s.json' % release
if not os.path.exists(json_filename):
    data = {}
else:
    with open(json_filename) as f:
        data = json.loads(f.read())


patches = []
for topic in data:
    for title in data[topic]:
        patches.extend(data[topic][title])
print 'Already seen patches: %s (%d in total)' %(patches, len(patches))


for patch in os.listdir('proposed-%s' % release):
    if not patch in patches:
        print '------------------------------------------------------------------------'
        print 'Patch: %s' % patch
        previously_approved = ''
        with open('proposed-%s/%s' %(release, patch)) as f:
            lines = f.readlines()[0:100]
            for line in lines:
                if line.lower().startswith('previously-approved: '):
                    previously_approved = ':'.join(line.split(':')[1:]).lstrip()
            
            print ''.join(lines)

        print
        print '*****'
        print
        print 'What topic?'
        topic = sys.stdin.readline().rstrip()
        print 'What title?'
        title = sys.stdin.readline().rstrip()
        data.setdefault(topic, {})
        data[topic].setdefault(title, [])
        data[topic][title].append(patch)
        if previously_approved:
            data.setdefault('__previously_approved__', [])
            data['__previously_approved__'].append(patch)

        with open(json_filename, 'w') as f:
            f.write(json.dumps(data, indent=4, sort_keys=True))

        print '------------------------------------------------------------------------'
