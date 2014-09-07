#!/usr/bin/python

# Attempt to calculate who should be an extra ATC, based on co-authored-by

import re

import utils


AUTHOR_RE = re.compile('^Author: (.*) <(.*)>$')
CO_AUTHOR_1_RE = re.compile('Co-authored-by: (.*) ?<(.*)>', re.IGNORECASE)
CO_AUTHOR_2_RE = re.compile('Co-authored-by: (.*)', re.IGNORECASE)

authors = {}
coauthors = {}
names = {}

stdout = utils.runcmd('git log --since 2014-04-01')
for line in stdout.split('\n'):
    m = AUTHOR_RE.match(line)
    if m:
        authors[m.group(2)] = True

    line = line.lstrip()
    if line.lower().startswith('co-authored-by'):
        m = CO_AUTHOR_1_RE.match(line)
        if m:
            # Check for multiple email addresses for the same name
            if m.group(1) in names:
                continue

            coauthors.setdefault(m.group(2), [])
            if not m.group(1) in coauthors[m.group(2)]:
                coauthors[m.group(2)].append(m.group(1).rstrip())
            names[m.group(1)] = True
            continue

        m = CO_AUTHOR_2_RE.match(line)
        if m:
            coauthors.setdefault(m.group(1), ['Unknown'])
            continue

        print 'Unparsed: %s' % line


for email in coauthors:
    if not email in authors:
        print 'Compute: %s (%s) [September 2015]' % (coauthors[email][0],
                                                     email)
