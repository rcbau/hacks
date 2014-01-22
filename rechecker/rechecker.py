# Copyright 2013 Rackspace Australia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import datetime
import json
import os
import paramiko
import random
import subprocess
import sys
import time

hostname = 'review.openstack.org'
hostport = 29418
username = 'mikalstill'
keyfile = '/home/mikal/.ssh/id_gerrit'

def check(review):
    # TODO(mikal): more to paramiko as well
    print '%s Considering %s' % (datetime.datetime.now(), review)
    out = subprocess.check_output(
        ('ssh review.openstack.org gerrit query '
         '--format json --current-patch-set '
         '--all-approvals --comments %s'
         % review), shell=True, stderr=subprocess.PIPE)
    gerrit = json.loads(out.split('\n')[0])

    patchset = gerrit['patchSets'][-1]
    patch_created = patchset['createdOn']
    patch_verified = patch_created
    print ('%s Patchset created at %s (%s)'
           % (datetime.datetime.now(), patch_created,
              datetime.datetime.fromtimestamp(patch_created)))

    if not 'approvals' in patchset:
        print '%s No approvals, skipping' % datetime.datetime.now()
        return
    
    for approval in patchset['approvals']:
        #print '%s Approval by %s, type %s' % (datetime.datetime.now(),
        #                                      approval['by']['username'],
        #                                      approval['type'])
        if not approval['by']['username'] == 'jenkins':
            continue
        if not approval['type'] == 'VRIF':
            continue
        patch_verified = approval['grantedOn']
        print ('%s Patchset verified at %s (%s)'
               % (datetime.datetime.now(), patch_verified,
                  datetime.datetime.fromtimestamp(patch_verified)))

    last_recheck = 0
    for comment in gerrit.get('comments', []):
        found = 0
        #print ('%s Comment %s by %s'
        #       % (datetime.datetime.now(),
        #          comment['message'][0:60].replace('\n', ' '),
        #          comment['reviewer']['username']))
        for check in ['\nrecheck ', '\nreverify ', 'Starting gate',
                      'Restored', '; Approved', ': Rebased',
                      'Uploaded patch set', 'Abandoned code review expired']:
            if comment['message'].find(check) != -1:
                if comment['timestamp'] > last_recheck:
                    last_recheck = comment['timestamp']
                    print ('%s Patchset rechecked at %s (%s)'
                           % (datetime.datetime.now(), last_recheck,
                              datetime.datetime.fromtimestamp(last_recheck)))

        if comment['reviewer']['username'] == 'jenkins':
            patch_verified = comment['timestamp']
            print ('%s Patchset verified at %s (%s)'
                   % (datetime.datetime.now(), patch_verified,
                      datetime.datetime.fromtimestamp(patch_verified)))

    recheck = False
    jenkins_old = time.time() - patch_verified > 7 * 24 * 3600
    recheck_age = time.time() - last_recheck
    recent_recheck = recheck_age < 12 * 3600
    print ('%s Jenkins old %s, recent recheck %s'
               % (datetime.datetime.now(), jenkins_old, recent_recheck))

    if jenkins_old and not recent_recheck:
        recheck = True
    print '%s Recheck %s %s' % (datetime.datetime.now(), review, recheck)
    if recheck:
        out = subprocess.check_output(
            ('ssh review.openstack.org gerrit review -m "\'recheck no bug\'" %s'
            % patchset['revision']), shell=True, stderr=subprocess.PIPE)


def stream_events():
    last_event = time.time()
    wait_time = 300 + random.randint(0, 300)

    # Connect
    transport = paramiko.Transport((hostname, hostport))
    transport.start_client()

    # Authenticate with the key
    key = paramiko.RSAKey.from_private_key_file(keyfile)
    transport.auth_publickey(username, key)

    channel = transport.open_session()
    channel.exec_command('gerrit stream-events')

    print '%s Connected to gerrit' % datetime.datetime.now()
    data = ''

    try:
        while True:
            if not channel.recv_ready():
                if time.time() - last_event > wait_time:
                    print ('%s Possibly stale connection to gerrit'
                           % datetime.datetime.now())
                    return
                time.sleep(1)

            else:
                d = channel.recv(1024)
                if not d:
                    print '%s Connection closed' % datetime.datetime.now()
                    return

                last_event = time.time()
                print '%s Read %d bytes' %(datetime.datetime.now(), len(d))
                data += d

                if data.find('\n') != -1:
                    lines = data.split('\n')
                    for line in lines[:-1]:
                        try:
                            decode = json.loads(line)
                            if decode['type'] == 'comment-added':
                                check(decode['change']['number'])
                        except Exception as e:
                            print '%s Error: %s' %(datetime.datetime.now(), e)

                    data = lines[-1]

    finally:
        transport.close()


if __name__ == '__main__':
    random.seed()
    while True:
        stream_events()
