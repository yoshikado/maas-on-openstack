import click
from moo.config import Config
from moo.openstack_utils import OpenstackUtils
from moo.cloudconfig import CloudConfig
from moo.configuremaas import ConfigureMAAS
from moo.maas_utils import MaasUtils


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
@pass_config
def cli(cfg, verbose):
    cfg.verbose = verbose


@cli.command()
@click.option('-r', '--release', default='xenial',
              help='trusty or xenial. default=xenial')
@click.option('-c', '--config', type=click.Path(),
              help='set configuration file')
@click.option('--name', help='name of the MAAS instance. default=maasstack')
@click.option('--network', help='network cidr. defualt=10.12.1.0/24')
@click.option('--network-name', help='network name for MAAS network. default=maas_net')
@click.option('--skip-network', is_flag=True,
              help='skip creating network.')
@pass_config
def deploy(cfg, release, config, name, network, network_name, skip_network):
    """Deploy MAAS environment."""
    if cfg.verbose:
        click.echo('Running in verbose mode')
    if name or network or network_name:
        cfg.maas_name = name if name else cfg.maas_name
        cfg.maas_network = network if network else cfg.maas_network
        cfg.maas_network_name = network_name if network_name else cfg.maas_network_name
    if not cfg.Init(config):
        return False
    # Create MAAS network
    openstack = OpenstackUtils(cfg)
    if not openstack.Init():
        return
    if not skip_network:
        if not openstack.CreateNetwork(cfg.maas_network, cfg.maas_network_name):
            click.echo("ERROR: Network not created.")
            click.echo("If you don't need to create network, use '--skip-network' option.")
            return
    # Create cloud-config file
    cloudconfig = CloudConfig(cfg)
    cloudconfig.CreateCloudConfig(release)
    # Deploy instance
    image = cfg.GetImage(release)
    if image is False:
        click.echo('ERROR: Image not found for %s' % release)
        return
    if not openstack.CreateKeyPair(cfg.keyname):
        return
    maasnet_id = openstack.GetNetID(cfg.maas_network_name)
    if release == 'xenial':
        src_file = cloudconfig.networkcfgfile
        dst_file = '/etc/cloud/cloud.cfg.d/maas-networking.cfg'
        instance_nics = [{'net-id': maasnet_id}]
        if not openstack.BootInstance(cfg.maas_name,
                                      image,
                                      instance_nics,
                                      flavor='m1.medium',
                                      cloud_cfg_file=cloudconfig.cloudcfgfile,
                                      config_drive=True,
                                      src=src_file,
                                      dst=dst_file):
            return
    elif release == 'trusty':
        port_id = openstack.CreatePort(cfg.project_net)
        instance_nics = [{'port-id': port_id}, {'net-id': maasnet_id}]
        if not openstack.BootInstance(cfg.maas_name,
                                      image,
                                      instance_nics,
                                      flavor='m1.medium',
                                      cloud_cfg_file=cloudconfig.cloudcfgfile):
            return
    openstack.WaitCloudInit(cfg.maas_name)
    # Configure MAAS
    configuremaas = ConfigureMAAS(cfg)
    configuremaas.run(release, cfg.maas_ip)
    click.echo('Finished deploying')


@cli.command()
@click.argument('cidr')
@click.argument('name')
@pass_config
def add_network(cfg, cidr, name):
    """Add network to OpenStack environment."""
    # FIXME
    if not cfg.Init():
        return False
    openstack = OpenstackUtils(cfg)
    if not openstack.CreateNetwork(cidr, name):
        click.echo("ERROR: Network not created.")


@cli.command()
@pass_config
def create_pxeimage(cfg):
    """Create iPXE image for OpenStack"""
    # FIXME
    click.echo('Under construction')


@cli.command()
@click.argument('name')
@click.option('--image', default='maas-pxe-image', help='image name')
@click.option('--flavor', default='m1.small', help='instance flavor. default=m1.small')
@click.option('--tag', default='maasstack', help='tag name for the node. default=maasstack')
@pass_config
def add_node(cfg, name, image, flavor, tag):
    """Create an instance and add it to maas."""
    # FIXME
    if not cfg.Init():
        return False
    openstack = OpenstackUtils(cfg)
    if not openstack.Init():
        return
    maasnet_id = openstack.GetNetID(cfg.maas_network_name)
    instance_nics = [{'net-id': maasnet_id}]
    if not openstack.BootInstance(name, image, instance_nics, flavor=flavor):
        return
    instance_id = openstack.GetInstanceID(name)
    mac = openstack.GetMAC(openstack.GetInstanceID(name))
    maas = MaasUtils(cfg, cfg.maas_ip)
    maas.UpdateHost(name, instance_id, mac, tag)

