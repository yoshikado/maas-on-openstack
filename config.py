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
        self.image = 'auto-sync/ubuntu-xenial-16.04-amd64-server-20170202-disk1.img'
        self.ext_net = 'ext_net'
        self._get_openstack_config()

    def _get_openstack_config(self):
        try:
            self.credentials = {}
            self.credentials['username'] = environ['OS_USERNAME']
            self.credentials['password'] = environ['OS_PASSWORD']
            self.credentials['auth_url'] = environ['OS_AUTH_URL']
            self.credentials['project_id'] = environ['OS_PROJECT_ID']
            self.credentials['tenant'] = environ['OS_TENANT_NAME']
            self.keyname = environ['OS_TENANT_NAME']
        except KeyError:
            click.echo('No environmental varialbles available.')

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
