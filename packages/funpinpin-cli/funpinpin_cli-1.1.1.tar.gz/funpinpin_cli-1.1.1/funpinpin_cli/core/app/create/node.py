"""Funpinpin cli app create node."""
import os
import pathlib
import subprocess
import requests

from funpinpin_cli.config import (
    PARTNER_API_URL, APP_REDIRECT_URI
)
from funpinpin_cli.core.util.context import (
    which, get_current_platform
)
from funpinpin_cli.core.util.simple_db import db
from funpinpin_cli.core.util.exception import (
    CmdNotFound, CreateAppError
)
from funpinpin_cli.core.project import proj
from funpinpin_cli.core.env_file import EnvFile


class Node(object):
    """Node module."""

    default_app_url = "http://localhost"
    GIT_TEMPLATE_URL = "https://github.com/FunPinPin-support/app-template-node.git"

    def __init__(self, name, type, org_id, domain):
        """Init."""
        self.name = name
        self.type = type
        self.org_id = org_id
        self.domain = domain

    @classmethod
    def check_prereq_command(cls, cmd):
        """Check if cmd is installed."""
        try:
            ext = ".exe" if get_current_platform() == "windows" else ""
            cmd_path = which(cmd[0], default_ext=ext)
            exe_file = pathlib.Path(cmd_path).parts[-1]
            cmd = [exe_file] + cmd[1:]
            cp = subprocess.run(cmd, capture_output=True)
        except Exception as e:
            raise CmdNotFound(cmd[0], e)

        if cp.returncode != 0:
            raise CmdNotFound(cmd[0], cp.stderr.decode().strip())

        v = str(cp.stdout.decode().strip())

        print(f"{cmd[0]} {v}")

    def run(self, verbose=False):
        """Node create."""
        # checkout node and npm.
        Node.check_prereq_command(["node", "--version"])
        Node.check_prereq_command(["npm", "--version"])

        # pull node template.
        self.build(verbose)

        # save app information.
        api_client = self.create_client()
        client_id = api_client["client_id"]
        client_secret = api_client["client_secret"]
        shop = self.domain
        scopes = api_client["scopes"]
        proj.write({
            "project_type": "node", "organization_id": self.org_id,
            "project_id": int(api_client["id"])
        })
        EnvFile(client_id, client_secret, shop, scopes).write()

        return api_client

    @classmethod
    def install_deps(cls, verbose):
        """Install dependencies."""
        cmd = "npm install --no-audit --force"
        if not verbose:
            cmd += " --quiet --silent"
        os.system(cmd)

    def build(self, verbose):
        """Clone Node template from git."""
        cmd = f"git clone {Node.GIT_TEMPLATE_URL} {self.name}"
        print(f"Cloning {Node.GIT_TEMPLATE_URL} into {self.name}…")
        os.system(cmd)
        root = os.path.join(os.getcwd(), self.name)
        os.chdir(root)
        cmd = "npm --userconfig .npmrc config set @funpinpin:registry https://registry.yarnpkg.com"
        os.system(cmd)

        # npm install and yarn install
        print("Installing dependencies with npm…")
        Node.install_deps(verbose)
        print("Dependencies installed")

        os.system(f"rm -rf {os.path.join(root, '.git')} > /dev/null")
        os.system(f"rm -rf {os.path.join(root, '.github')} > /dev/null")
        pathlib.Path(
            os.path.join(root, "server", "handlers", "client.js")
        ).unlink(missing_ok=True)

    def create_client(self):
        """Create api client."""
        p_token = db.get("p_token")
        cookies = {"p_token": p_token}
        url = f"{PARTNER_API_URL}/app/app/"
        params = {
            "partner_id": self.org_id,
            "title": self.name,
            "redirect_uris": [APP_REDIRECT_URI],
            "url": Node.default_app_url
        }
        resp = requests.post(
            url, json=params, cookies=cookies
        )
        try:
            rv = resp.json()
        except Exception as e:
            raise CreateAppError(e)
        return rv
