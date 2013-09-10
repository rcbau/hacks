#!/usr/bin/python

# Push edits back to the mediawiki if it is safe to do so

import json
import os
import re
import shutil
import tempfile

import diff
import utils
import wiki


DIFF_FILE_RE = re.compile('\-\-\- (.*)')


with open(os.path.expanduser('~/.mediawiki'), 'r') as f:
    conf = json.loads(f.read())[os.environ['USER']]


def push():
    print 'Pushing as %s' % conf['username']
    w = wiki.Wiki(conf['url'], conf['username'], conf['password'])

    for (new_file, d) in diff.diff():
        m = DIFF_FILE_RE.match(d[0])
        if not m:
            print 'Failed to parse diff for %s' % d[0]
            continue

        tempdir = tempfile.mkdtemp()
        title = m.group(1)

        new_file_msg = ''
        if new_file:
            new_file_msg = ', page is new'

        print
        print 'Editted file: %s (resolving in %s%s)' %(title, tempdir, new_file_msg)

        try:
            with open(os.path.join(tempdir, title), 'w') as f:
                if not new_file:
                    f.write(w.get_page(title).encode('ascii', 'replace'))
            with open(os.path.join(tempdir, '.patch'), 'w') as f:
                f.write(''.join(d))
            cmd = 'cd %s; patch < .patch' % tempdir
            (out, exit) = utils.execute(cmd)
            if exit != 0:
                print '    %s' % '    '.join(out)
                continue

            with open(os.path.join(tempdir, title), 'r') as f:
                data = f.read()
            w.post_page(title, data, minor=False, bot=False)

        finally:
            pass
        shutil.rmtree(tempdir)


if __name__ == '__main__':
    push()
