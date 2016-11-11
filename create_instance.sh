#!/bin/bash
# ./create_instance.sh <instance_name> <numbers_of_nics> <release>
# ex) ./create_instance.sh maas-server 2 xenial

# Networks that is going to be attached to the instance
nicarg="--nic net-id=$base_net_id "                                          
for i in `seq 1 $2`                                                           
do                                                                            
  maas_net_id=`neutron net-list | grep $maas_nw_name$i | awk '{print $2}'`    
  nicarg="${nicarg}--nic net-id=$maas_net_id "                                
done                                                                          

# Create key-pair
if [ ! -f maas-key ]; then
  ssh-keygen -b 4096 -t rsa -f maas-key -q -N ""
  nova keypair-add --pub-key maas-key.pub maas-keypair
fi

# Boot instance
if [ $3 = "trusty" ]; then
  boot_img=$boot_img_trusty
else
  boot_img=$boot_img_xenial
fi
nova show $1
if [ $? -eq 1 ]; then
  nova boot --flavor $flavor --image $boot_img --key-name maas-keypair ${nicarg} --poll --user-data cloudconfig.yaml $1
else
  echo "ERROR: instance $1 does already exist."
  exit -1
fi

# Wait for cloud-init to finish
echo "Waiting for the instance to finish"
ret=0
while [ $ret -eq 0 ]; do
  ret=`nova console-log maas-server|egrep -c "Cloud-init v.* finished at" | cat`
  sleep 5
done
