import click
from config import Config
from openstack_utils import OpenstackUtils
from cloudconfig import CloudConfig
from configuremaas import ConfigureMAAS


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
        click.echo('We are in verbose mode')
    if name or network or network_name:
        cfg.maas_name = name if name else cfg.maas_name
        cfg.maas_network = network if network else cfg.maas_network
        cfg.maas_network_name = network_name if network_name else cfg.maas_network_name
        cfg.Update()
    # if not cfg.Init(config):
    #    return
    # Create MAAS network
    openstack = OpenstackUtils(cfg)
    if not skip_network:
        if not openstack.CreateNetwork(cfg.maas_network, cfg.maas_network_name):
            click.echo("ERROR: Network not created.")
            return
    # Create cloud-config file
    cloudconfig = CloudConfig(cfg)
    cloudconfig.CreateCloudConfig(release)
    # Deploy instance
    if not openstack.BootInstance(cfg.maas_name, cfg.maas_network_name, cloudconfig.file):
        return
    # Configure MAAS
    ip = openstack.GetIP(cfg.maas_name, cfg.project_net)
    configuremaas = ConfigureMAAS(cfg)
    configuremaas.run(release, ip)


@cli.command()
@click.argument('cidr')
@click.argument('name')
@pass_config
def add_network(cfg, cidr, name):
    """Add network to OpenStack environment."""
    if cfg.verbose:
        click.echo('We are in verbose mode')
    openstack = OpenstackUtils()
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
@click.option('--flavor', default='m1.small', help='instance flavor. default=m1.small')
@click.option('--tag', default='maasstack', help='tag name for the node. default=maasstack')
@pass_config
def add_node(cfg, name, flavor, tag):
    """Create an instance and add it to maas."""
    # FIXME
    click.echo('Under construction')
