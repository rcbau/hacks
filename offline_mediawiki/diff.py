#!/usr/bin/python

# Diff the locally editted wiki version against what we downloaded

import os
import tempfile

import utils


def diff():
    _, empty = tempfile.mkstemp()
    try:
        file_is_new = False

        existing = []
        for ent in os.listdir('.mediawiki'):
            if os.path.isfile(ent):
                existing.append(ent)

        for ent in os.listdir('.'):
            if os.path.isdir(ent):
                continue
            if ent.endswith('~'):
                continue

            orig = '.mediawiki/"%s"' % ent
            if not ent in existing:
                file_is_new = True
                orig = empty

            cmd = 'diff -u --label="%s" %s "%s"' %(ent, orig, ent)
            (d, exit) = utils.execute(cmd)
            if d:
                yield (file_is_new, d)

    finally:
        os.unlink(empty)


if __name__ == '__main__':
    for d in diff():
        print ''.join(d[1])
