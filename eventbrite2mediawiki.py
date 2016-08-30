#!/usr/bin/python

# Convert eventbrite registrations into mediawiki user accounts
# Args:
#    1: event name

# We read a config file at ~/.eventbrite2mediawiki_%(eventname)s, which looks
# something like this:
#
#mikal@dell:~/src/rcbau/hacks$ cat ~/.eventbrite2mediawiki_technical_topics 
#{
#    "eventbrite": {
#        "event_id": "27377136753", 
#        "token": "...token..."
#    }, 
#    "mediawiki": {
#        "password": "...password...", 
#        "url": "https://wiki.madebymikal.com/api.php", 
#        "username": "...sysop_username..."
#    },
#    "email": {
#        "subject": "Your Technical Topics wiki account",
#        "from": "mikal@stillhq.com",
#        "body": "Thanks for registering for Technical Topics. As part of that\nregistration I've created a wiki account for you. That account\ncan be used to edit the event wiki page as much as you'd like.\nThe hope is that requiring people to be registered for the\nevent before being able to edit the wiki will mean that we\nhave less spam problems.\n\nYour account details are:\n    Username: %(username)s\n    Password: %(password)s\n\nThe wiki is at https://wiki.madebymikal.com/index.php?title=Technical_Topics:December_2016\n\nEnjoy!\n\nMichael"
#    }
#}


import json
import mimetypes
import os
import random
import requests
import smtplib
import string
import sys

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import wiki

with open(os.path.expanduser('~/.eventbrite2mediawiki_%s' % sys.argv[1]),
          'r') as f:
    conf = json.loads(f.read())

base_url = ('https://www.eventbriteapi.com/v3/events/%s'
            % conf['eventbrite']['event_id'])
password_chars = string.ascii_letters + string.digits + '!@#$%^&*()'

random.seed(os.urandom(1024))

w = wiki.Wiki(conf['mediawiki']['url'],
              conf['mediawiki']['username'],
              conf['mediawiki']['password'])


def send_email(email, username, password):
    body = conf['email']['body'] % {'username': username,
                                    'password': password}

    print '-' * 40
    print body
    print '-' * 40
    
    msg = MIMEMultipart()
    msg['Subject'] = conf['email']['subject']
    msg['From'] = conf['email']['from']
    msg['To'] = email
    msg.preamble = body

    txt = MIMEText(body, 'plain')
    msg.attach(txt)

    s = smtplib.SMTP('192.168.1.14')
    s.sendmail(conf['email']['from'], [email], msg.as_string())
    s.quit()


def process_attendee(profile):
    # Generate a random password
    password = ''.join(random.choice(password_chars) for i in range(13))

    print '%s %s -> %s %s' %(profile['first_name'], profile['last_name'],
                             profile['email'], password)
    username = '%s%s' %(profile['first_name'], profile['last_name'])
    success = w.create_account(
        username,
        password,
        profile['email'],
        '%s %s' %(profile['first_name'], profile['last_name']))
    if success:
        send_email(profile['email'], username, password)
    else:
        print 'Account creation failed'


if __name__ == '__main__':
    response = requests.get(
        '%s/attendees/' % base_url,
        headers = {'Authorization': ('Bearer %s'
                                     % conf['eventbrite']['token'])},
        verify = True,
        )

    for attendee in response.json()['attendees']:
        process_attendee(attendee['profile'])
