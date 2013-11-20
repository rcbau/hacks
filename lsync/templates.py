#!/usr/bin/python

settings = """settings = {
   logfile    = "/var/log/lsyncd/lsyncd.log",
   statusFile = "/var/log/lsyncd/lsyncd-status.log",
   statusInterval = 5,
   pidfile = "/var/run/lsyncd.pid"
}

"""

sync = """sync{
        default.rsync,
        source="%(source)s",
        target="%(target)s",
        rsyncOps={"%(flags)s", "-e", "/usr/bin/ssh -i /root/.ssh/id_rsa.lsyncd -o StrictHostKeyChecking=no"}
}
"""
