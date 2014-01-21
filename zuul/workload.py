#!/usr/bin/python

# Copyright 2014 Rackspace Australia
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


# A simple script that draws graphs of zuul workload based on the output of
# the mysql reporter.

import ConfigParser
import datetime
import MySQLdb


def report():
    config = ConfigParser.ConfigParser()
    config.read('/etc/zuul/zuul.conf')
    
    db = MySQLdb.connect(host=(config.get('mysql', 'host')
                               if config.has_option('mysql', 'host') else
                               '127.0.0.1'),
                         port=(int(config.get('mysql', 'port'))
                               if config.has_option('mysql', 'port') else
                               3306),
                         user=config.get('mysql', 'user'),
                         passwd=config.get('mysql', 'password'),
                         db=config.get('mysql', 'database'))
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    all_tests = {}
    passes = {}
    fails = {}

    cursor.execute('select * from %s;' % config.get('mysql', 'table'))
    for row in cursor:
        daystamp = row['timestamp'].strftime('%Y%m%d')
        all_tests.setdefault(daystamp, 0)
        passes.setdefault(daystamp, 0)
        fails.setdefault(daystamp, 0)

        all_tests[daystamp] += 1
        if row['score'] == 1:
            passes[daystamp] += 1
        elif row['score'] == -1:
            fails[daystamp] += 1

    print 'Day,All,Pass,Fail'
            
    daystamp = sorted(all_tests.keys())[0]
    day = datetime.datetime(int(daystamp[0:4]),
                            int(daystamp[4:6]),
                            int(daystamp[6:8]))
    while daystamp in all_tests:
        print '%s,%s,%s,%s' %(daystamp, all_tests.get(daystamp, 0),
                              passes.get(daystamp, 0), fails.get(daystamp, 0))
        day += datetime.timedelta(days=1)
        daystamp = day.strftime('%Y%m%d')

if __name__ == '__main__':
    report()
