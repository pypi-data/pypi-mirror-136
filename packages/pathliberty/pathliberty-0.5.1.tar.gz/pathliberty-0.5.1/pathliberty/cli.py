import os

import click
def get_env_vars(ctx, args, incomplete):
    return [k for k in os.environ.keys() if incomplete in k]

@click.command()
@click.argument("--envvar", type=click.STRING, autocompletion=get_env_vars)
def cmd1(envvar):
    click.echo('Environment variable: %s' % envvar)
    click.echo('Value: %s' % os.environ[envvar])