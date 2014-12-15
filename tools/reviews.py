#!/usr/bin/python

import argparse
import json

import utils


def component_reviews(component, reviewer=None):
    cmd = ('ssh review.openstack.org gerrit query --format json '
           '--current-patch-set --files --dependencies project:%s status:open '
           'limit:10000'
           % component)
    if reviewer:
        cmd += ' reviewer:%s' % reviewer
    else:
        cmd += ' --all-approvals'

    def _filter(packet, value):
        if packet.get('project') == value:
            return True
        return False
        
    return get_reviews(cmd, _filter, component)


def author_reviews(author, reviewer=None):
    cmd = ('ssh review.openstack.org gerrit query --format json '
           '--current-patch-set --files --dependencies owner:%s status:open '
           'limit:10000'
           % author)
    if reviewer:
        cmd += ' reviewer:%s' % reviewer
    else:
        cmd += ' --all-approvals'

    def _filter(packet, value):
        if packet.get('owner', {}).get('username') == value:
            return True
        return False

    return get_reviews(cmd, _filter, author)


def reviewed_by(component, reviewer):
    cmd = ('ssh review.openstack.org gerrit query --format json project:%s '
           '--patch-sets --all-approvals reviewer:%s limit:10000'
           %(component, reviewer))

    def _filter(packet, value):
        if packet.get('project') == value:
            return True
        return False
        
    return get_reviews(cmd, _filter, component)


def get_reviews(cmd, filt, value):
    stdout = utils.runcmd(cmd)

    reviews = []
    for line in stdout.split('\n'):
        if not line:
            continue

        try:
            packet = json.loads(line)
            if filt(packet, value):
                reviews.append(packet)
        except ValueError as e:
            print 'Could not decode:'
            print '  %s' % line
            print '  Error: %s' % e

    return reviews

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', default='mikalstill',
                        help='The username (if any) to filter by')
    ARGS = parser.parse_args()
    
    reviews = component_reviews('openstack/nova', reviewer=ARGS.username)
    # reviews = author_reviews('mikalstill')
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
