#!/usr/bin/python

# Copyright (c) Twisted Matrix Laboratories.
# Copyright (c) Michael Still 2013

# See LICENSE for details.


"""
A simple LCA2013 irc bot.

Run this script with two arguments, the channel name the bot should
connect to, and file to log to, e.g.:

  $ python lcabot.py

will log channel #test to the file 'test.log'.
"""


# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

import datetime
import gzip
import imp
import os
import re
import sys
import time
import yaml

import utils

class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class Lcabot(irc.IRCClient):
    """A logging IRC bot."""
    
    def __init__(self, factory):
        self.plugins = []
        self.verbs = {}

        self.last_heartbeat = time.time()
        self.current_topic = None
        self.seen_heartbeat = False
        self.last_input = time.time()

        self.factory = factory
        self.nickname = self.factory.conf['nickname']

        self.realtime_queue = []
        self.queue = []

        # Rate limiting implementation
        self.rate = 10.0           # messages
        self.per  = 5.0            # seconds
        self.last_check = time.time()
        self.allowance = self.rate

    def _writeLog(self, msg):
        try:
            self.logger.log(msg)
        except:
            pass
        log.msg(msg)

    def _enqueue(self, item, realtime):
        self._writeLog('Queued: %s' % repr(item))
        if not realtime:
            self.queue.append(item)
        else:
            self.realtime_queue.append(item)

    def _dequeue(self):
        if not self.seen_heartbeat:
            return

        current_time = time.time()
        time_passed = current_time - self.last_check
        self.last_check = current_time;

        self.allowance += time_passed * (self.rate / self.per)
        if self.allowance > self.rate:
            self.allowance = self.rate

        messages = int(self.allowance)
        self._writeLog('Dequeue %d messages of %d realtime and %d normal'
                       %(messages, len(self.realtime_queue), len(self.queue)))
        if messages > 0:
            outgoing = []
            realtime_outgoing = self.realtime_queue[:messages]
            if len(outgoing) < messages:
                outgoing = self.queue[:messages]

            self.allowance -= len(realtime_outgoing)
            self.allowance -= len(outgoing)

            for messages in [realtime_outgoing, outgoing]:
                for (method, channel, data) in messages:
                    self._writeLog('Dequeue %s %s %s' %(method, channel, data))
                    if method == 'msg':
                        self._send_msg(channel, data)
                    elif method == 'topic':
                        self._send_topic(channel, data)
                    elif method == 'describe':
                        self._send_describe(channel, data)

            self.queue = self.queue[len(outgoing):]        
            self.realtime_queue = self.realtime_queue[len(realtime_outgoing):]

    def _msg(self, channel, msg, realtime=False):
        self._enqueue(('msg', channel, msg), realtime)
        self._dequeue()

    def _send_msg(self, channel, msg):
        self._writeLog('%s >> <%s> %s' %(channel, self.nickname, msg))
        self.msg(channel, msg)

    def _topic(self, channel, topic, realtime=False):
        self._enqueue(('topic', channel, topic), realtime)
        self._dequeue()

    def _send_topic(self, channel, topic):
        self.topic(channel, topic)
        self._writeLog('%s >> Set topic to "%s"' %(channel, topic))
    
    def _describe(self, channel, action, realtime=False):
        self._enqueue(('describe', channel, action), realtime)
        self._dequeue()

    def _send_describe(self, channel, action):
        self.describe(channel, action)
        self._writeLog('%s >> /me %s' %(channel, action))

    def _loadPlugins(self):
        self._unloadPlugins()

        self._writeLog('[Loading plugins]')
        self.plugins = []
        self.verbs = {}

        plugin_directory = 'commands'
        re_plugin = re.compile('[^.].*\.py$')
        for plugin_file in os.listdir(plugin_directory):
            if re_plugin.match(plugin_file):
                name = plugin_file[:-3]
                self._writeLog('>> %s' % name)

                plugin_info = imp.find_module(name, [plugin_directory])
                plugin = imp.load_module(name, *plugin_info)

                for module in plugin.Init(self._writeLog,
                                          self.factory.conf):
                    try:
                        self.plugins.append(module)
                        yield module
                        for verb in module.Verbs():
                            self.verbs[verb] = module
                            self._writeLog('   implements verb %s' % verb)
                    except Exception, e:
                        self._writeLog('Exception from %s: %s' %(module, e))

    def _unloadPlugins(self):
        self._writeLog('[Unloading plugins]')
        for module in self.plugins:
            try:
                module.Cleanup()
            except Exception, e:
                self._writeLog('Exception from %s: %s' %(module, e))

    def _handleResponse(self, responses, realtime=False):
        for resp in responses:
            if resp:
                self._writeLog('Response: %s' %(repr(resp)))
                channel, kind, body = resp
                if channel is None:
                    channel = '#%s' % self.factory.conf['channels'][0]['name']

                if kind == 'msg':
                    self._msg(channel, utils.Normalize(body), realtime)
                elif kind == 'topic':
                    if body != self.current_topic:
                        self._topic(channel, body, realtime)
                    else:
                        self._writeLog('[Skipping topic update, no change]')
                else:
                    self._writeLog('Unknown response type')

    def _doHeartbeat(self):
        """Heartbeat our modules."""

        self.seen_heartbeat = True
        self.last_heartbeat = time.time()
        for module in self.plugins:
            try:
                self._writeLog('[Heartbeat sent to %s]' % module.Name())
                self._handleResponse(list(module.HeartBeat()), realtime=False)
            except Exception, e:
                self._writeLog('Exception from %s: %s' %(module, e))

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self._writeLog("[connected at %s]" % 
                       time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self._writeLog("[disconnected at %s]" % 
                       time.asctime(time.localtime(time.time())))
        self.logger.close()

    ###########
    # callbacks for events
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self._writeLog("[I have signed on]")
        if self.factory.conf.get('password', None):
            self._msg('nickserv',
                      'identify %s %s' %(self.nickname,
                                         self.factory.conf['password']),
                      realtime=True)

        for channel in self.factory.conf['channels']:
            self.join(channel['name'], channel['password'])

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self._writeLog('[I have joined %s]' % channel)
        for module in self._loadPlugins():
            self._writeLog('[Loaded %s]' % module.Name())
        self._writeLog('[Setup complete]')

        # Do some opping
        self._msg('chanserv', 'op %s %s' %(channel, self.nickname),
                  realtime=True)
        for op in self.factory.conf['operators']:
            self._msg('chanserv', 'op %s %s' %(channel, op),
                      realtime=True)

    def topicUpdated(self, user, channel, topic):
        """Called when the topic changes or we join a channel."""
        self._writeLog('%s >> topic set by %s is "%s"'
                       %(channel, user, topic))
        self.current_topic = topic

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""

        user = user.split('!', 1)[0]
        self._writeLog('channel: %s, user: %s, msg: %s' % (channel, user, msg))

        # We don't reply to ourselves
        if user == self.nickname:
            return

        # If this is a privmsg, then we need to handle channels. Ignore in
        # channel messages which aren't addressed to us
        outchannel = channel
        if channel == self.nickname:
            outchannel = user
        elif not msg.startswith(self.nickname + ':'):
            return
        
        # Determine the command
        command = msg.rstrip()
        if msg.startswith(self.nickname + ':'):
            command = ':'.join(command.split(':')[1:]).lstrip()
        elems = command.split(' ')
        self._writeLog('* %s *' % repr(elems))

        # Execute commands
        if elems[0] == 'reload':
            if user in self.factory.conf.get('operators', []):
                for module in self._loadPlugins():
                    self._msg(outchannel,
                              '%s: Loaded %s' %(user, module.Name()),
                              realtime=True)
            else:
                self._msg(outchannel, 'Damn kids today', realtime=True)

        elif elems[0] == 'heartbeat':
            if user in self.factory.conf.get('operators', []):
                self._doHeartbeat()
            else:
                self._msg(outchannel, 
                          'I\'m sorry sonny, I can\'t quite hear you',
                          realtime=True)

        elif elems[0] in self.verbs:
            module = self.verbs[elems[0]]
            try:
                args = command[len(elems[0]):].lstrip()
                self._writeLog('[Command sent to %s]' % module.Name())
                self._handleResponse(list(module.Command(outchannel,
                                                         elems[0],
                                                         args)))
            except Exception, e:
                self._writeLog('Exception: %s' % e)
                self._msg(outchannel, 'Error while handling command',
                          realtime=True)

        else:
            if channel == self.nickname:
                if elems[0] == 'help' and len(elems) > 1:
                    module = self.verbs.get(elems[1])
                    if module:
                        self._msg(user, module.Help(elems[1]),
                                  realtime=True)
                    else:
                        self._msg(user, 'That command is not registered',
                                  realtime=True)

                else:
                    sorted_verbs = self.verbs.keys()
                    sorted_verbs.sort()
                    self._msg(user, ('I understand the following commands: %s'
                                     % ', '.join(sorted_verbs)),
                              realtime=True)
            else:
                self._describe(outchannel, 'is confused', realtime=True)
                self._msg(outchannel, ('%s: I am a very simple irc bot. PM me '
                                       'for help.' % user),
                          realtime=True)

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""

        user = user.split('!', 1)[0]
        self._writeLog('%s >> * %s %s' % (channel, user, msg))

    def userJoined(self, user, channel):
        """This is called when a user joins a channel."""

        for module in self.plugins:
            try:
                self._writeLog('[Join event for %s on %s sent to %s]'
                               %(user, channel, module.Name()))
                self._handleResponse(list(module.NoticeUser(channel, user)))
            except Exception, e:
                self._writeLog('Exception from %s: %s' %(module, e))

    # irc callbacks
    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self._writeLog("%s is now known as %s" % (old_nick, new_nick))


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'

    # Scary inner goo
    def dataReceived(self, data):
        """Log all incoming data."""

        self.last_input = time.time()
        if self.factory.conf['verbose']:
            for l in data.replace('\r', '').split('\n'):
                self._writeLog('IN: %s' % l)
        irc.IRCClient.dataReceived(self, data)
        self._dequeue()

        if data.find(' PONG ') != -1:
            self._writeLog('Considering heartbeat')
            if time.time() - self.last_heartbeat > 60:
                self._doHeartbeat()

    def sendLine(self, line):
        """Log all outgoing data."""

        if self.factory.conf['verbose']:
            for l in line.replace('\r', '').split('\n'):
                self._writeLog('OUT: %s' % l)

        if self.last_input - time.time() > 300:
            self._writeLog('No input for more than five minutes. Aborting')
            sys.exit(1)

        irc.IRCClient.sendLine(self, line)


class LcaBotFactory(protocol.ClientFactory):
    """A factory for LcaBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, conf, filename):
        self.conf = conf
        self.filename = filename

    def buildProtocol(self, addr):
        p = Lcabot(self)
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # Initialize logging
    log.startLogging(sys.stdout)

    # Load config
    conf_file = open('bot.yaml')
    conf = yaml.load(conf_file.read())
    conf_file.close()
    print conf

    # Create factory protocol and application
    logfile = datetime.datetime.now().strftime('%Y%m%d-%H%M%S.log')
    f = LcaBotFactory(conf, logfile)

    # Connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # Run bot
    reactor.run()
