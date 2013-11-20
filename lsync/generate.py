#!/usr/bin/python

# Generate our lsync configs based on a config language, because they were
# getting really big

import sys
import yaml

import templates


if __name__ == '__main__':
    config = {}
    with open('lsync.yaml', 'r') as f:
        config = yaml.load(f.read())

    sys.stdout.write(templates.settings % locals())
    for system in config:
        sys.stdout.write('-- %s\n\n' % system)
        flags = config[system]['flags']

        for target in config[system]['targets']:
            for source in config[system]['sources']:
                sys.stdout.write(templates.sync % locals())

        sys.stdout.write('\n')
