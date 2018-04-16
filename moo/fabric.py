from fabric.operations import run as fabric_run
from fabric.context_managers import settings, hide, show
from pathlib import Path
from moo.logging import Logging

LOG = Logging(__name__)
log = LOG.getLogger()


def RunCommand(cfg, host, cmd):
    key = Path(cfg.configpath).joinpath(cfg.keypath)
    key = Path(key).joinpath(cfg.keyname)
    if cfg.log_level == "DEBUG":
        with settings(show('everything'), user='ubuntu',
                      host_string=host,
                      key_filename=key.as_posix(),
                      warn_only=True):
            results = fabric_run(cmd)
    else:
        with settings(hide('everything'), user='ubuntu',
                      host_string=host,
                      key_filename=key.as_posix(),
                      warn_only=True):
            results = fabric_run(cmd)
    return results
