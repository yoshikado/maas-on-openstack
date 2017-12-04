import time
import click
from pathlib import Path
from fabric.operations import run as fabric_run
from fabric.context_managers import settings, hide


class MaasUtils:
    """MAAS Utils Class"""

    def __init__(self, cfg, maas_ip):
        self.cfg = cfg
        self.maas_ip = maas_ip

    def UpdateHost(self, instance_name, instance_id, mac, tag):
        ver = self.GetVersion()
        if int(ver[0]) == 1:
            self.UpdateHostV1(instance_name, instance_id, mac, tag)
        elif int(ver[0]) == 2:
            self.UpdateHostV2(instance_name, instance_id, mac, tag)
        else:
            click.echo('ERROR: MAAS version %s is not supported' % ver)
            return

    def UpdateHostV1(self, instance_name, instance_id, mac, tag):
        cmd = "maas %s nodes list | \
               jq -r '.[] | select(.interface_set[].mac_address==\"%s\").system_id'" % (self.cfg.profile, mac)
        sys_id = None
        click.echo('Waiting for instance to be ready for commision')
        while not sys_id:
            time.sleep(5)
            sys_id = self.RunCommand(cmd)

        cmd = "maas %s node update %s power_type=nova \
               power_parameters_nova_id=%s \
               power_parameters_os_tenantname=%s \
               power_parameters_os_username=%s \
               power_parameters_os_password=%s \
               power_parameters_os_authurl=%s" % (self.cfg.profile, sys_id, instance_id,
                                                  self.cfg.credentials['project_name'],
                                                  self.cfg.credentials['username'],
                                                  self.cfg.credentials['password'],
                                                  self.cfg.credentials['auth_url'])
        self.RunCommand(cmd)
        cmd = "maas %s node update %s hostname=%s" % (self.cfg.profile, sys_id, instance_name)
        self.RunCommand(cmd)
        cmd = "maas %s tag read %s" % (self.cfg.profile, tag)
        ret = self.RunCommand(cmd)
        if ret == "Not Found":
            cmd = "maas %s tags new name=%s" % (self.cfg.profile, tag)
            self.RunCommand(cmd)
        cmd = "maas %s tag update-nodes %s add=%s" % (self.cfg.profile, tag, sys_id)
        self.RunCommand(cmd)
        click.echo('%s has been added to MAAS' % instance_name)

    def UpdateHostV2(self, instance_name, instance_id, mac, tag):
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
                                           self.cfg.credentials['project_name'],
                                           self.cfg.credentials['username'],
                                           self.cfg.credentials['password'],
                                           self.cfg.credentials['auth_url'])
        self.RunCommand(cmd)
        cmd = "maas %s machine update %s hostname=%s" % (self.cfg.profile, sys_id, instance_name)
        self.RunCommand(cmd)
        cmd = "maas %s tag read %s" % (self.cfg.profile, tag)
        ret = self.RunCommand(cmd)
        click.echo('ret:%s' % ret)
        if ret == "Not Found":
            cmd = "maas %s tags create name=%s" % (self.cfg.profile, tag)
            click.echo('new tag created: %s' % tag)
            self.RunCommand(cmd)
        cmd = "maas %s tag update-nodes %s add=%s" % (self.cfg.profile, tag, sys_id)
        self.RunCommand(cmd)
        click.echo('%s has been added to MAAS' % instance_name)

    def GetVersion(self):
        cmd = "maas %s version read | jq -r .version" % (self.cfg.profile)
        ret = self.RunCommand(cmd)
        return ret

    def RunCommand(self, cmd):
        key = Path(self.cfg.configpath).joinpath(self.cfg.keypath)
        key = Path(key).joinpath(self.cfg.keyname)
        with settings(hide('everything'), user='ubuntu', host_string=self.maas_ip, key_filename=key.as_posix(), warn_only=True):
            results = fabric_run(cmd)
        # FIXME
        # click.echo(results)
        return results
