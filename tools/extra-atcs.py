#!/usr/bin/python

# Attempt to calculate who should be an extra ATC, based on co-authored-by
#
# How do I run this?
#
# - change directory to your project, git pull master
# - ./extra-atcs.py --since=2014-04-01 --expires="September 2015" \
#   --program Docs

import argparse
import re

import utils


AUTHOR_RE = re.compile('^Author: (.*) <(.*)>$')
CO_AUTHOR_1_RE = re.compile('Co-authored-by: (.*) ?<(.*)>', re.IGNORECASE)
CO_AUTHOR_2_RE = re.compile('Co-authored-by: (.*)', re.IGNORECASE)

def find_authors(since, program, expires):
    authors = {}
    coauthors = {}
    names = {}

    stdout = utils.runcmd('git log --since %s' % since)
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
            print '%s: %s (%s) [%s]' % (program, coauthors[email][0],
                                        email, expires)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--since', default='2014-04-1',
                        help='When to process from (when the release started)')
    parser.add_argument('--expires', default='September 2015',
                        help='When to grant ATC status until')
    parser.add_argument('--program', default='compute',
                        help='What program to grant access to')
    ARGS = parser.parse_args()

    find_authors(ARGS.since, ARGS.program, ARGS.expires)
