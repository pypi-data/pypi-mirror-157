"""Serve command."""
import os
import click

from funpinpin_cli.core.app.serve import Serve
from funpinpin_cli.core.project import proj
from funpinpin_cli.core.util.exception import (
    NotInProjError, UpdateAppError
)
from ..message import (
    NOT_VERIFIED_SHOP_MSG, NOT_IN_PROJ_MSG, get_app_serve_msg,
    get_ngrok_108_msg, get_ngrok_107_msg
)
from .validator import detect_app


@click.command("serve")
@click.option(
    "--detect-app",
    is_flag=True,
    callback=detect_app,
    hidden=True
)
@click.option(
    "--host",
    default="",
)
@click.option("--port", type=int)
@click.option("--no-update", is_flag=True)
def serve(detect_app, host, port, no_update):
    """
    \b
    \033[96mserve\033[0m: Start a local development server for your project, as well as a public ngrok tunnel to your localhost.
      \b
      Usage: \033[96mfunpinpin app serve\033[0m
      \b
      Options:
        \033[96m--host=HOST\033[0m: Bypass running tunnel and use custom host. HOST must be HTTPS url.
        \033[96m--port=PORT\033[0m: Use custom port.
        \033[96m--no-update\033[0m: Skips the dashboard URL update step
    """
    try:
        env_file = proj.env
    except NotInProjError:
        click.echo(NOT_IN_PROJ_MSG)
        return

    if not env_file.SHOP:
        click.echo(NOT_VERIFIED_SHOP_MSG)
        return

    project_info = dict(
        project_id=proj.current_project_id(),
        project_name=proj.current_project_name()
    ) if not no_update else dict()
    try:
        serve = Serve(
            host, port, no_update, **project_info
        )
        host, shop = serve.run()
    except UpdateAppError as e:
        click.echo(e)
        return
    except Exception as e:
        e_str = str(e)
        if "ERR_NGROK_107" in e_str:
            click.echo(get_ngrok_107_msg())
        elif "ERR_NGROK_108" in e_str:
            click.echo(get_ngrok_108_msg())
        else:
            click.echo(e_str)
        return

    msg = get_app_serve_msg(host, env_file.SHOP)
    click.echo(msg)

    # run app
    cmd = ("npm run dev")
    os.system(cmd)
