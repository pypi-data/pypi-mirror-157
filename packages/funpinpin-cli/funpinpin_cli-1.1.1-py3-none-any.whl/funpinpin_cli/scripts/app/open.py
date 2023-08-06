"""Open command."""
import click

from funpinpin_cli.core.app.open import Open
from funpinpin_cli.core.project import proj
from funpinpin_cli.core.util.exception import (
    NotInProjError
)
from ..message import (
    get_open_msg, NOT_IN_PROJ_MSG
)


@click.command("open")
def open():
    """
    \b
    \033[96mopen\033[0m: Open your local development app in the default browser.
      \b
      Usage: \033[96mfunpinpin app open\033[0m
    """
    try:
        open_obj = Open(proj)
        shop, host = open_obj.run()
    except NotInProjError:
        click.echo(NOT_IN_PROJ_MSG)
        return
    except Exception as e:
        click.echo(e)
        return
    msg = get_open_msg(shop, host)
    click.echo(msg)
