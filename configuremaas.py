import click
from fabric.api import env
from fabric.operations import run as fabric_run
from fabric.context_managers import settings, hide


class ConfigureMAAS:

    def __init__(self, cfg):
        self.cfg = cfg

    def run(self, release, host):
        """ Run a command on the host. Assumes user has SSH keys setup """
        env.user = 'ubuntu'
        # env.use_ssh_config = True
        if release == 'trusty':
            self.ConfigureTrusty(host)
        elif release == 'xenial':
            self.ConfigureXenial(host)
        else:
            click.echo('The distribution is not supported')
        return True

    def ConfigureTrusty(self, host):
        # FIXME
        click.echo(host)

    def ConfigureXenial(self, host):
        cmd = 'sudo maas-region createadmin --username %s --password %s --email root@example.com' % (self.cfg.profile, self.cfg.passw)
        self.RunCommand(host, cmd)
        cmd = 'maas login %s http://localhost/MAAS/api/2.0 "`sudo maas-region apikey --username %s`"' % (self.cfg.profile, self.cfg.profile)
        self.RunCommand(host, cmd)
        cmd = "maas %s boot-resources import" % (self.cfg.profile)
        self.RunCommand(host, cmd)
        cmd = 'maas %s ipranges create type=dynamic start_ip=%s end_ip=%s' % (self.cfg.profile, self.cfg.dynamic_start_ip, self.cfg.dynamic_end_ip)
        self.RunCommand(host, cmd)
        cmd = 'maas %s rack-controllers read | jq -r .[].system_id' % (self.cfg.profile)
        rack_id = self.RunCommand(host, cmd)
        cmd = "maas %s subnets read | jq -M '.[] | select(.cidr==\"%s\").vlan.vid'" % (self.cfg.profile, self.cfg.maas_network)
        vid = self.RunCommand(host, cmd)
        cmd = "maas %s subnets read| jq -r '.[] | select(.cidr==\"%s\").vlan.fabric'" % (self.cfg.profile, self.cfg.maas_network)
        fabric = self.RunCommand(host, cmd)
        cmd = "maas %s fabrics read | jq -M '.[] | select(.name==\"%s\").id'" % (self.cfg.profile, fabric)
        fabric_id = self.RunCommand(host, cmd)
        cmd = 'maas %s vlan update %d %d primary_rack=%s dhcp_on=true' % (self.cfg.profile, int(fabric_id), int(vid), rack_id)
        self.RunCommand(host, cmd)
        cmd = "maas %s maas set-config name=upstream_dns value=%s" % (self.cfg.profile, self.cfg.dns_forwarder_ip)
        self.RunCommand(host, cmd)
        cmd = "maas %s maas set-config name=dnssec_validation value=no" % (self.cfg.profile)
        self.RunCommand(host, cmd)
        cmd = "sudo sed -i -e \"s/maas_url:.*/maas_url: %s/g\" \"/etc/maas/regiond.conf\"" % (self.cfg.sed_maas_url_region)
        self.RunCommand(host, cmd)
        cmd = "sudo sed -i -e \"s/maas_url:.*/maas_url: %s/g\" \"/etc/maas/rackd.conf\"" % (self.cfg.sed_maas_url_rack)
        self.RunCommand(host, cmd)
        cmd = "echo \"maas-rack-controller maas-rack-controller/maas-url string %s\" | sudo debconf-set-selections" % (self.cfg.maas_url_rack)
        self.RunCommand(host, cmd)
        cmd = "echo \"maas-region-controller maas/default-maas-url string %s\" | sudo debconf-set-selections" % (self.cfg.maas_ip)
        self.RunCommand(host, cmd)
        cmd = "maas %s sshkeys create key=\"`cat ~/.ssh/authorized_keys`\"" % (self.cfg.profile)
        self.RunCommand(host, cmd)
        self.RunCommand(host, 'sudo shutdown -r 30')


    def RunCommand(self, host, cmd):
        with settings(hide('everything'), host_string=host):
            results = fabric_run(cmd)
        # click.echo(results) # FIXME
        return results