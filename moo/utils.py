from pathlib import Path
from Crypto.PublicKey import RSA
import yaml
import re
import urllib.request
from moo.logging import Logging

LOG = Logging(__name__)
log = LOG.getLogger()


def CheckDir(dir):
    if Path(dir).is_file():
        log.error('%s is not a directory but file.' % dir)
        return False
    if not Path(dir).is_dir():
        Path(dir).mkdir(parents=True, exist_ok=True)
    return True


def GetMOOEnvVar(moo_envpath):
    if not Path(moo_envpath).is_file():
        log.error('Configuration file: %s not found.' % moo_envpath)
        return False
    f = open(moo_envpath, 'r')
    moo_vars = yaml.load(f)
    f.close()
    return moo_vars


def CreateSSHKey(keyname, dir):
    key = RSA.generate(2048)
    CheckDir(dir)
    privkey_path = Path(dir).joinpath(keyname)
    with privkey_path.open('wb') as content_file:
        content_file.write(key.exportKey('PEM'))
    privkey_path.chmod(0o600)
    pubkey = key.publickey()
    keyname = keyname + '.pub'
    pubkey_path = Path(dir).joinpath(keyname)
    with pubkey_path.open('wb') as content_file:
        content_file.write(pubkey.exportKey('OpenSSH'))
    return pubkey.exportKey('OpenSSH').decode("utf-8")


def TouchFile(dir, filename):
    Path(dir).mkdir(parents=True, exist_ok=True)
    config = Path.joinpath(dir, filename)
    try:
        Path(config).touch(exist_ok=False)
    except FileExistsError:
        return config
    return config


def get_resolv():
    rconf = open("/etc/resolv.conf", "r")
    line = rconf.readline()
    while line:
        ip = re.search(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", line)
        if ip is None:
            line = rconf.readline()
            continue
        nameserver = ip.group()
        line = rconf.readline()
    return nameserver


def url_is_alive(url):
    request = urllib.request.Request(url)
    request.get_method = lambda: 'HEAD'

    try:
        urllib.request.urlopen(request)
        return True
    except urllib.request.HTTPError:
        return False
