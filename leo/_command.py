"""
Author: Nguyen Khac Thanh
"""
import click

from leo import (
    _service,
    _utils
)


@click.group()
def cli() -> None:
    """Main group
    """


@cli.command()
@click.option('--delay', type=click.INT, default=60*60*24)
@click.option('--detach', type=click.BOOL, default=False)
@click.option('--psrv', type=click.STRING, default='http://localhost')
@click.option('--els', type=click.STRING, default='http://localhost:88')
def run(delay: int, detach: bool, psrv: str, els: str) -> None:
    """Sync data product for tags
    """
    if _utils.is_task_already():
        click.echo('Task already')
    else:
        pid = _service.run(delay, detach, (psrv, els))
        if pid:
            click.echo(f'Task is running in background with pid {pid}')
        else:
            click.echo('Run task fail')


@cli.command()
def stop() -> None:
    """Stop all task is running in background
    """
    if _utils.is_task_already():
        _service.stop_bg_process()
        click.echo('Process stopped')
    else:
        click.echo('Process not found')
