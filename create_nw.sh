#!/bin/bash

CreateNetwork() {
  for i in `seq 1 $1`
  do
    maas_nw_allocation_start="10.12.${i}.2"
    maas_nw_allocation_end="10.12.${i}.254"
    maas_nw_cidr="10.12.${i}.0/24"
    neutron net-show $maas_nw_name$i
    if [ $? -eq 1 ]; then
      neutron net-create $maas_nw_name$i
    fi
    neutron subnet-show $maas_subnw_name$i
    if [ $? -eq 1 ]; then
      neutron subnet-create $maas_nw_name$i \
        --name $maas_subnw_name$i \
        --allocation-pool start=${maas_nw_allocation_start},end=${maas_nw_allocation_end} \
        --disable-dhcp \
        $maas_nw_cidr
    fi
    neutron router-show $maas_rt_name$i
    if [ $? -eq 1 ]; then
      neutron router-create $maas_rt_name$i
      neutron router-interface-add $maas_rt_name$i $maas_subnw_name$i
      neutron router-gateway-set $maas_rt_name$i $ext_net_id
    fi
  done
}
source setvars
CreateNetwork $1
