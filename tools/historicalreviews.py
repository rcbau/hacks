#!/usr/bin/python

import datetime
import reviews
import sys
import time

# Show me a history of someones reviews in a given project

def dump_history(component, username):
    rvs = reviews.reviewed_by('openstack/nova', username)
    print '%s reviews found' % len(rvs)

    for review in rvs:
        newest = 0
        out = []
        out.append('%s %s (%s)' %(review['number'], review['subject'],
                                  review['status']))
        out.append('    by %s' % review['owner'].get('email', review['owner']))

        for ps in review.get('patchSets', []):
            for approval in ps.get('approvals', []):
                if approval['by'].get('username', '') == username:
                    out.append('    # %s: %15s %s %s'
                               %(ps['number'], approval['type'],
                                 approval['value'], approval['by']['username']))
                    if int(approval['grantedOn']) > newest:
                        newest = int(approval['grantedOn'])

        if time.time() - newest < 60 * 24 * 3600:
            print
            print '\n'.join(out)



if __name__ == '__main__':
    dump_history(sys.argv[1], sys.argv[2])
