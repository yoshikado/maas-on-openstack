from netaddr import IPNetwork
import moo.fabric
from moo.logging import Logging

LOG = Logging(__name__)
log = LOG.getLogger()


class ConfigureMAAS:

    def __init__(self, cfg):
        self.cfg = cfg
        LOG.SetLevel(self.cfg.log_level)

    def run(self, release, host):
        """ Run a command on the host. Assumes user has SSH keys setup """
        # env.use_ssh_config = True
        if release == 'trusty':
            self.ConfigureTrusty(host)
        elif release == 'xenial':
            self.ConfigureXenial(host)
        else:
            log.error('The distribution is not supported')
        return True

    def ConfigureTrusty(self, host):
        cmd = "sudo maas-region-admin createadmin \
              --username %s --password %s --email root@example.com" % (self.cfg.profile, self.cfg.passw)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = 'maas login %s http://localhost/MAAS/api/1.0 \
        "`sudo maas-region-admin apikey --username %s`"' % (self.cfg.profile, self.cfg.profile)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s boot-resources import" % (self.cfg.profile)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = 'maas %s node-groups list | jq -r .[].uuid' % (self.cfg.profile)
        rack_uuid = moo.fabric.RunCommand(self.cfg, host, cmd)
        ips = IPNetwork(self.cfg.maas_network)
        cmd = "maas %s node-group-interface update -d %s eth1 \
          ip_range_low=%s \
          ip_range_high=%s \
          management=2 \
          broadcast_ip=%s \
          router_ip=%s \
          static_ip_range_low=%s \
          static_ip_range_high=%s" % (self.cfg.profile, rack_uuid,
                                      self.cfg.dynamic_start_ip,
                                      self.cfg.dynamic_end_ip,
                                      ips[ips.size-1], ips[1],
                                      ips[int(ips.size/2+1)], ips[ips.size-2])
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s maas set-config name=upstream_dns value=%s" % (self.cfg.profile, self.cfg.dns_forwarder_ip)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s sshkeys new key=\"`cat ~/.ssh/authorized_keys`\"" % (self.cfg.profile)
        moo.fabric.RunCommand(self.cfg, host, cmd)

    def ConfigureXenial(self, host):
        cmd = "sudo maas-region createadmin --username %s \
              --password %s --email root@example.com" % (self.cfg.profile, self.cfg.passw)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = 'maas login %s http://localhost/MAAS/api/2.0 \
              "`sudo maas-region apikey --username %s`"' % (self.cfg.profile, self.cfg.profile)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s boot-resources import" % (self.cfg.profile)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        is_importing = "true"
        while is_importing == "true":
            cmd = "maas %s boot-resources is-importing | awk 'NR==1'" % (self.cfg.profile)
            is_importing = moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = 'maas %s ipranges create type=dynamic start_ip=%s end_ip=%s' % \
              (self.cfg.profile, self.cfg.dynamic_start_ip, self.cfg.dynamic_end_ip)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = 'maas %s ipranges create type=reserved start_ip=%s end_ip=%s' % \
              (self.cfg.profile, self.cfg.reserved_start_ip, self.cfg.reserved_end_ip)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = 'maas %s rack-controllers read | jq -r .[].system_id' % (self.cfg.profile)
        rack_id = moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s subnets read | jq -M '.[] | \
              select(.cidr==\"%s\").vlan.vid'" % (self.cfg.profile, self.cfg.maas_network)
        vid = moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s subnets read| jq -r '.[] | \
              select(.cidr==\"%s\").vlan.fabric'" % (self.cfg.profile, self.cfg.maas_network)
        fabric = moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s subnets read | jq -M '.[]| select(.name==\"%s\").id'" % \
              (self.cfg.profile, self.cfg.maas_network)
        subnet_id = moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s subnet update %d name=main" % (self.cfg.profile, int(subnet_id))
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s fabrics read | jq -M '.[] | select(.name==\"%s\").id'" % (self.cfg.profile, fabric)
        fabric_id = moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = 'maas %s vlan update %d %d primary_rack=%s dhcp_on=true' % \
              (self.cfg.profile, int(fabric_id), int(vid), rack_id)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s maas set-config name=upstream_dns value=%s" % (self.cfg.profile, self.cfg.dns_forwarder_ip)
        moo.fabric.RunCommand(self.cfg, host, cmd)
        cmd = "maas %s sshkeys create key=\"`cat ~/.ssh/authorized_keys`\"" % (self.cfg.profile)
        moo.fabric.RunCommand(self.cfg, host, cmd)
