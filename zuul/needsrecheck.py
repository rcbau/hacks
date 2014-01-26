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
    subcursor = db.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('select * from %s where score=-1 and '
                   'datediff(date(now()), date(timestamp)) < 3;'
                   % config.get('mysql', 'table'))
    for row in cursor:
        subcursor.execute('select * from %s where score=1 and '
                          'number=%s and timestamp > "%s";'
                          % (config.get('mysql', 'table'),
                             row['number'], row['timestamp']))
        if subcursor.rowcount > 0:
            continue

        print '%s,%s' % (row['number'], row['patchset'])

if __name__ == '__main__':
    report()
