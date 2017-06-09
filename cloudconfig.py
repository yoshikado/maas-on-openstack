from netaddr import IPNetwork
import yaml
from pathlib import Path
from os import remove


class CloudConfig:
    """cloud-config Class"""

    def __init__(self, cfg):
        self.file = 'cloudconfigtmp.yaml'
        self.cfg = cfg

    def CreateCloudConfig(self, release):
        if release == 'trusty':
            self.GenTrustyConfig()
        elif release == 'xenial':
            self.GenXenialConfig()
        else:
            print('hoge')
        return True

    def GenTrustyConfig(self):
        if Path(self.file).is_file():
            remove(self.file)
        f = open(self.file, 'a', encoding='utf-8')
        f.write("#cloud-config\n")
        debconf_maas_rack = "maas-cluster-controller maas-cluster-controller/maas-url string %s\n" % self.cfg.maas_url
        debconf_maas_region = "maas-region-controller-min maas/default-maas-url string %s\n" % self.cfg.maas_ip
        ips = IPNetwork(self.cfg.maas_network)
        eth1cfg = "auto eth1\n \
                   iface eth1 inet static\n \
                   address %s\n \
                   network %s\n \
                   netmask %s\n \
                   gateway %s\n" % (ips[2], ips[0], ips.netmask, ips[1])
        packages = [['maas', self.cfg.trusty_ver],
                    ['maas-cluster-controller', self.cfg.trusty_ver],
                    ['maas-region-controller', self.cfg.trusty_ver],
                    ['maas-cli', self.cfg.trusty_ver],
                    ['maas-common', self.cfg.trusty_ver],
                    ['maas-dhcp', self.cfg.trusty_ver],
                    ['maas-dns', self.cfg.trusty_ver],
                    ['maas-region-controller-min', self.cfg.trusty_ver],
                    ['python-maas-client', self.cfg.trusty_ver],
                    ['python-django-maas', self.cfg.trusty_ver],
                    ['python-maas-provisioningserver', self.cfg.trusty_ver],
                    ['maas-proxy', self.cfg.trusty_ver],
                    'jq', 'python-novaclient', 'python-neutronclient']
        data = {'apt_sources': [{'source': 'ppa:juju/stable'},
                                {'source': 'ppa:yoshikadokawa/maas-nova'}],
                'debconf_selections': debconf_maas_rack + debconf_maas_region,
                'package_update': True,
                'package_upgrade': True,
                'packages': packages,
                'runcmd': ['ifup eth1'],
                'ssh_pwauth': False,
                'write_files': [{'content': eth1cfg,
                                 'path': '/etc/network/interfaces.d/eth1.cfg'}]}
        yaml.safe_dump(data, f, encoding='utf8', default_flow_style=False)
        f.close()

    def GenXenialConfig(self):
        if Path(self.file).is_file():
            remove(self.file)
        f = open(self.file, 'a', encoding='utf-8')
        f.write("#cloud-config\n")
        debconf_maas_rack = "maas-rack-controller maas-rack-controller/maas-url string %s\n" % self.cfg.maas_url_rack
        debconf_maas_region = "maas-region-controller maas/default-maas-url string %s\n" % self.cfg.maas_ip
        ips = IPNetwork(self.cfg.maas_network)
        ens4cfg = "auto ens4\n \
                  iface ens4 inet static\n \
                  address %s\n \
                  network %s\n \
                  netmask %s\n \
                  gateway %s\n" % (ips[2], ips[0], ips.netmask, ips[1])
        packages = [['maas', self.cfg.xenial_ver],
                    ['maas-cli', self.cfg.xenial_ver],
                    ['maas-common', self.cfg.xenial_ver],
                    ['maas-dhcp', self.cfg.xenial_ver],
                    ['maas-dns', self.cfg.xenial_ver],
                    ['maas-rack-controller', self.cfg.xenial_ver],
                    ['maas-region-controller', self.cfg.xenial_ver],
                    ['maas-region-api', self.cfg.xenial_ver],
                    ['python3-maas-client', self.cfg.xenial_ver],
                    ['python3-django-maas', self.cfg.xenial_ver],
                    ['python3-maas-provisioningserver', self.cfg.xenial_ver],
                    ['maas-proxy', self.cfg.xenial_ver],
                    'jq', 'python3-novaclient', 'python3-neutronclient']
        data = {'apt_sources': [{'source': 'ppa:juju/stable'},
                                {'source': 'ppa:yoshikadokawa/maas-nova'}],
                'debconf_selections': debconf_maas_rack + debconf_maas_region,
                'package_update': True,
                'package_upgrade': True,
                'packages': packages,
                'runcmd': ['ifup ens4'],
                'ssh_pwauth': False,
                'write_files': [{'content': ens4cfg,
                                 'path': '/etc/network/interfaces.d/ens4.cfg'}]}
        yaml.safe_dump(data, f, encoding='utf8', default_flow_style=False)
        f.close()
