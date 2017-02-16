from os import environ
import urllib
import click
import time
import re
import novaclient.client as novaclient
from neutronclient.v2_0 import client as neutronclient


class OpenstackUtils:
    """OpenStack Utils Class"""

    def __init__(self, cfg):
        self.cfg = cfg
        try:
            self.credentials = {}
            self.credentials['username'] = environ['OS_USERNAME']
            self.credentials['password'] = environ['OS_PASSWORD']
            self.credentials['auth_url'] = environ['OS_AUTH_URL']
            self.credentials['project_id'] = environ['OS_PROJECT_ID']
        except KeyError:
            click.echo('No environmental varialbles available.')
        self.neutron = neutronclient.Client(**self.credentials)
        self.nova = novaclient.Client(2, self.credentials["username"],
                                      self.credentials["password"],
                                      self.credentials["project_id"],
                                      self.credentials["auth_url"])
        self.CheckAuth()

    def CheckAuth(self):
        """Check if credential info are correct"""
        try:
            urllib.request.urlopen(self.credentials["auth_url"])
        except urllib.error.URLError:
            click.echo('Auth URL error: %s' %
                       self.credentials["auth_url"])
        try:
            self.nova.authenticate()
        except novaclient.exceptions.Unauthorized:
            click.echo('Failed to authenticate with OpenStack')

    def CheckDuplicateNetwork(self, cidr, name):
        """Check for possible duplicate network name and cidr"""
        subn = self.neutron.list_subnets()
        for i in range(len(subn['subnets'])):
            if cidr == subn['subnets'][i]['cidr']:
                click.echo('Duplicate subnet found: %s' % cidr)
                return True
        netw = self.neutron.list_networks()
        for i in range(len(netw['networks'])):
            if name == netw['networks'][i]['name']:
                click.echo('Duplicate network found: %s' % name)
                return True

    def CreateNetwork(self, cidr, name):
        """Create Network(network, subnet, router)"""
        if self.CheckDuplicateNetwork(cidr, name):
            return False
        ipv = 4
        # Create network
        try:
            body_netw = {'network': {'name': name,
                         'admin_state_up': True}}
            ret = self.neutron.create_network(body=body_netw)
        finally:
            click.echo('Create Network')
        try:
            # Create subnet
            network_id = ret['network']['id']
            subnet_name = name + "_subnet"
            body_subn = {'subnets': [{
                         'cidr': cidr,
                         'ip_version': ipv,
                         'name': subnet_name,
                         'enable_dhcp': False,
                         'network_id': network_id}]}
            ret = self.neutron.create_subnet(body=body_subn)
        finally:
            click.echo('Create subnet')
        try:
            subnet_id = ret['subnets'][0]['id']
            router_name = name + "_router"
            body_rt = {'router': {
                       'name': router_name,
                       'admin_state_up': True}}
            ret = self.neutron.create_router(body_rt)
        finally:
            click.echo('Create router')
        try:
            ext_net_id = self.GetNetID(self.cfg.ext_net)
            router_id = ret['router']['id']
            body_rt = {'network_id': ext_net_id}
            self.neutron.add_gateway_router(router_id, body_rt)
        finally:
            click.echo('Add gateway to router')
        try:
            body_rt = {'subnet_id': subnet_id}
            ret = self.neutron.add_interface_router(router_id, body_rt)
        finally:
            click.echo('Add interface to router')
        return True

    def GetNetID(self, network_name):
        netw = self.neutron.list_networks()
        for i in range(len(netw['networks'])):
            if network_name == netw['networks'][i]['name']:
                return netw['networks'][i]['id']
        return False

    def GetInstanceID(self, instance):
        try:
            instance_id = self.nova.servers.find(name=instance).id
        except novaclient.exceptions.NotFound as e:
            return False
        return instance_id

    def GetIP(self, name, network_name):
        try:
            ips = self.nova.servers.ips(self.nova.servers.find(name=name))
        except novaclient.exceptions.NotFound as e:
            # click.echo(e)
            return False
        ip = ips[network_name][0]['addr']
        return ip

    def BootInstance(self, name, network_name, cloud_cfg_file):
        defaultnet_id = self.GetNetID(self.cfg.project_net)
        maasnet_id = self.GetNetID(network_name)
        image = self.cfg.image
        flavor = self.nova.flavors.find(name='m1.small')
        key = self.cfg.keyname
        nics = [{'net-id': defaultnet_id}, {'net-id': maasnet_id}]
        if self.GetInstanceID(name):
            click.echo('ERROR:Could not create instance. Instance already created: %s' % name)
            return False
        with open(cloud_cfg_file) as userdata_file:
            instance = self.nova.servers.create(name, image, flavor,
                                                userdata=userdata_file,
                                                key_name=key,
                                                nics=nics)
        while instance.status == 'BUILD':
            click.echo("Waiting for instance to be active.")
            time.sleep(10)
            instance = self.nova.servers.get(instance.id)
        console_log = self.nova.servers.get_console_output(instance, 10)
        pattern = "Cloud-init v.* finished at"
        click.echo("Waiting for cloud-init to finish. This will take a while...")
        while not re.search(pattern, console_log):
            time.sleep(10)
            console_log = self.nova.servers.get_console_output(instance, 10)
        return True
