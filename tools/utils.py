#!/usr/bin/python

import subprocess


def runcmd(cmd):
    obj = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = obj.communicate()
    returncode = obj.returncode
    return stdout
