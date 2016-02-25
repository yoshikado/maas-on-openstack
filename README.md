# maas-on-openstack
Deploy MAAS on OpenStack

run from the bastion

$ ./deploy_maas_env.sh

after MAAS is deployed add nodes to MAAS with

ex.) add a node with the hostname 'node1' with the tag 'bootstrap' in m1.small flavor.

$ ssh -i maas-key maas-server 'bash -s' < enlist_node.sh node1 m1.small bootstrap
