# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Nova Power Driver."""

__all__ = []

from provisioningserver.drivers.power import PowerDriver
from provisioningserver.utils import shell
from provisioningserver.logger import get_maas_logger
from novaclient import client

REQUIRED_PACKAGES = [["nova", "python-novaclient"]]

maaslog = get_maas_logger("drivers.power.nova")

class NovaPowerDriver(PowerDriver):
    name = 'nova'
    description = "OpenStack nova Power Driver."
    settings = []

    def _issue_nova_api(
            self, power_change, nova_id=None, os_tenantname=None,
            os_username=None, os_password=None, os_authurl=None,
            **extra):

        nova = client.Client(2,os_username,
                            os_password,
                            os_tenantname,
                            os_authurl)

        task_state = getattr(nova.servers.get(nova_id), 'OS-EXT-STS:task_state')

        if power_change == 'on':
            if task_state == 'powering-on':
                return
            nova.servers.get(nova_id).start()
        elif power_change == 'off':
            if task_state == 'powering-off':
                return
            nova.servers.get(nova_id).stop()
        elif power_change == 'query':
            output = nova.servers.get(nova_id).status
            if 'ACTIVE' in output:
                return 'on'
            elif 'SHUTOFF' in output:
                return 'off'

    def detect_missing_packages(self):
        missing_packages = set()
        for binary, package in REQUIRED_PACKAGES:
            if not shell.has_command_available(binary):
                missing_packages.add(package)
        return list(missing_packages)

    def power_on(self, system_id, context):
        maaslog.info('nova power_on %s', system_id)
        self._issue_nova_api('on', **context)

    def power_off(self, system_id, context):
        maaslog.info('nova power_off %s', system_id)
        self._issue_nova_api('off', **context)

    def power_query(self, system_id, context):
        maaslog.info('nova power_query %s', system_id)
        return self._issue_nova_api('query', **context)

