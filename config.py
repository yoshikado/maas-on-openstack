from pathlib import Path
from netaddr import IPNetwork
from os import environ
import utils
import click


class Config(object):

    def __init__(self):
        self.verbose = False
        self.profile = 'admin'
        self.passw = 'ubuntu'
        self.maas_name = 'maasstack'
        self.maas_ip = '10.12.1.2'
        self.maas_network = '10.12.1.0/24'
        self.maas_network_name = 'maas_net'
        self.maas_url_rack = "http://%s:5240/MAAS" % self.maas_ip
        self.dns_forwarder_ip = '10.5.0.3'
        self.dynamic_start_ip = '10.12.1.10'
        self.dynamic_end_ip = '10.12.1.50'
        self.sed_maas_url_region = "http:\/\/%s\/MAAS" % self.maas_ip
        self.sed_maas_url_rack = "http:\/\/%s:5240\/MAAS" % self.maas_ip
        self.project_net = '%s_admin_net' % environ['OS_TENANT_NAME']
        self.configpath = Path(Path.home()).joinpath('.moo')
        self.configfile = 'moo_environment.yaml'
        self.image = '5f63568f-cb2e-4e80-a22c-63cc86074328'
        self.keyname = environ['OS_TENANT_NAME']
        self.ext_net = 'ext_net'

    def Update(self):
        ips = IPNetwork(self.maas_network)
        self.maas_ip = ips[2]
        self.dynamic_start_ip = ips[3]
        self.dynamic_end_ip = ips[int(ips.size/2)]
        self.maas_url_rack = "http://%s:5240/MAAS" % self.maas_ip
        self.sed_maas_url_region = "http:\/\/%s\/MAAS" % self.maas_ip
        self.sed_maas_url_rack = "http:\/\/%s:5240\/MAAS" % self.maas_ip

    def ValidateConfig(self):
        # FIXME
        click.echo('validate')

    def Init(self, config):
        # FIXME
        if config:
            if Path(config).exists():
                self.config = config
            else:
                click.echo('Configuration file: %s not found.' % config)
                return False
        else:
            config = utils.TouchFile(self.configpath, self.configfile)
        return True
        # f = open(self.configpath, 'w')
