#!/usr/bin/python

# Wiki helpers

import json

from simplemediawiki import MediaWiki


class Wiki(object):
    def __init__(self, url, username, password):
        self.wiki = MediaWiki(url)
        self.username = username
        self.password = password

        self.login = self._make_wiki_login_call({'action': 'login'})
        self.token = self._make_wiki_login_call(
            {'action': 'login', 'lgtoken': self.login['login']['token']})

    def _make_wiki_login_call(self, packet):
        packet.update({'lgname': self.username,
                       'lgpassword': self.password})
        return self.wiki.call(packet)

    def get_page(self, title):
        response = self.wiki.call({'action': 'query',
                                   'titles': title,
                                   'prop': 'revisions',
                                   'rvprop': 'content'})
        pages = response['query']['pages']
        page_id = pages.keys()[0]
        return pages[page_id]['revisions'][0]['*']

    def post_page(self, title, text):
        page_token = self.wiki.call({'action': 'query',
                                     'prop': 'info',
                                     'titles': title,
                                     'intoken': 'edit'})
        pages = page_token['query']['pages']
        page_id = pages.keys()[0]

        response = self.wiki.call({'action': 'edit',
                                   'minor': True,
                                   'bot': True,
                                   'title': title,
                                   'text': json.dumps(text).replace(
                                       '\\n', '\n')[1:-1],
                                   'token': pages[page_id]['edittoken']})
        if not 'nochange' in response['edit']:
            print 'Modified %s' % title
