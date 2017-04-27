from pathlib import Path
from os import chmod
from Crypto.PublicKey import RSA
import yaml
import click


def CheckDir(dir):
    if Path(dir).is_file():
        click.echo('%s is not a directory but file.' % dir)
        return False
    if not Path(dir).is_dir():
        Path(dir).mkdir(parents=True, exist_ok=True)
    return True


def GetMOOEnvVar(moo_envpath):
    if not Path(moo_envpath).is_file():
        click.echo('Configuration file: %s not found.' % moo_envpath)
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
    try:
        Path(dir).mkdir(parents=True, exist_ok=True)
    except FileExistsError as e:
        # click.echo(e)
        return False
    config = Path.joinpath(dir, filename)
    try:
        Path(config).touch(exist_ok=False)
    except FileExistsError as e:
        click.echo(e)
    return config
