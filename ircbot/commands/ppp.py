#!/usr/bin/python2.4

# Add entries to a PPP report on the wiki via IRC

import datetime
import json
import os
import re

import wiki


WIKI_SECTION_RE = re.compile('=+ (.*) =+')


class PPPHelper(object):
    def __init__(self, log, conf):
        self.log = log
        self.conf = conf

    # Things you're expected to implement
    def Name(self):
        """Who am I?"""
        return 'PPPHelper'

    def Verbs(self):
        """Return the verbs which this module supports

        Takes no arguments, and returns an array of strings.
        """

        return ['ppp']

    def Help(self, verb):
        """Display help for a verb

        Takes the name of a verb, and returns a string which is the help
        message for that verb.
        """
        if verb == 'ppp':
            return ('Used to add an entry to your PPP report. Simply try '
                    'something like: "ppp <section> <text>". For example '
                    'you might do "ppp progress Shaved a yak."')
        return ''

    def Command(self, user, channel, verb, line):
        """Execute a given verb with these arguments

        Takes the verb which the user entered, and the remainder of the line.
        Returns a string which is sent to the user.
        """
        if verb == 'ppp':
            tuesday = datetime.datetime.now()
            while tuesday.weekday() != 1:
                tuesday += datetime.timedelta(days=1)

            elems = line.split(' ')
            section = elems[0]
            if elems[-1].startswith('[') and elems[-1].endswith(']'):
                user = elems[-1][1:-1]
                line = ' '.join(elems[1:-1])
            else:
                line = ' '.join(elems[1:])

            user = user.rstrip('_')
            user = self.conf['ppp']['usermap'].get(user, user)
            title = '%s PPP report %04d%02d%02d' %(user, tuesday.year,
                                                   tuesday.month, tuesday.day)
            self.log('Adding PPP entry for %s' % title)

            ppp_line = '* %s' % line
            self.log('... section %s' % section)
            self.log('    entry "%s"' % line)

            with open(os.path.expanduser('~/.mediawiki'), 'r') as f:
                wikiconf = json.loads(f.read())['ircbot']
            w = wiki.Wiki(wikiconf['url'], wikiconf['username'],
                          wikiconf['password'])
            text = w.get_page(title).split('\n')

            # This is a bit horrible. There is no support in the mediawiki api for
            # grabbing just one section, so we have to grab the entire page and then
            # parse it into its headings. However, we can assume that there are only
            # three headings on a PPP page.
            parsed = {'Progress': [],
                      'Plans': [],
                      'Problems': [],
                      'Unknown': []}
            page_section = 'Unknown'
            for page_line in text:
                m = WIKI_SECTION_RE.match(page_line)
                if m:
                    page_section = m.group(1)
                elif page_line:
                    parsed[page_section].append(page_line)

            text = []
            for report_section in ['Progress', 'Plans', 'Problems']:
                text.append('== %s ==' % report_section)
                for page_line in parsed[report_section]:
                    text.append(page_line)

                self.log('    %s vs %s' %(report_section.lower(), section.lower()))
                if report_section.lower() == section.lower():
                    if not ppp_line in text:
                        self.log('    adding the new ppp line')
                        text.append(ppp_line)
                text.append('')

            for page_line in text:
                self.log('*** %s' % page_line)

            w.post_page(title, '\n'.join(text))
            yield(channel, 'msg', 'PPP entry added to %s' % title)

        yield

    def NoticeUser(self, channel, user):
        """We just noticed this user. Either they joined, or we did."""
        yield

    def HeartBeat(self):
        """Gets called at regular intervals"""
        yield

    def Cleanup(self):
        """We're about to be torn down."""
        pass


def Init(log, conf):
    """Initialize all command classes."""
    yield PPPHelper(log, conf)
