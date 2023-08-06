"""Create command."""
import click

from funpinpin_cli.core.app import Node
from funpinpin_cli.core.util.exception import CmdNotFound

from ..util import (
    QuestionaryOption, get_organization, get_org_shops
)

from ..message import (
    get_app_create_msg, NODE_INSTALL_MSG, NPM_INSTALL_MSG
)

from .validator import (
    validate_name, validate_type, validate_org
)


@click.command("node")
@click.option(
    "--name",
    prompt="? App name",
    callback=validate_name,
    help="App name. Any string."
)
@click.option(
    "--type",
    prompt="What type of app are you building?",
    type=click.Choice(
        [
            "Public: An app built for a wide merchant audience.",
            # "Custom: An app custom built for a single client."
        ],
        case_sensitive=False
    ),
    cls=QuestionaryOption,
    callback=validate_type,
    help="Partner organization ID. Must be an existing organization."
)
@click.option(
    "--organization-id",
    prompt="Select partner organization",
    type=click.Choice(get_organization(), case_sensitive=False),
    cls=QuestionaryOption,
    callback=validate_org,
    help="Partner organization ID. Must be an existing organization."
)
@click.option(
    "--store-domain",
    prompt="Select store",
    type=click.Choice(get_org_shops(), case_sensitive=False),
    cls=QuestionaryOption,
    help="Development store URL. Must be an existing development store."
)
@click.option(
    "--verbose", is_flag=True
)
def node(name, type, organization_id, store_domain, verbose):
    """
    \b
    \033[96mnode\033[0m: Creates an embedded nodejs app.
      Usage: \033[96mfunpinpin app create node\033[0m

      Options:
        \033[96m--name=NAME\033[0m App name. Any string.
        \033[96m--organization-id=ID\033[0m Partner organization ID. Must be an existing organization.
        \033[96m--store-domain=MYFUNPINPINDOMAIN\033[0m  Development store URL. Must be an existing development store.
    """
    try:
        node = Node(name, type, organization_id, store_domain)
        api_client = node.run(verbose)
    except Exception as e:
        if hasattr(e, 'name'):
            if e.name == "node":
                msg = NODE_INSTALL_MSG
            elif e.name == "npm":
                msg = NPM_INSTALL_MSG
        else:
            msg = e
        click.echo(msg)
        return
    msg = get_app_create_msg(store_domain, name, api_client)
    click.echo(msg)
