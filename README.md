Deploy MAAS on OpenStack
========================

How to deploy MAAS on OpenStack
-------------------------------
### Create an pxe-bootable image
First, in order to enable instances to pxeboot, you will need to create an image based on [ipxe](http://ipxe.org/start).
You can do this by,
```
$ bash create_pxe_image.sh create
```
You can upload the created image to glance by,
```
$ bash create_pxe_image.sh upload
```

### Deploy
With the following script it will,

1. create necessary networks
2. create an instance for MAAS
3. install MAAS
4. configure MAAS
```
$ bash deploy_maas.sh <number_of_nics> <release>
```
For example,
```
$ bash deploy_maas.sh 2 trusty
```

### Enlist nodes
You can enlist nodes, just by creating instances booting from pxe-boot image,
or you can create and enlist an node with the following script.
```
$ ssh -i maas-key maas-server 'bash -s' < enlist_node.sh node1 m1.small bootstrap
```

With this it will create an instance with the hostname 'node1' with the tag 'bootstrap' in m1.small flavor.
