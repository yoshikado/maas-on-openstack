#!/bin/bash

#set -e
set -u

DeleteInstances(){
  nova delete $maas_instance
  ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R $maas_instance
  nova keypair-delete maas-keypair
  rm maas-key
  rm maas-key.pub
}

DeleteNetwork() {
  neutron router-interface-delete $maas_rt_name $maas_subnw_name
  neutron router-gateway-clear $maas_rt_name
  neutron router-delete $maas_rt_name
  sleep 2
  neutron net-delete $maas_nw_name
}

DeleteImage(){
  glance image-delete $glance_img_name
}

### main ###
source setvars
DeleteInstances
DeleteNetwork
DeleteImage
