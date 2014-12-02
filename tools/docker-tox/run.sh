#!/bin/sh

set -e -x

dockdir=$(mktemp -d)

tox --sdistonly
mv .tox/dist/*.zip $dockdir/sdist.zip

cp --preserve=timestamps tox.ini *requirements.txt setup.py $dockdir/

cat <<EOF >$dockdir/Dockerfile
FROM anguslees/openstack-tox
EOF

sudo docker build "$@" $dockdir

cd /
rm -r $dockdir
