from netaddr import IPNetwork
import yaml
from pathlib import Path
from os import remove


class CloudConfig:
    """cloud-config Class"""

    def __init__(self, cfg):
        self.cloudcfgfile = str(Path(Path.home()).joinpath('cloudcfgtmp.yaml'))
        self.networkcfgfile = str(Path(Path.home()).joinpath('networkcfgtmp.yaml'))
        self.cfg = cfg

    def CreateCloudConfig(self, release):
        if release == 'trusty':
            self.SetTrustyVar()
        elif release == 'xenial':
            self.SetXenialVar()
        else:
            print('%s is not supported.' % release)
            return False
        self.GenerateCloudConfig(release)
        self.GenerateCloudNetConfig(release)
        return True

    def SetTrustyVar(self):
        self.debconf_maas_rack = "maas-cluster-controller maas-cluster-controller/maas-url string %s\n" \
                                 % self.cfg.maas_url
        self.debconf_maas_region = "maas-region-controller-min maas/default-maas-url string %s\n" % self.cfg.maas_ip
        self.packages = [['maas', self.cfg.trusty_ver],
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
        self.ppa = [{'source': 'ppa:yoshikadokawa/maas-nova'}]
        ips = IPNetwork(self.cfg.maas_network)
        self.eth1cfg = "auto eth1\n\
iface eth1 inet static\n\
address %s\n\
network %s\n\
netmask %s\n\
gateway %s\n" % (ips[2], ips[0], ips.netmask, ips[1])

    def SetXenialVar(self):
        self.debconf_maas_rack = ""
        self.debconf_maas_region = ""
        self.interface = "ens3"
        self.packages = [['maas', self.cfg.xenial_ver],
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
        self.ppa = [{'source': 'ppa:yoshikadokawa/maas-nova'}]

    def GenerateCloudConfig(self, release):
        if Path(self.cloudcfgfile).is_file():
            remove(self.cloudcfgfile)
        f = open(self.cloudcfgfile, 'a', encoding='utf-8')
        f.write("#cloud-config\n")
        data = {'apt_sources': self.ppa,
                'debconf_selections': self.debconf_maas_rack + self.debconf_maas_region,
                'package_update': True,
                'package_upgrade': True,
                'packages': self.packages,
                'ssh_pwauth': False}
        if release == 'trusty':
            data.update({'runcmd': ['ifup eth1'],
                         'write_files': [{'content': self.eth1cfg,
                                          'path': '/etc/network/interfaces.d/eth1.cfg'}]})
        yaml.safe_dump(data, f, encoding='utf8', default_flow_style=False)
        f.close()

    def GenerateCloudNetConfig(self, release):
        if release == 'trusty':
            return True
        if Path(self.networkcfgfile).is_file():
            remove(self.networkcfgfile)
        f = open(self.networkcfgfile, 'a', encoding='utf-8')
        ips = IPNetwork(self.cfg.maas_network)
        data = {'network': {'version': 1,
                            'config': [{'subnets': [{'dns_nameservers': [self.cfg.dns_forwarder_ip],
                                                     'type': 'static',
                                                     'gateway': str(ips[1]),
                                                     'address': str(self.cfg.maas_ip)}],
                                        'type': 'physical',
                                        'name': self.interface}]}}
        yaml.safe_dump(data, f, encoding='utf8', default_flow_style=False)
        f.close()
