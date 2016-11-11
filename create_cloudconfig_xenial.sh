#!/bin/bash

CreateCloudconfig(){
  for i in `seq 1 $1`
  do
    ifname="ens`expr 3 + $i`"
    a="  - content: |
      auto $ifname
      iface $ifname inet static
      address 10.12.${i}.2
      network 10.12.${i}.0
      netmask 255.255.255.0
      gateway 10.12.${i}.1
    path: /etc/network/interfaces.d/${ifname}.cfg"
    if [ "${interfaces:-X}" = X ]; then
      interfaces=$a
    else
      interfaces=$interfaces$'\n'$a
    fi
    b="  - ifup $ifname"
    if [ "${runcmd:-X}" = X ]; then
      runcmd=$b
    else
      runcmd=$runcmd$'\n'$b
    fi
  done
  cat << EOF | tee "cloudconfig.yaml"
#cloud-config
apt_sources:
  - source: 'ppa:juju/stable'
package_update: true
package_upgrade: true
package_reboot_if_required: true
packages:
  - maas
  - jq
  - python3-novaclient
  - python3-neutronclient
debconf_selections: |
  maas-rack-controller maas-rack-controller/maas-url string http://10.12.1.2:5240/MAAS
  maas-region-controller maas/default-maas-url string 10.12.1.2
write_files:
$interfaces
runcmd:
$runcmd
ssh_pwauth: False
EOF
}

CreateCloudconfig
