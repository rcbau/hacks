#!/usr/bin/python

import subprocess


def execute(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    p.wait()
    return (p.stdout.readlines(), p.returncode)

