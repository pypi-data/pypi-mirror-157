"""Funpinpin cli app connect."""
import requests
from funpinpin_cli.core.util.simple_db import db
from funpinpin_cli.core.env_file import EnvFile
from funpinpin_cli.config import PARTNER_API_URL


class Connect(object):
    """Connect module."""

    def __init__(self, proj, organization_id, app_id, domain):
        """Init."""
        self.proj = proj
        self.project_type = proj.current_project_type()
        self.organization_id = organization_id
        self.app_id = app_id
        self.domain = domain

    def default_connect(self):
        """Connect app."""
        api_client = self.get_app_by_id()
        client_id = api_client["client_id"]
        client_secret = api_client["client_secret"]
        shop = self.domain
        scopes = api_client["scopes"]
        EnvFile(client_id, client_secret, shop, scopes).write()
        self.write_cli_yml()
        return api_client["name"]

    def write_cli_yml(self):
        """Write app yml."""
        self.proj.write({
            "project_type": self.project_type,
            "organization_id": self.organization_id,
            "project_id": int(self.app_id)
        })
        print(".funpinpin-cli.yml saved to project root")

    def get_app_by_id(self):
        """Get app by id."""
        p_token = db.get("p_token")
        cookies = {"p_token": p_token}
        url = f"{PARTNER_API_URL}/app/app/{self.app_id}/?"
        params = {
            "partner_id": self.organization_id,
        }
        resp = requests.get(
            url, params=params, cookies=cookies
        )
        if resp.status_code != 200:
            return None
        rv = resp.json()
        return rv

    def run(self):
        """Run function."""
        return self.default_connect()
