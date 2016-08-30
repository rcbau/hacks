OpenStack-Ansible-Deployment hacks
==================================

The paths in `ansible.cfg` assume that `openstack-ansible-deployment` is
checked out alongside this repo.

Push my quick source change/fix/debug-print
-------------------------------------------

Push the code in `$MYSRC/nova`.  This playbook will build a wheel,
copy it to the relevant servers, and restart affected daemons.

```shell
cd playbooks
sudo openstack-ansible push-project.yml -e "project=nova source_path=$MYSRC/nova"
```

A reasonable way to fit this into a workflow might be to rsync your
source tree to the cloud server where you run OSAD, and then run the
above command.  I'll leave that 2-line shell script as an exercise for
the reader.

**Note:** `push-project.yml` doesn't update the repo server with your
new wheel.  This means a regular osad playbook run will most likely
overwrite your custom wheel and replace it with the usual one built
from upstream git.  This is considered a feature.
