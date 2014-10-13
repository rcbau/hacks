#!/usr/bin/python

# Run this from a directory containing a checkout of nova-specs


import json
import re
import subprocess
import sys


RELEASE_TARGET = 'juno'


def runcmd(cmd):
    print 'Executing command: %s\n' % cmd
    obj = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = obj.communicate()
    returncode = obj.returncode
    return stdout


if __name__ == '__main__':
    juno_spec_re = re.compile('.*specs/juno/.*\.rst.*')

    kilo_spec_re = re.compile('.*specs/kilo/.*\.rst.*')
    kilo_impl_re = re.compile('.*specs/kilo/implemented/.*\.rst.*')

    merged = []
    for line in runcmd('ssh review.openstack.org gerrit query '
                       '--format=json --current-patch-set '
                       'project:openstack/nova-specs').split('\n'):
        if not line:
            continue

        j = json.loads(line)
        if not 'project' in j:
            continue

        print 'Patch: %s' % j['number']
        print 'Ref: %s' % j['currentPatchSet']['ref']

        spec_match = []
        implemented = False
        diff = runcmd('git fetch '
                      'https://mikalstill@review.openstack.org/openstack/'
                      'nova-specs '
                      '%s && git format-patch -1 --stdout FETCH_HEAD'
                      % j['currentPatchSet']['ref'])
        for line in diff.split('\n'):
            m = kilo_impl_re.match(line)
            if m:
                implemented = True

            m = juno_spec_re.match(line)
            if m:
                spec_match.append('juno')

            m = kilo_spec_re.match(line)
            if m:
                spec_match.append('kilo')

        if implemented:
            continue

        if RELEASE_TARGET in spec_match:
            print 'Writing to /tmp/patches/%s' % j['number']
            with open('/tmp/patches/%s' % j['number'], 'w') as f:
                f.write(diff)

            if j.get('status') == 'MERGED':
                merged.append(j['number'])

        print

    with open('/tmp/patches/__merged__', 'w') as f:
        f.write(json.dumps(merged))
