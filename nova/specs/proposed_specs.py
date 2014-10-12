#!/usr/bin/python

# Run this from a directory containing a checkout of nova-specs


import json
import re
import subprocess
import sys


def runcmd(cmd):
    sys.stderr.write('Executing command: %s\n' % cmd)
    obj = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = obj.communicate()
    returncode = obj.returncode
    return stdout


if __name__ == '__main__':
    juno_spec_re = re.compile('.*specs/juno/.*\.rst.*')

    kilo_spec_re = re.compile('.*specs/kilo/.*\.rst.*')
    kilo_impl_re = re.compile('.*specs/kilo/implemented/.*\.rst.*')


    for line in runcmd('ssh review.openstack.org gerrit query '
                       '--format=json --current-patch-set '
                       'project:openstack/nova-specs').split('\n'):
        if not line:
            continue

        j = json.loads(line)
        if not 'project' in j:
            continue
        #if j.get('status') == 'MERGED':
        #    continue

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

        if 'kilo' in spec_match:
            with open('/tmp/patches/%s' % j['number'], 'w') as f:
                f.write(diff)
