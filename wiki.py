#!/usr/bin/python

# Wiki helpers

import json

from simplemediawiki import MediaWiki


DEBUG = False


def assert_present(value, d):
    if not value in d:
        print 'Error, %s not present in response' % value
        print d
        raise Exception('Invalid response')


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
        response = self.wiki.call(packet)
        if DEBUG:
            print response
        return response

    def all_pages(self):
        response = self.wiki.call({'action': 'query',
                                   'list': 'allpages'})
        if DEBUG:
            print response
        assert_present('query', response)

        marker = 'foo'
        while marker:
            if 'query-continue' in response:
                marker = response['query-continue']['allpages']['apfrom']
            else:
                marker = None

            for page in response['query']['allpages']:
                yield page['title']
            response = self.wiki.call({'action': 'query',
                                       'list': 'allpages',
                                       'apfrom': marker})
            if DEBUG:
                print response

    def get_page(self, title):
        response = self.wiki.call({'action': 'query',
                                   'titles': title,
                                   'prop': 'revisions',
                                   'rvprop': 'content'})
        if DEBUG:
            print response
        assert_present('query', response)

        pages = response['query']['pages']
        page_id = pages.keys()[0]

        if not 'revisions' in pages[page_id]:
            # This is a new page
            return ''

        return pages[page_id]['revisions'][0]['*']

    def post_page(self, title, text, minor=True, bot=True):
        response = self.wiki.call({'action': 'query',
                                   'prop': 'info',
                                   'titles': title,
                                   'intoken': 'edit'})
        if DEBUG:
            print response
        assert_present('query', response)

        pages = response['query']['pages']
        page_id = pages.keys()[0]

        response = self.wiki.call({'action': 'edit',
                                   'minor': minor,
                                   'bot': bot,
                                   'title': title,
                                   'text': json.dumps(text).replace(
                                       '\\n', '\n')[1:-1],
                                   'token': pages[page_id]['edittoken']})
        if DEBUG:
            print response
        if not 'nochange' in response['edit']:
            print 'Modified %s' % title
