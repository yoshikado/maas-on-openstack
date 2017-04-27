import urllib
import click
import time
import re
import utils
from pathlib import Path
import novaclient.client as novaclient
from neutronclient.v2_0 import client as neutronclient
import neutronclient.neutron.v2_0 as neutronv2
import neutronclient.common.exceptions as neutronexceptions


class OpenstackUtils:
    """OpenStack Utils Class"""

    def __init__(self, cfg):
        self.cfg = cfg
        self.credentials = self.cfg.credentials
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
        try:
            detail = neutronv2.find_resource_by_name_or_id(self.neutron, 'network', network_name)
        except neutronexceptions.NotFound as e:
            click.echo(e)
            return e
        return detail['id']

    def GetInstanceID(self, instance_name):
        try:
            instance_id = self.nova.servers.find(name=instance_name).id
        except novaclient.exceptions.NotFound as e:
            click.echo(e)
            return False
        return instance_id

    def GetIP(self, name, network_name):
        try:
            ips = self.nova.servers.ips(self.nova.servers.find(name=name))
        except novaclient.exceptions.NotFound as e:
            click.echo(e)
            return False
        ip = ips[network_name][0]['addr']
        return ip

    def GetFlavor(self, flavor_name):
        try:
            flavor = self.nova.flavors.find(name=flavor_name)
        except novaclient.exceptions.NotFound as e:
            click.echo(e)
            return False
        return flavor

    def GetImageID(self, image_name):
        try:
            image = self.nova.glance.find_image(name_or_id=image_name)
        except novaclient.exceptions.NotFound as e:
            click.echo(e)
            return False
        return image.id

    def GetMAC(self, instance_id):
        ports = self.neutron.list_ports()
        for port in ports['ports']:
            if port['device_id'] == instance_id:
                return port['mac_address']
        return False

    def KeyExist(self, keyname):
        try:
            self.nova.keypairs.find(name=keyname)
        except novaclient.exceptions.NotFound:
            return False
        return True

    def CreateKeyPair(self, keyname):
        click.echo('Creating keypair')
        if self.KeyExist(keyname):
            keypath = Path(self.cfg.configpath).joinpath(self.cfg.keypath)
            keypath = Path(keypath).joinpath(self.cfg.keyname)
            if not keypath.is_file():
                click.echo('ERROR: keypair in OpenStack exists, but key file not found.')
                click.echo('%s' % keypath)
                return False
            click.echo('Keypair exists, skip creating')
            return True
        else:
            pubkey = utils.CreateSSHKey(keyname, self.cfg.keypath)
            self.nova.keypairs.create(keyname, pubkey)
        return True

    def BootInstance(self, name, network_name, image, flavor='m1.small', cloud_cfg_file=None, default_nw=False):
        defaultnet_id = self.GetNetID(self.cfg.project_net)
        maasnet_id = self.GetNetID(network_name)
        flavor = self.GetFlavor(flavor)
        image_id = self.GetImageID(image)
        if default_nw:
            if not defaultnet_id or not maasnet_id or not flavor or not image_id:
                return False
            else:
                nics = [{'net-id': defaultnet_id}, {'net-id': maasnet_id}]
        else:
            if not maasnet_id or not flavor or not image_id:
                return False
            else:
                nics = [{'net-id': maasnet_id}]
        key = self.cfg.keyname
        if self.GetInstanceID(name):
            click.echo('ERROR:Could not create instance. Instance already created: %s' % name)
            return False
        try:
            with open(cloud_cfg_file) as userdata_file:
                instance = self.nova.servers.create(name, image_id, flavor,
                                                    userdata=userdata_file,
                                                    key_name=key,
                                                    nics=nics)
        except TypeError:
            instance = self.nova.servers.create(name, image_id, flavor,
                                                key_name=key,
                                                nics=nics)
        while instance.status == 'BUILD':
            click.echo("Waiting for instance to be active.")
            time.sleep(10)
            instance = self.nova.servers.get(instance.id)
        return True

    def WaitCloudInit(self, instance_name):
        instance = self.GetInstanceID(instance_name)
        console_log = self.nova.servers.get_console_output(instance, 10)
        pattern = "Cloud-init v.* finished at"
        click.echo("Waiting for cloud-init to finish. This will take a while...")
        while not re.search(pattern, console_log):
            time.sleep(10)
            console_log = self.nova.servers.get_console_output(instance, 10)
