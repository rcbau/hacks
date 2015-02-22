#!/opt/local/bin/bash

set -x
## BEGIN config vars
_base='projects/openstack'
_net_type='nova'
## END   config vars

## BEGIN calculated vars
# FIXME: update the neutron config to have the "markers"
_conf_src="${_base}/openstack-dev/tony-scripts/local.conf-${_net_type}"
_conf_dst="${_base}/openstack-dev/devstack/local.conf"
## END   calculated vars

# set -x
# set -e
# set -ex

declare -A host_home_mapping=(
    ["thor"]='/home/tony'
    ["devstack"]='/home/stack'
    ["devstack01"]='/home/stack'
    ["devstack02"]='/home/stack'
    ["devstack-vm"]='/home/stack'
    ["migrate01"]='/home/stack'
    ["migrate02"]='/home/stack'
)

while [ $# -gt 0 ] ; do
    case "$1" in
    -h|--host)  _host=$2;
                _home=${host_home_mapping[$_host]}
                shift 1
    ;;
    --)
                shift 1
                __args+=" $@"
                break
    ;;
    *)          __args+=" $1"
    esac
    shift 1;
done

# reset  Args after local filtering
set -- $__args

if [ -z "$_host" ] ; then
    _host='thor'
    _home=${host_home_mapping[$_host]}
fi
if [ -z "$_home" ] ; then
    echo "$_host Unknown, please update host_home_mapping[]" >&2
    exit 1
fi

if [ -z "$1" ] ; then
    echo Copying the whole lot to ${_host}:${_base}/.
    cd ~/${_base}
    rsync -a --partial . ${_host}:${_base}/.
else
    for prj in "${@}" ; do
        prj_name=

        if [ $prj == '.' ] ; then
            prj=$(pwd)
            prj="${prj/$HOME\//}"
            prj="${prj/$_base\//}"
        fi

        case "$prj" in
        openstack/nova)     prj_name="NOVA" ;;
        openstack/cinder)   prj_name="CINDER" ;;
        esac

        # FIXME: This needs to be done outside the for loop and remove
        #        all ^.*_REPO= lines.
        #        othereise you end up with stale lines building up over time.
        echo "Removing config for $prj"
        sed -e "/^${prj_name}_REPO=/d" -e "/^${prj_name}_BRANCH=/d"            \
            -i~ ~/$_conf_src

        cd ~/${_base}/${prj}
        branch=$(git rev-parse --symbolic --abbrev-ref HEAD)

        if [ "$branch" != "master" ] ; then
            # Some nice information
            git show -s --format="%h %d| %s" HEAD

            if [ -n "$prj_name" ] ; then
                echo "Tweaking devstack setup for $prj (${prj_name})"
                # OMG this is ugly but it works
                sed -e "/#.*REPO_CONFIG/a \\
${prj_name}_REPO=file://$_home/$_base/$prj" -e "/#.*BRANCH_CONFIG/a \\
${prj_name}_BRANCH=refs/heads/$branch" \
                    -i~ ~/$_conf_src
            fi
        fi

        # It's possible that the dir doesn't exist at the other end
        ssh ${_host} "mkdir -p \"${_base}/${prj}/.\""
        echo Copying $prj to ${_host}:${_base}/${prj}
        rsync -a --partial . ${_host}:${_base}/${prj}/.
        echo ''
    done
fi

echo Copying ~/$_conf_src '->' ${_host}:${_conf_dst}
rsync -a --partial ~/$_conf_src ${_host}:${_conf_dst}

# restack
# Run tox in /opt/stack/$project
# Run exercise.sh in $devstack
