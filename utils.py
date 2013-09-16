#!/usr/bin/python

import json
import subprocess
import unicodedata


def execute(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    p.wait()
    return (p.stdout.readlines(), p.returncode)


def get_patchset_info(review):
    out, exit = execute('ssh -i ~/.ssh/id_gerrit review.openstack.org gerrit '
                        'query %s --patch-sets --format JSON' % review)
    data = json.loads(out[0])
    return data


def Normalize(value):
    normalized = unicodedata.normalize('NFKD', unicode(value))
    normalized = normalized.encode('ascii', 'replace')
    normalized.replace('\r', '')
    normalized.replace('\n', ' ')
    return str(normalized)
