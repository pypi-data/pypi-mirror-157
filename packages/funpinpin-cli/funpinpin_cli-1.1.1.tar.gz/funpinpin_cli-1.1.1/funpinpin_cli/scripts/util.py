"""scripts utils."""
import click
import requests
import questionary
from funpinpin_cli.core.util.simple_db import db
from funpinpin_cli.core.login import Login
from funpinpin_cli.config import PARTNER_API_URL


class QuestionaryOption(click.Option):
    """Questionary option."""

    def __init__(self, param_decls=None, **attrs):
        """Init."""
        click.Option.__init__(self, param_decls, **attrs)
        if not isinstance(self.type, click.Choice):
            raise Exception(
                'ChoiceOption type arg must be click.Choice'
            )

    def prompt_for_value(self, ctx):
        """Select item."""
        val = questionary.select(
            self.prompt, choices=self.type.choices
        ).unsafe_ask()
        return val


def get_organization():
    """Get organization."""
    info = f"{db.get('partner_name')} ({db.get('partner_id')})"
    return [info]


def get_org_shops():
    """Get shops for questionary to select."""
    p_token = db.get("p_token")
    if not p_token:
        return []
    shops = Login.get_sandbox_shop(p_token)
    return shops


def get_org_apps():
    """Get apps by org_id for questionary to select."""
    p_token = db.get("p_token")
    if not p_token:
        return []
    partner_id = db.get("partner_id")
    partner_name = db.get("partner_name")
    cookies = {"p_token": p_token}
    url = f"{PARTNER_API_URL}/app/app/"
    params = {
        "partner_id": partner_id,
        "page": 1,
        "limit": 200
    }
    resp = requests.get(url, params=params, cookies=cookies)
    if resp.status_code != 200:
        return []
    rv = resp.json()
    if rv.get("total", 0) <= 0:
        return []
    s_apps = [f"{item['name']} ({item['id']})" for item in rv.get("data", [])]
    return s_apps
