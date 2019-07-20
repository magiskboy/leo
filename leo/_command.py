"""
Author: Nguyen Khac Thanh
"""
from typing import IO
import click

from leo import _core


@click.group()
def cli() -> None:
    """Main group
    """


@cli.command()
@click.argument('file', type=click.File('r'))
@click.option('--delay', type=click.INT, default=60*60*24)
@click.option('--detach', type=click.BOOL, default=False)
@click.option('--psrv', type=click.STRING, default='http://localhost')
@click.option('--els', type=click.STRING, default='http://localhost:88')
def run(file: IO, delay: int, detach: bool, psrv: str, els: str) -> None:
    """Sync data product for tags
    """
    _core.run(file, delay, detach, (psrv, els))


@cli.command()
def stop() -> None:
    """Stop all task is running in background
    """
    msg = _core.stop_bg_process()
    click.echo(msg)
