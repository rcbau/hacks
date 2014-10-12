#!/usr/bin/python

import json


data = {}

data[('Allow deletion of hypervisor nodes via nova-manage', 'Administrative')] = ['94536']
data[('Add a new nova service which pre-caches images on hypervisor nodes', 'Administrative')] = ['85768']
data[('Add support for monitoring the number of free IPs in a given fixed-ip block', 'Administrative')] = ['94299']
data[('Tweak the output of "nova hypervisor-state" to show the number of free vcpus after the cpu_allocation_ratio is taken into account', 'Administrative')] = ['98058']
data[('Implement support for nested quotas', 'Administrative')] = ['110639']
data[('Add additional database indexes to help address slow SQL queries', 'Administrative')] = ['97520']
data[('Allow ephemeral instance storage to be served by cinder', 'Administrative')] = ['91321']
data[('A scheme to support online SQL schema changes', 'Administrative')] = ['102545']
data[('Allow volumes to be force detached from instances', 'Administrative')] = ['84048']
data[('Refactor the iSCSI driver to support other iSCSI transports besides TCP', 'Administrative')] = ['86637']
data[('More clearly mark auto disabled hypervisors in the SQL database', 'Administrative')] = ['88515']
data[('Consume cinder event notifications', 'Administrative')] = ['87546']
data[('Continue moving cold migrations to conductor', 'Administrative')] = ['86907']
data[('Enable the nova metadata cache to be a shared resource to improve the hit rate', 'Administrative')] = ['121646']
data[('Make TCP keepalive tunable', 'Administrative')] = ['87427']
data[('Allow TLS for connections to spice and vnc consoles', 'Administrative')] = ['101026']

data[('Morphing the v3 API proposal into a v2.1 API', 'API')] = ['84695']
data[('Supporting micro-versions in the v2.1 API', 'API')] = ['96139','101648','104418']
data[('A proposal for how to support neutron in the v3 API', 'API')] = ['92926']
data[('Include extra-specs information in the output of flavor show and list calls', 'API')] = ['95408']
data[('Pass through creation hints to cinder when auto-creating volumes on instance boot', 'API')] = ['106330']
data[('Add support for tagging to the EC2 API', 'API')] = ['90276']
data[('Expose hypervisor metrics via an API', 'API')] = ['91998']

data[('Make fetching images from glance pluggable so that its easier to write alternate implementations', 'Image features')] = ['86583']
data[('Convert to using the glance v2 API', 'Image feature')] = ['84887']
data[('Pre-fetch specific images to hypervisor nodes to speed up boot times', 'Image feature')] = ['85792']

data[('Allow users of Nova such as Trove "hide" instances running as a certain user from the user', 'Instance features')] = ['90678']
data[('Support deletion of volumes when an instance terminates', 'Instance features')] = ['89777']
data[('Implement VMThunder support for booting many identical instances using boot-from-volume', 'Instance features')] = ['94060']
data[('Enable changing the owner of an instance. There were two proposed implementations', 'Instance features')] = ['85811','105367']
data[('Support USB hot plug', 'Instance features')] = ['89842']
data[('Allow USB devices to be passed through to instances', 'Instance features')] = ['86118']
data[('Support specifying the USB controller for USB passthrough', 'Instance features')] = ['88337']
data[('Enable USB redirection over remote console connections', 'Instance features')] = ['89834']
data[('Configure the vCPU over-commitment for specific flavors', 'Instance features')] = ['87213']

data[('Refactor nova-network to be maintainable on freebsd', 'Networking')] = ['95328']
data[('Reconcile how DNS resolution works between Nova and Neutron', 'Networking')] = ['90150']
data[('Associate the least recently used fixed IP address', 'Networking')] = ['102688']

data[('Add an action type to the filter scheduler so it knows why a scheduling operation is occurring', 'Scheduler')] = ['97103']
data[('Use the scheduler to more strongly validate the destination hypervisor node for live migration of instances', 'Scheduler')] = ['89502']
data[('A proposed scheduler which doesn\'t use a SQL database', 'Scheduler')] = ['92128']
data[('Add additional monitors for utilisation based scheduling', 'Scheduler')] = ['89766']
data[('Add utilisation based weighers', 'Scheduler')] = ['90647']

data[('Strongly validate the tenant and user for quota consuming requests with keystone', 'Security')] = ['92507']

data[('Add FreeBSD as a supported hypervisor operating system', 'Hypervisor: FreeBSD')] = ['85119']

data[('Proposed re-integration of the docker driver', 'Hypervisor: Docker')] = ['103571']

data[('Support generation 2 virtual machines', 'Hypervisor: Hyper-V')] = ['103945']
data[('Add power off and reboot support', 'Hypervisor: Hyper-V')] = ['104630']
data[('Use RemoteFX to expose GPU features of instances', 'Hypervisor: Hyper-V')] = ['105041']
data[('Support the rescue instance operation', 'Hypervisor: Hyper-V')] = ['105042']
data[('Allow volumes to be stored on SMB shares instead of just iSCSI', 'Hypervisor: Hyper-V')] = ['102190']
data[('Allow the creation of highly available instances', 'Hypervisor: Hyper-V')] = ['105094']

data[('Add config drive support', 'Hypervisor: Ironic')] = ['98930']
data[('Support for selecting ironic nodes based on boot mode', 'Hypervisor: Ironic')] = ['108582']

data[('Make hugepages accessible to instances', 'Hypervisor: libvirt')] = ['96821']
data[('Allow flavours to specify which libvirt storage engine is used', 'Hypervisor: libvirt')] = ['91957']
data[('Enable Intel dpdkvhost support for attaching VIFs to instances', 'Hypervisor: libvirt')] = ['95805']
data[('Separate out the various supported virtualization types (kvm, lxc, etc) into separate classes', 'Hypervisor: libvirt')] = ['91460']
data[('Add support for SMBFS as a volume type', 'Hypervisor: libvirt')] = ['103203']
data[('Add support for StorPool volumes', 'Hypervisor: libvirt')] = ['115716']
data[('Add support for TPM pass-through to instances', 'Hypervisor: libvirt')] = ['85558']
data[('Use libvirt\'s sharing policy feature to control access to VNC consoles', 'Hypervisor: libvirt')] = ['86901']
data[('Allow instances to be pinned to specific hypervisor CPUs', 'Hypervisor: libvirt')] = ['92054']
data[('Make the virtio driver more configurable', 'Hypervisor: libvirt')] = ['103797']
data[('Allow instances to be booted via PXE instead of downloading an image from glance', 'Hypervisor: libvirt')] = ['118474']
data[('Enable vCPUs to be added to running instances', 'Hypervisor: libvirt')] = ['86273']
data[('Make the USB controller exposed to instances configurable', 'Hypervisor: libvirt')] = ['88334']

data[('Provide an alternative place to store vCenter usernames and passwords instead of nova.conf', 'VMWare specific features')] = ['85502', '85510']
data[('Add support for the Glance VMWare image store support', 'VMWare specific features')] = ['84281']
data[('Expose vCenter resource pools', 'VMWare specific features')] = ['84629']
data[('Refactor utility classes', 'VMWare specific features')] = ['84535']
data[('Allow Nova to access a VMWare image store over NFS', 'VMWare specific features')] = ['104211']
data[('Image cache improvements', 'VMWare specific features')] = ['84662']


new_data = {}
for title, topic in data:
    new_data.setdefault(topic, {})
    new_data[topic][title] = data[(title, topic)]


with open('juno.json', 'w') as f:
    f.write(json.dumps(new_data, indent=4, sort_keys=True))
