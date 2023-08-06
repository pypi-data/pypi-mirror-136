import click

from .. import controllers
from ..main import cli


@cli.command(name='search')
@click.option('--query', help='Search query to be sent to sources')
@click.pass_context
def _search():
    pass
