"""Funpinpin cli app serve."""
import os
import re
import click
import requests
from urllib.parse import urljoin

from ..tunnel import Tunnel
from ..util.exception import InvalidHost
from ..project import proj

from funpinpin_cli.scripts.message import get_ngrok_run_msg
from funpinpin_cli.core.util.simple_db import db
from funpinpin_cli.core.util.exception import UpdateAppError
from funpinpin_cli.config import (
    PARTNER_API_URL, APP_REDIRECT_URI
)


class Serve(object):
    """Serve module."""

    def __init__(self, host, port, no_update, **kwargs):
        """Init."""
        self.host = host
        self.port = port
        self.no_update = no_update
        self.project_id = kwargs.get("project_id")
        self.project_name = kwargs.get("project_name")

    def create_tunnel(self):
        """Start ngrok first."""
        try:
            account, url = Tunnel.start(self.port)
        except Exception as e:
            raise e
        msg = get_ngrok_run_msg(account, url)
        click.echo(msg)
        return url

    def update_url(self, url):
        """Update callback url."""
        p_token = db.get("p_token")
        partner_id = db.get("partner_id")
        cookies = {"p_token": p_token}
        callback_url = urljoin(url, "auth/callback")
        partner_url = f"{PARTNER_API_URL}/app/app/{self.project_id}/"
        params = {
            "partner_id": partner_id,
            "url": url,
            "title": self.project_name,
            "redirect_uris": [callback_url, APP_REDIRECT_URI],
        }
        resp = requests.put(
            partner_url, json=params, cookies=cookies
        )
        try:
            rv = resp.json()
        except Exception as e:
            raise UpdateAppError(e)
        return rv

    def generate_url(self):
        """Start tunnel and get url."""
        # run ngrok
        url = self.host or self.create_tunnel()
        m = re.match(r"^https", url)
        if not m:
            raise InvalidHost(
                "HOST must be a HTTPS url."
            )
        env_file = proj.env
        env_file.update("HOST", url)

        # update callback url
        if not self.no_update:
            self.update_url(url)

        return env_file.HOST, env_file.SHOP

    def run(self):
        """Run function."""
        host, shop = self.generate_url()
        return host, shop
