#!/usr/bin/python

import os

import reviews
import utils


RELEASE = 'juno'
APPROVED_SPECS = []
PROPOSED_SPECS = []


def print_heading(header):
    print
    print '*****************************************************************'
    print header
    print '*****************************************************************'


def approval_to_string(approval):
    return '%s:%s(%s)' % (approval['by'].get('username',
                                             repr(approval['by'])),
                          approval['type'],
                          approval['value'])
    

def get_votes(review):
    votes = []
    lowest = 0
    highest = 0

    for approval in review.get('currentPatchSet', {}).get('approvals', []):
        lowest = min(int(approval['value']), lowest)
        highest = max(int(approval['value']), highest)
        votes.append(approval_to_string(approval))

    return votes, lowest, highest
    

PRINTED = []
def print_review(review, message):
    global PRINTED

    if review in PRINTED:
        return

    if review['subject'].startswith('WIP '):
        return
    if review['subject'].startswith('WIP:'):
        return

    for approval in review.get('currentPatchSet', {}).get('approvals', []):
        if approval['by'].get('username', '') == 'mikalstill':
            return
        if approval['type'] in ['APRV', 'Workflow'] and approval['value'] == '1':
            return

    votes, lowest, highest = get_votes(review)
    if lowest == -2:
        return

    print review['subject']
    if message:
        print '    %s' % message
    print '    %s (%s) in %s' % (review['owner']['username'],
                                 review.get('topic'),
                                 review.get('project'))
    print '    Votes: %s' % ' '.join(votes)
    print '    %s' % review['url']
    print

    PRINTED.append(review)


def filter_obvious(possible):
    for review in possible:
        if review.get('branch') != 'master':
            continue
        if review.get('status') == 'WORKINGPROGRESS':
            continue

        yield review


def targets():
    global APPROVED_SPECS
    global PROPOSED_SPECS
    
    # Find translation reviews
    print_heading('Translation reviews')
    possible = reviews.component_reviews('openstack/nova')
    for review in filter_obvious(possible):
        if not review.get('topic', '').startswith('transifex/'):
            continue

        print_review(review, '')

    # Turbo Hipster
    print_heading('Turbo hipster')
    possible = reviews.component_reviews('stackforge/turbo-hipster')
    for review in filter_obvious(possible):
        print_review(review, '')

    # Governance
    print_heading('Governance')
    possible = reviews.component_reviews('openstack/governance')
    for review in filter_obvious(possible):
        print_review(review, '')
        
    # Other nova
    previously_reviewed = {}
    plus_two = []
    unapproved_spec_reviews = []
    approved_spec_reviews = []
    bug_reviews = []
    uncategorized_reviews = []

    for component in ['openstack/nova', 'openstack/python-novaclient']:
        possible = reviews.component_reviews(component)
        for review in filter_obvious(possible):
            topic = review.get('topic', '')
            votes, lowest, highest = get_votes(review)

            # Determine my most recent votes
            vote = ''
            for ps in review['patchSets']:
                for approval in ps.get('approvals', []):
                    if approval['by'].get('username', '') == 'mikalstill':
                        vote = approval_to_string(approval)

            if vote:
                previously_reviewed.setdefault(vote, [])
                previously_reviewed[vote].append(review)
            elif highest == 2:
                plus_two.append(review)
            elif topic.startswith('bp/'):
                bp_name = review.get('topic', '').split('/')[1]
                if not bp_name in APPROVED_SPECS:
                    if bp_name in PROPOSED_SPECS:
                        unapproved_spec_reviews.append(
                            (review, 'Unapproved spec, spec proposed'))
                    else:
                        unapproved_spec_reviews.append(
                            (review, 'Unapproved spec'))
                else:
                    approved_spec_reviews.append(review)

            elif topic.startswith('bug/'):
                bug_reviews.append(review)

            else:
                uncategorized_reviews.append(review)

    for vote in sorted(previously_reviewed.keys()):
        print_heading('Previously reviewed -- %s' % vote)
        for review in previously_reviewed[vote]:
            print_review(review, '')
                
    print_heading('Has a +2')
    for review in plus_two:
        print_review(review, '')

    print_heading('Unapproved blueprints')
    for review, msg in unapproved_spec_reviews:
        print_review(review, msg)

    print_heading('Bug fix reviews')
    for review in bug_reviews:
        print_review(review, '')

    print_heading('Specs to review')
    possible = reviews.component_reviews('openstack/nova-specs')
    for review in filter_obvious(possible):
        print_review(review, '')

    print_heading('Approved blueprints')
    for review in approved_spec_reviews:
        print_review(review, '')

    print_heading('Uncategorized')
    for review in uncategorized_reviews:
        print_review(review, '')


if __name__ == '__main__':
    print utils.runcmd('cd ~/src/openstack/nova-specs; '
                       'git checkout master; '
                       'git pull')
    print
    print '-----------------------------------------------------------------'
    print

    for ent in os.listdir(os.path.expanduser('~/src/openstack/nova-specs'
                                             '/specs/%s'
                                             % RELEASE)):
        if not ent.endswith('.rst'):
            continue
        APPROVED_SPECS.append(ent[:-4])
    print 'Approved specs: %s' % ' '.join(APPROVED_SPECS)
    print

    possible = reviews.component_reviews('openstack/nova-specs')
    for review in filter_obvious(possible):
        try:
            bp_name = review.get('topic', 'bp/nosuch').split('/')[1]
        except:
            bp_name = review.get('topic', '')

        PROPOSED_SPECS.append(bp_name)
    print 'Proposed specs: %s' % ' '.join(PROPOSED_SPECS)
    print

    targets()

    print
    print 'I printed %d reviews' % len(PRINTED)
