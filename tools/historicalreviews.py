#!/usr/bin/python

import datetime
import reviews
import sys

# Show me a history of someones reviews in a given project

def dump_history(component, username):
    rvs = reviews.reviewed_by('openstack/nova', username)
    print '%s reviews found' % len(rvs)

    for review in rvs:
        print
        print '%s %s (%s)' %(review['number'], review['subject'],
                             review['status'])
        print '    by %s' % review['owner'].get('email', review['owner'])

        for ps in review.get('patchSets', []):
            for approval in ps.get('approvals', []):
                if approval['by'].get('username', '') == username:
                    print '    # %s: %s %s' %(ps['number'],
                                              approval['value'],
                                              approval['by']['username'])



if __name__ == '__main__':
    dump_history(sys.argv[1], sys.argv[2])
