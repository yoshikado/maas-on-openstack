#!/bin/bash
# ./deploy_maas.sh <numbers_of_nics> <release>
 
source setvars
# Create required networks in OpenStack
/bin/bash create_nw.sh $1
# Create instance
if [ $2 = "trusty" ]; then
  /bin/bash create_cloudconfig_trusty.sh
else
  /bin/bash create_cloudconfig_xenial.sh
fi
/bin/bash create_instance.sh $maas_instance $1 $2
# Configure initial settings
ip=`nova show $maas_instance | grep "$base_nw_name" | awk '{print $5}'`
if [ $2 = "trusty" ]; then
  scp -i maas-key $openstack_cred maas-key* enlist_node.sh setvars nova_driver/* $ip:
  ssh -i maas-key $ip 'bash -s' < configure_maas_v1x.sh
else
  scp -i maas-key $openstack_cred maas-key* enlist_node.sh setvars maasdebconf $ip:
  ssh -i maas-key $ip 'bash -s' < configure_maas_v2x.sh
fi

echo "Deploy finished"

