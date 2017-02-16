from pathlib import Path
import yaml
import click


def isExist(path):
    if Path(path).is_file:
        return True
    else:
        return False


def GetMOOEnvVar(moo_envpath):
    if not Path(moo_envpath).is_file():
        click.echo('ERROR: You need to first create a init file.You can create it by typing:')
        click.echo("moo init")
        return False
    f = open(moo_envpath, 'r')
    moo_vars = yaml.load(f)
    f.close()
    return moo_vars


def TouchFile(dir, filename):
    try:
        Path(dir).mkdir(parents=True, exist_ok=True)
    except FileExistsError as e:
        click.echo(e)
        return False
    config = Path.joinpath(dir, filename)
    try:
        Path(config).touch(exist_ok=False)
    except FileExistsError as e:
        click.echo(e)
    return config
