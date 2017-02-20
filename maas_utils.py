import time
import click
from fabric.api import env
from fabric.operations import run as fabric_run
from fabric.context_managers import settings, hide


class MaasUtils:
    """MAAS Utils Class"""

    def __init__(self, cfg, maas_ip):
        self.cfg = cfg
        self.maas_ip = maas_ip

    def UpdateHost(self, instance_name, instance_id, mac):
        cmd = "maas %s machines read | \
               jq -r '.[].interface_set[] | \
               select(.mac_address==\"%s\").system_id'" % (self.cfg.profile, mac)
        sys_id = None
        click.echo('Waiting for instance to be ready for commision')
        while not sys_id:
            time.sleep(5)
            sys_id = self.RunCommand(cmd)
        cmd = "maas %s machine update %s power_type=nova \
        power_parameters_nova_id=%s \
        power_parameters_os_tenantname=%s \
        power_parameters_os_username=%s \
        power_parameters_os_password=%s \
        power_parameters_os_authurl=%s" % (self.cfg.profile, sys_id, instance_id,
                                           self.cfg.credentials['tenant'],
                                           self.cfg.credentials['username'],
                                           self.cfg.credentials['password'],
                                           self.cfg.credentials['auth_url'])
        self.RunCommand(cmd)
        cmd = "maas %s machine update %s hostname=%s" % (self.cfg.profile, sys_id, instance_name)
        self.RunCommand(cmd)
        click.echo('%s has been added to MAAS' % instance_name)

    def RunCommand(self, cmd):
        env.user = 'ubuntu'
        with settings(hide('everything'), host_string=self.maas_ip):
            results = fabric_run(cmd)
        # FIXME
        # click.echo(results)
        return results
