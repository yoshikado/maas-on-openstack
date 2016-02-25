#!/bin/bash

CreateNetwork() {
  neutron net-create $maas_nw_name
  neutron subnet-create $maas_nw_name \
      --name $maas_subnw_name \
      --allocation-pool start=${maas_nw_allocation_start},end=${maas_nw_allocation_end} \
      --disable-dhcp \
      $maas_nw_cidr
  neutron router-create $maas_rt_name
  neutron router-interface-add $maas_rt_name $maas_subnw_name
  neutron router-gateway-set $maas_rt_name $ext_net_id
}

CreatePXEbootImage() {
  dd if=/dev/zero of=$pxeboot_img_name bs=1M count=4
  mkdosfs $pxeboot_img_name
  sudo losetup /dev/loop0 $pxeboot_img_name
  sudo mount /dev/loop0 /mnt
  sudo syslinux --install /dev/loop0
  #wget http://boot.ipxe.org/ipxe.iso
  wget http://10.230.19.126:80/swift/v1/public-dir/ipxe.iso
  sudo mount -o loop ipxe.iso /media
  sudo cp /media/ipxe.krn /mnt
  cat << EOF | sudo tee "/mnt/syslinux.cfg"
DEFAULT ipxe
LABEL ipxe
 KERNEL ipxe.krn
EOF
  sudo umount /media/
  sudo umount /mnt
  sudo losetup -d /dev/loop0
}

UploadImage(){
  # upload pxe-boot image to glance
  glance image-create --name $1 --is-public false --disk-format raw --container-format bare < $2
}

CreateInstance(){
  maas_net_id=`neutron net-list | grep maas-network| cut -d\| -f2| tr -d ' '`
  ssh-keygen -b 2048 -t rsa -f maas-key -q -N ""
  nova keypair-add --pub-key maas-key.pub maas-keypair
  nova boot --flavor $flavor --image $boot_img --key-name maas-keypair --nic net-id=$admin_net_id --nic net-id=$maas_net_id --poll --user-data cloudconfig.yaml $1
  echo "Waiting for the instance to finish"
  ret=0
  while [ $ret -eq 0 ]; do
    ret=`nova console-log maas-server|egrep -c "Cloud-init v.* finished at" | cat`
    sleep 5
  done
}

CopyFiles() {
  echo "Copy files to the instance"
  ip=`nova show $maas_instance | grep "$admin_nw_name" | cut -d\| -f3 |tr -d ' '`
  scp -i maas-key ~/novarc maas-key* nova_driver/* setvars $ip:
}

### main ###
source setvars
CreateNetwork
CreatePXEbootImage
UploadImage $glance_img_name $pxeboot_img_name
CreateInstance $maas_instance
CopyFiles
# Configure MAAS
ssh -i maas-key $ip 'bash -s' < configure_maas.sh
echo "Finished environment preparation."
