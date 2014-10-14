#!/usr/bin/python

import datetime
import json
import sys
import urllib

# Show me a history of someones reviews in a given project

def dump_history(component, username):
    d = datetime.datetime.now()
    d -= datetime.timedelta(days=30)

    while d < datetime.datetime.now():
        try:
            r = urllib.urlopen('http://www.rcbops.com/gerrit/merged/%d/%d/'
                               '%d_reviews_verbose.json'
                               %(d.year, d.month, d.day))
            j = r.read()
            data = json.loads(j)
        except:
            data = {}

        if username in data:
            reviews = []
            for review in data[username]:
                if review['project'] != component:
                    continue
                r = ("""
http://review.openstack.org/#/c/%s/%s
%s: %s
%s""" %(review['number'], review['patchset'], review['type'], review['value'],
        review['comment']))
                reviews.append(r)

            if reviews:
                print
                print '******************************************************'
                print '%d/%d/%d' %(d.day, d.month, d.year)
                print '******************************************************'
                print '\n'.join(reviews)

        d += datetime.timedelta(days=1)


if __name__ == '__main__':
    dump_history(sys.argv[1], sys.argv[2])
