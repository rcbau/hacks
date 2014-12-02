tox-in-docker
=============

Warning: Still at the proof-of-concept stage.

1. Build the base system, and cache it locally:

 ```
 docker build -t openstack-tox openstack-tox/
 ```

 The only thing OpenStack-specific about this is the set of `*-dev`
 packages that are pre-installed into the base image.

2. Build a new docker image with the source from your particular project:

 ```
 project=neutron  # or whatever
 cd ~/src/openstack/$project  # or wherever
 /path/to/docker-tox/run.sh -t $project-tox
 ```

 This will build a new docker image containing the python project from
 local directory, with tox environments all set up and ready to go.
 The intention is that this step caches and reuses intermediate images
 when the files used to create the tox environments haven't changed.

 You will need to repeat this step whenever you have a new source tree
 you want to test, so hack up `run.sh` to make it do exactly what you
 want.

3. Run isolated/repeatable tests via the new tox container

 Some examples:

 ```
 docker run --rm $project-tox tox --develop -epep8
 docker run --rm $project-tox .tox/py27/bin/testr list-tests
 docker run --rm -ti $project-tox .tox/py27/bin/python
 ```
