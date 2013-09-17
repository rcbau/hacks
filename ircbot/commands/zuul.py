#!/usr/bin/python2.4

# A simple zuul watcher bot

import json
import sqlite3
import subprocess
import time
import urllib2

import utils

class ZuulWatcher(object):
    def __init__(self, log, conf):
        self.log = log
        self.conf = conf
        self.database = sqlite3.connect('commands/zuul.sqlite',
                                        detect_types=sqlite3.PARSE_DECLTYPES)
        self.database.row_factory = sqlite3.Row
        self.cursor = self.database.cursor()

        self.statuses = {}

        # Create tables
        try:
            self.cursor.execute('create table patchsets('
                                'ident int, number int, author varchar(255), '
                                'monitored int, seen datetime)')
        except sqlite3.OperationalError:
            pass

        self.database.commit()

    # Things you're expected to implement
    def Name(self):
        """Who am I?"""
        return 'zuulwatcher'

    def Verbs(self):
        """Return the verbs which this module supports

        Takes no arguments, and returns an array of strings.
        """

        return []

    def Help(self, verb):
        """Display help for a verb

        Takes the name of a verb, and returns a string which is the help
        message for that verb.
        """
        return ''

    def Command(self, user, channel, verb, line):
        """Execute a given verb with these arguments

        Takes the verb which the user entered, and the remainder of the line.
        Returns a string which is sent to the user.
        """
        yield

    def NoticeUser(self, channel, user):
        """We just noticed this user. Either they joined, or we did."""
        yield

    def HeartBeat(self):
        """Gets called at regular intervals"""

        channel = '#%s' % self.conf['zuul']['channel']

        try:
            remote = urllib2.urlopen('http://zuul.openstack.org/status.json')
            status = json.loads(remote.read())
            remote.close()

            for pipeline in status['pipelines']:
                if pipeline['name'] in ['check', 'gate']:
                    for queue in pipeline['change_queues']:
                        for head in queue['heads']:
                            for review in head:
                                ident, number = review['id'].split(',')
                                self.log('... zuul processing %s, %s'
                                         %(ident, number))
                                owner = None

                                self.cursor.execute('select * from patchsets where '
                                                    'ident=? and number=?',
                                                    [ident, number])
                                rows = self.cursor.fetchall()
                                if rows:
                                    owner = rows[0][2]
                                else:
                                    self.log('    looking up patchset info')
                                    info = utils.get_patchset_info(ident)
                                    for patchset in info['patchSets']:
                                        if patchset['number'] == number:
                                            owner = patchset['uploader']['name']
                                            break

                                    self.cursor.execute('insert into patchsets'
                                                        '(ident, number, author, '
                                                        'monitored, seen) '
                                                        'values(?, ?, ?, ?, ?)',
                                                        [ident, number, owner,
                                                         1, time.time()])
                                    self.database.commit()

                                    if not owner in self.conf['zuul']['usermap']:
                                        continue

                                    yield(channel, 'msg',
                                          ('OMG, %s did some work! %s'
                                           %(owner, review['url'])))

                                nick = self.conf['zuul']['usermap'].get(owner, None)
                                self.log('    nick for %s is %s' %(owner, nick))
                                if nick:
                                    for job in review['jobs']:
                                        self.log('    %s: %s' %(job['name'],
                                                                job['result']))
                                        if not job['result']:
                                            continue
                                        if job['result'] == 'SUCCESS':
                                            continue

                                        key = (ident, number, job['name'])
                                        if key in self.statuses:
                                           continue

                                        self.log('%s, %s status %s: %s'
                                                 %(ident, number, job['name'],
                                                   job['result']))
                                        test = '-'.join(job['name'].split('-')[2:])
                                        voting = ''
                                        if not job['voting']:
                                            voting = ' (non-voting)'
                                        yield(channel, 'msg',
                                              ('%s: %s %s ... %s%s'
                                               %(nick, review['url'], test,
                                                 job['result'], voting)))

                                        self.statuses[key] = True

        except Exception, e:
            self.log('Ignoring exception %s' % e)

    def Cleanup(self):
        """We're about to be torn down."""
        self.database.commit()
        self.cursor.close()


def Init(log, conf):
    """Initialize all command classes."""
    yield ZuulWatcher(log, conf)
