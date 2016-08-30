FROM python
MAINTAINER Angus Lees <gus@inodes.org>

RUN adduser --disabled-login --home /user \
 --gecos 'Generic unprivileged user' user

RUN install -d -m 01777 /pipcache
ENV PIP_DOWNLOAD_CACHE /pipcache

RUN pip install tox

# Install some common OpenStack system dependencies
RUN apt-get -q update && apt-get -qy install \
 git-core \
 graphviz \
 libffi-dev \
 libmysqlclient-dev \
 libpq-dev \
 libsqlite3-dev \
 libssl-dev \
 libvirt-dev \
 libxml2-dev \
 libxslt-dev \
 pkg-config \
 python-dev \
 python-pip

ENV HOME /user
WORKDIR /app
RUN chown user:user /app
USER user

ONBUILD COPY tox.ini setup.py *requirements.txt /app/

# The idea here is that the above files change rarely, and we'd like
# docker to setup+cache+reuse the venv as much as possible.
ONBUILD RUN tox --notest -c /app/tox.ini --installpkg /dev/null

ONBUILD COPY sdist.zip /tmp/

# Unpack sdist.zip into /app.  Some mucking around to deal with the
# unknown directory prefix that tox --sdistonly generates.
ONBUILD RUN \
 unzip -q /tmp/sdist.zip -d /tmp/exdir && \
 find /tmp/exdir -mindepth 2 -maxdepth 2 -print0 | xargs -0 mv -t /app && \
 rmdir /tmp/exdir/* /tmp/exdir

CMD ["tox", "--develop"]
