#!/usr/bin/python

import json

import utils


def component_reviews(component, reviewer=None):
    cmd = ('ssh review.openstack.org gerrit query --format json '
           '--current-patch-set project:%s status:open '
           'limit:10000'
           % component)
    if reviewer:
        cmd += ' reviewer:%s' % reviewer
    else:
        cmd += ' --all-approvals'
    stdout = utils.runcmd(cmd)

    reviews = []
    for line in stdout.split('\n'):
        if not line:
            continue

        try:
            packet = json.loads(line)
            if packet.get('project') == component:
                reviews.append(packet)
        except ValueError as e:
            print 'Could not decode:'
            print '  %s' % line
            print '  Error: %s' % e

    return reviews

if __name__ == '__main__':
    reviews = component_reviews('openstack/nova', reviewer='mikal@stillhq.com')
    print '%s reviews found' % len(reviews)

    for review in reviews:
        print
        for key in sorted(review.keys()):
            if key == 'patchSets':
                print '%s:' % key
                for ps in review[key]:
                    print '    %s' % ps
            else:
                print '%s: %s' %(key, review[key])
