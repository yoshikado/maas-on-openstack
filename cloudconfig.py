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
        f = open(self.file, 'w')
        yaml.safe_dump(f)
        f.close()

    def GenXenialConfig(self):
        if Path(self.file).is_file():
            remove(self.file)
        f = open(self.file, 'a', encoding='utf-8')
        f.write("#cloud-config\n")
        debconf_maas_rack = "maas-rack-controller maas-rack-controller/maas-url string %s\n" % self.cfg.maas_url_rack
        debconf_maas_region = "maas-region-controller maas/default-maas-url string %s\n" % self.cfg.maas_ip
        ips = IPNetwork(self.cfg.maas_network)
        ens4cfg = "auto ens4\niface ens4 inet static\naddress %s\nnetwork %s\nnetmask %s\ngateway %s\n" % (ips[2], ips[0], ips.netmask, ips[1])
        data = {'apt_sources': [{'source': 'ppa:juju/stable'},
                                {'source': 'ppa:yoshikadokawa/maas-nova'}],
                'debconf_selections': debconf_maas_rack + debconf_maas_region,
                'package_reboot_if_required': True,
                'package_update': True,
                'package_upgrade': True,
                'packages': ['maas', 'jq', 'python3-novaclient', 'python3-neutronclient'],
                'runcmd': ['ifup ens4'],
                'ssh_pwauth': False,
                'write_files': [{'content': ens4cfg,
                                 'path': '/etc/network/interfaces.d/ens4.cfg'}]}
        yaml.safe_dump(data, f, encoding='utf8', default_flow_style=False)
        f.close()
