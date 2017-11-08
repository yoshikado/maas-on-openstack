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
        self.maas_network = '10.12.1.0/24'
        self.maas_network_name = 'maas_net'
        self.dns_forwarder_ip = utils.get_resolv()
        self.configpath = Path(Path.home()).joinpath('.moo')
        self.configfile = 'moo_environment.yaml'
        self.xenial_image = 'auto-sync/ubuntu-xenial-16.04-amd64-server-20171026.1-disk1.img'
        self.trusty_image = 'auto-sync/ubuntu-trusty-14.04-amd64-server-20171101-disk1.img'
        self.ext_net = 'ext_net'
        self.trusty_ver = '1.9.5+bzr4599-0ubuntu1~14.04.1lp1657941rev1'
        self.xenial_ver = ''
        self.keypath = Path.joinpath(self.configpath, 'ssh')
        self.keyname = 'maas_key'
        self.maas_ppa = 'ppa:maas/stable'

    def _get_openstack_config(self):
        try:
            self.credentials = {}
            self.credentials['username'] = environ['OS_USERNAME']
            self.credentials['password'] = environ['OS_PASSWORD']
            self.credentials['auth_url'] = environ['OS_AUTH_URL']
            self.credentials['project_name'] = environ['OS_PROJECT_NAME']
            self.project_net = '%s_admin_net' % environ['OS_PROJECT_NAME']
        except KeyError as e:
            click.echo('Provide OpenStack variables. %s' % e)
            return False
        return True

    def Update(self):
        ips = IPNetwork(self.maas_network)
        self.maas_ip = ips[2]
        self.reserved_start_ip = ips[3]
        self.reserved_end_ip = ips[9]
        self.dynamic_start_ip = ips[10]
        self.dynamic_end_ip = ips[int(ips.size/2)]
        self.maas_url = "http://%s/MAAS" % self.maas_ip
        self.maas_url_rack = "http://%s:5240/MAAS" % self.maas_ip
        self.sed_maas_url_region = "http:\/\/%s\/MAAS" % self.maas_ip
        self.sed_maas_url_rack = "http:\/\/%s:5240\/MAAS" % self.maas_ip
        if not self._get_openstack_config():
            return False
        return True

    def ValidateConfig(self):
        # FIXME
        click.echo('validate')

    def GetImage(self, release):
        if release == 'trusty':
            return self.trusty_image
        elif release == 'xenial':
            return self.xenial_image
        else:
            click.echo('The distribution is not supported')

    def Init(self, config=None):
        # FIXME
        if config:
            moo_vars = utils.GetMOOEnvVar(config)
        else:
            config = utils.TouchFile(self.configpath, self.configfile)
        if not self.Update():
            return False
        # click.echo("resolv:%s" % self.dns_forwarder_ip)
        return True
        # f = open(self.configpath, 'w')
