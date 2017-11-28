kube-vcloud-flexvolume
======================

VMware vCloud Director [flexVolume](https://kubernetes.io/docs/concepts/storage/volumes/#out-of-tree-volume-plugins)
driver for Kubernetes.


Status
======

Highly experimental and under heavy development. Do not use on a system that you care about the data.
The current works-for-me version is: [1.1.0a2](../../releases/tag/1.1.0a2).

Description
============

vcloud-flexvolume provides a storage driver using vCloud's Independent Disk feature. The Independent Disk provides
persistent disk storage which can be attached to instances running in vCloud Director environment.


Installation
============

*  Make sure kubelet is running with `--enable-controller-attach-detach=false`
*  Create the directory `/usr/libexec/kubernetes/kubelet-plugins/volume/exec/sysoperator.pl~vcloud`
*  Install wrapper `scripts/vcloud` as `/usr/libexec/kubernetes/kubelet-plugins/volume/exec/sysoperator.pl~vcloud/vcloud`
*  Create the directory `/opt/vcloud-flexvolume/etc`
*  Install configuration file `config/config.yaml.example` as `/opt/vcloud-flexvolume/etc/config.yaml` and set parameters.

Install packages:

*  python
*  python-pip
*  python-pip-whl
*  python-setuptools
*  python-flufl.enum
*  python-lxml
*  python-netaddr
*  python-progressbar
*  python-pyudev
*  python-pyvmomi
*  python-wheel

Install the driver itself:

```
python setup.py build
sudo python setup.py install
```

or

```
pip install git+https://github.com/sysoperator/kube-vcloud-flexvolume.git
```

Create a Kubernetes Pod such as:

```
cat examples/nginx.yaml | kubectl apply -f -
```

The driver will create an independent disk with name "testdisk" and size 1Gi under storage profile "T1".
The volume will also be mounted as /data inside the container.


Options
=======

Following options are required:

*  volumeName - Name of the independent disk volume.
*  size - Size to allocate for the new independent disk volume. Accepts any value in human-readable format. (e.g. 100Mi, 1Gi)
*  storage - Name of the storage pool.

Optional options may be passed:

*  mountoptions - Additional options passed to mount. (e.g. noatime, relatime, nobarrier)


Driver invocation
=================

*  Init:

```
>>> vcloud-flexvolume init
<<< {"status": "Success", "capabilities": {"attach": true}}
```

*  Volume is attached:

```
>>> vcloud-flexvolume isattached '{"kubernetes.io/fsType":"ext4","kubernetes.io/pvOrVolumeName":"testdisk","kubernetes.io/readwrite":"rw","mountoptions":"relatime,nobarrier","size":"1Gi","storage":"T1","volumeName":"testdisk"}' nodename
<<< {"status": "Success", "attached": false}
```

*  Attach:

```
>>> vcloud-flexvolume attach '{"kubernetes.io/fsType":"ext4","kubernetes.io/pvOrVolumeName":"testdisk","kubernetes.io/readwrite":"rw","mountoptions":"relatime,nobarrier","size":"1Gi","storage":"T1","volumeName":"testdisk"}' nodename
<<< {"status": "Success", "device": "/dev/sdb1"}
```

The driver detects (using udev events) the name of the device under which it was registered by the Linux kernel and automatically creates symlink `/dev/block/<URN>` pointing to `/dev/<device>`.
URN is a unique volume ID generated by vCloud Director.

*  Wait for attach:

```
>>> vcloud-flexvolume waitforattach /dev/sdb1 '{"kubernetes.io/fsType":"ext4","kubernetes.io/pvOrVolumeName":"testdisk","kubernetes.io/readwrite":"rw","mountoptions":"relatime,nobarrier","size":"1Gi","storage":"T1","volumeName":"testdisk"}'
<<< {"status": "Success", "device": "/dev/sdb1"}
```

*  Mount device:

```
>>> vcloud-flexvolume mountdevice /mnt/testdisk /dev/sdb1 '{"kubernetes.io/fsType":"ext4","kubernetes.io/pvOrVolumeName":"testdisk","kubernetes.io/readwrite":"rw","mountoptions":"relatime,nobarrier","size":"1Gi","storage":"T1","volumeName":"testdisk"}'
<<< {"status": "Success"}
```

*  Unmount device:

```
>>> vcloud-flexvolume unmountdevice /mnt/testdisk
<<< {"status": "Success"}
```

*  Detach:

```
>>> vcloud-flexvolume detach testdisk nodename
<<< {"status": "Success"}
```


TODO
====

*  Write some tests.
*  ~~Functions in flexvolume/mount.py should raise Exceptions just like the ones in attach.py.~~
*  Reuse vCloud API session token between invocations.
