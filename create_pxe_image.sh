#!/bin/bash

CreatePXEbootImage() {
  if [ ! -f $pxeboot_img_name ]; then
    dd if=/dev/zero of=$pxeboot_img_name bs=1M count=4
  fi
  mkdosfs $pxeboot_img_name
  sudo losetup /dev/loop0 $pxeboot_img_name
  sudo mount /dev/loop0 /mnt
  sudo syslinux --install /dev/loop0
  #wget http://boot.ipxe.org/ipxe.iso
  sudo mount -o loop images/ipxe.iso /media
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

source setvars
CreatePXEbootImage
UploadImage $glance_img_name $pxeboot_img_name
