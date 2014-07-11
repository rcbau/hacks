#!/usr/bin/python

import datetime
import json
import os
import pytz
import time

from launchpadlib.launchpad import Launchpad


CACHEDIR = '/tmp/launchpadlib-cache'


def get_bug(number):
    launchpad = Launchpad.login_with(
        'openstack-lp-scripts', 'production', CACHEDIR,
        credentials_file=os.path.expanduser('~/.lp'))
    return launchpad.bugs[number]


def get_bug_age(number):
    if not os.path.exists('/tmp/lp_bug_ages'):
        os.makedirs('/tmp/lp_bug_ages')

    filename = '/tmp/lp_bug_ages/%s' % number
    if not os.path.exists(filename):
        bug = get_bug(number)
        epoch = time.mktime(bug.date_created.timetuple())
        with open(filename, 'w') as f:
            f.write(json.dumps(epoch))
    else:
        with open(filename) as f:
            epoch = json.loads(f.read())

    epoch_dt = datetime.datetime.fromtimestamp(epoch, tz=pytz.utc)
    return datetime.datetime.now(tz=pytz.utc) - epoch_dt


if __name__ == '__main__':
    print get_bug_age(1302831)
