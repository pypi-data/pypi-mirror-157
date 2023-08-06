"""Connect command."""
import click

from funpinpin_cli.core.app.connect import Connect
from funpinpin_cli.core.project import proj

from ..util import (
    QuestionaryOption, get_organization,
    get_org_shops, get_org_apps
)

from ..message import get_connected_msg

from .validator import (
    validate_org, validate_app, detect_app_connect
)


@click.command("connect")
@click.option(
    "--detect-app",
    is_flag=True,
    callback=detect_app_connect,
    hidden=True
)
@click.option(
    "--organization-id",
    prompt="Select partner organization",
    type=click.Choice(get_organization(), case_sensitive=False),
    cls=QuestionaryOption,
    callback=validate_org,
    hidden=True
)
@click.option(
    "--app-id",
    prompt="Select app",
    type=click.Choice(get_org_apps(), case_sensitive=False),
    cls=QuestionaryOption,
    callback=validate_app,
    hidden=True
)
@click.option(
    "--store-domain",
    prompt="Select store",
    type=click.Choice(get_org_shops(), case_sensitive=False),
    cls=QuestionaryOption,
    hidden=True
)
def connect(detect_app, organization_id, app_id, store_domain):
    """
    \b
    \033[96mconnect\033[0m: Connects an existing app to Funpinpin CLI. Creates a config file.
      \b
      Usage: \033[96mfunpinpin app connect\033[0m
    """

    connect = Connect(
         proj, organization_id, app_id, store_domain
    )
    app_name = connect.run()
    msg = get_connected_msg(app_name)
    click.echo(msg)
