#!/usr/bin/python

# $1 is the name of the command, with no .py

import imp
import sys
import yaml

def log(message):
    print message


conf_file = open('bot.yaml')
conf = yaml.load(conf_file.read())
conf_file.close()

plugin_info = imp.find_module(sys.argv[1], ['commands'])
plugin = imp.load_module(sys.argv[1], *plugin_info)
module = list(plugin.Init(log, conf))[0]

for result in list(module.HeartBeat()):
    print 'Result: %s' % repr(result)

module.Cleanup()
