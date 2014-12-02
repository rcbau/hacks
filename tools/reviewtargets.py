#!/usr/bin/python

import argparse
import datetime
import json
import os

import bugs
import reviews
import utils


ARGS = None
RELEASE = 'juno'
APPROVED_SPECS = []
PROPOSED_SPECS = []

OUTPUT = []
HEADERS = []

CONFIG = None


def print_heading(header):
    global OUTPUT
    global HEADERS
    
    OUTPUT.append('<h1><a name="%s">%s</a></h1>'
                  % (header.replace(' ', '_'), header))
    HEADERS.append(header)


def approval_to_string(approval, markup=True):
    s = '%s:%s(%s)' % (approval['by'].get('username',
                                          repr(approval['by'])),
                       approval['type'],
                       approval['value'])
    colors = {'-2': 'red',
              '-1': 'red',
              '0': 'gray',
              '1': 'green',
              '2': 'green'}

    if markup:
        return '<font color="%s">%s</font>' % (colors[approval['value']], s)
    else:
        return s


def get_votes(review, markup=True):
    votes = []
    lowest = 0
    highest = 0

    for approval in review.get('currentPatchSet', {}).get('approvals', []):
        lowest = min(int(approval['value']), lowest)
        highest = max(int(approval['value']), highest)
        votes.append(approval_to_string(approval, markup=markup))

    return votes, lowest, highest
    

PRINTED = []
def print_review(review, message, skip_reviewed_by_me=True, dependancy=False):
    global PRINTED
    global OUTPUT

    local_output = []

    if review in PRINTED:
        return

    for approval in review.get('currentPatchSet', {}).get('approvals', []):
        if (skip_reviewed_by_me
            and approval['by'].get('username', '') == ARGS.username):
            return
        if (approval['type'] in ['APRV', 'Workflow']
            and approval['value'] == '1'):
            return

    if review.get('topic', '').startswith('bug/'):
        try:
            age = bugs.get_bug_age(int(review['topic'].split('/')[1]))
            review['topic'] += ' %s' % age
        except:
            pass

    votes, lowest, highest = get_votes(review)
    if lowest == -2:
        return

    local_output.append('<p><b>%s</b><ul>' % review['subject'])
    if message:
        local_output.append('<li><i>%s</i>' % message)
    local_output.append('<li>%s (%s) in %s' % (review['owner']['username'],
                                               review.get('topic'),
                                               review.get('project')))
    local_output.append('<!-- %s -->' % review)
    if 'dependsOn' in review:
        number = review['dependsOn'][0]['number']
        local_output.append('<li>Depends on: %s' % number)
    local_output.append('<li>Votes: %s' % ' '.join(votes))
    local_output.append('<li><a href="%s">review</a>' % review['url'])
    local_output.append('</ul></p>')

    OUTPUT.extend(local_output)
    PRINTED.append(review)


def filter_obvious(possible):
    for review in possible:
        if review.get('branch') != 'master':
            continue
        if review.get('status') == 'WORKINGPROGRESS':
            continue
        if review['subject'].startswith('WIP '):
            return
        if review['subject'].startswith('WIP:'):
            return

        votes, _, _ = get_votes(review, markup=False)
        skip = False
        for vote in votes:
            if vote.endswith('Workflow(-1)'):
                skip = True
                continue

        if not skip:
            yield review


def targets():
    global APPROVED_SPECS
    global PROPOSED_SPECS
    
    # Find translation reviews
    print_heading('Bot reviews')
    possible = reviews.component_reviews('openstack/nova')
    for review in filter_obvious(possible):
        if (review['currentPatchSet'].get('author', {}).get('username', '')
            != 'proposal-bot'):
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

    # Ironic nova driver
    print_heading('Ironic nova driver, remote repo')
    possible = reviews.component_reviews('openstack/ironic')
    for review in filter_obvious(possible):
        ps = review['patchSets'][-1]
        interesting = False
        for file_details in ps.get('files', {}):
            if file_details.get('file', '').startswith('ironic/nova'):
                interesting = True
        if interesting:
            print_review(review, '')

    # Direct reports, which might not be in repos I track otherwise
    print_heading('Direct reports')
    for username in CONFIG['direct_reports']:
        for review in reviews.author_reviews(username):
            print_review(review, '')

    # Other nova
    previously_reviewed = {}
    plus_two = []
    needs_merge_approve = []
    unapproved_spec_reviews = []
    approved_spec_reviews = []
    bug_reviews = []
    uncategorized_reviews = []
    favorites = []

    for component in ['openstack/nova', 'openstack/python-novaclient',
                      'openstack/nova-specs', 'stackforge/ec2-api']:
        possible = reviews.component_reviews(component)
        for review in filter_obvious(possible):
            topic = review.get('topic', '')
            votes, lowest, highest = get_votes(review)

            # My favorite developers (people who consistently produce high
            # quality code and therefore get a fast pass)
            if review['currentPatchSet']['author'].get('username') in \
              CONFIG['favourites']:
                favorites.append(review)

            # Does this patch just need a merge approval?
            yeps = 0
            merges = 0
            for vote in votes:
                if vote.find(':Code-Review(2)') != -1:
                    yeps += 1
                elif vote.find(':Workflow(2)') != -1:
                    merges += 1
            if yeps > 1 and merges == 0:
                needs_merge_approve.append(review)

            # Determine my most recent votes
            vote = ''
            for ps in review['patchSets']:
                for approval in ps.get('approvals', []):
                    if approval['by'].get('username', '') == ARGS.username:
                        vote = approval_to_string(approval, markup=False)

            if vote:
                previously_reviewed.setdefault(vote, [])
                previously_reviewed[vote].append(review)
            elif highest == 2:
                plus_two.append(review)
            elif (topic.startswith('bp/')
                  and component != 'openstack/nova-specs'):
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
                
    print_heading('Needs merge approval')
    for review in needs_merge_approve:
        print_review(review, '', skip_reviewed_by_me=False)

    print_heading('Favorites')
    for review in favorites:
        print_review(review, '')
                
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', default='mikalstill',
                        help='Your gerrit username')
    ARGS = parser.parse_args()

    with open(os.path.expanduser('~/.reviewtargets')) as f:
        CONFIG = json.loads(f.read())

    print utils.runcmd('cd ~/cache/nova-specs; '
                       'git checkout master; '
                       'git pull')

    for ent in os.listdir(os.path.expanduser('~/cache/nova-specs'
                                             '/specs/%s'
                                             % RELEASE)):
        if not ent.endswith('.rst'):
            continue
        APPROVED_SPECS.append(ent[:-4])

    possible = reviews.component_reviews('openstack/nova-specs')
    for review in filter_obvious(possible):
        try:
            bp_name = review.get('topic', 'bp/nosuch').split('/')[1]
        except:
            bp_name = review.get('topic', '')

        PROPOSED_SPECS.append(bp_name)

    targets()

    for header in HEADERS:
        print '<li><a href="#%s">%s</a>' % (header.replace(' ', '_'),
                                                header)
    print '<br/><br/>'
    print utils.Normalize('\n'.join(OUTPUT))
    print
    print 'I printed %d reviews' % len(PRINTED)
    print 'Generated at: %s' % datetime.datetime.now()
