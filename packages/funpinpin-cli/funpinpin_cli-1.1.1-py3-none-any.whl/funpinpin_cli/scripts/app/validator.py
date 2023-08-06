"""App validator."""
import os
import re
import subprocess
import pathlib

import click

from funpinpin_cli.core.util.simple_db import db
from funpinpin_cli.core.project import Project, load_yaml_file, proj
from funpinpin_cli.core.util.exception import (
    MissingCliYml, NotInProjError
)
from ..message import (
    APP_AUTHENTICATED_ERROR_MSG, get_missing_yml_msg,
    get_type_not_found_msg, get_invalid_type_msg,
    CONNECT_PROD_WARNING, NOT_IN_PROJ_MSG,
    ALREADY_CONNECTED_WARNING
)


def verify_authorized(ctx):
    """Verify if login."""
    p_token = db.get("p_token")
    if not p_token:
        click.echo(APP_AUTHENTICATED_ERROR_MSG)
        ctx.exit()


def validate_name(ctx, param, value):
    """Replace space with underscode."""
    formatted_name = "_".join(value.lower().split(" "))
    return formatted_name


def validate_type(ctx, param, value):
    """Verify app type."""
    value_l = value.lower()
    if value_l.startswith(("public", "custom")):
        return value_l[:6]
    click.echo(f"INVALID_APP_TYPE {value}")
    ctx.exit()


def validate_org(ctx, param, value):
    """Verify organization_id."""
    pattern = r".*[(](\d+?)[)]"
    m = re.search(pattern, value)
    return int(m.group(1))


def validate_host(ctx, param, value):
    """Verify host."""
    pattern = r"^https"
    m = re.match(pattern, value)
    if not m:
        click.echo("HOST must be a HTTPS url.")
        ctx.exit()
    return value


def validate_port(ctx, param, value):
    """Validate port."""
    if value < 0:
        click.echo(f"{value} is not a valid port.")
        ctx.exit()
    return value


def verify_git(ctx):
    """Verify if git is available."""
    msg = (
        "Git needs to be installed: " +
        click.style("https://git-scm.com/download", underline=True)
    )
    try:
        cp = subprocess.run(
            ["git", "version"], capture_output=True
        )
    except Exception:
        click.echo(msg)
        ctx.exit()

    if cp.returncode != 0:
        click.echo(msg)
        ctx.exit()


def validate_app(ctx, param, value):
    """Validate app."""
    if not value:
        click.echo("Couldn't find a valid development app, please create one.")
        ctx.exit()
    pattern = r".*[(](\d+?)[)]"
    m = re.search(pattern, value)
    return int(m.group(1))


def detect_app(ctx, params, value):
    """Detect app by .funpinpin-cli.yml."""
    # check .funpinpin-cli.yml
    curr_dir = os.getcwd()
    yaml_file = os.path.join(curr_dir, Project.config_name)
    if not pathlib.Path(yaml_file).exists():
        msg = get_missing_yml_msg(curr_dir, Project.config_name)
        click.echo(msg)
        ctx.exit()
    config = load_yaml_file(curr_dir, Project.config_name)
    project_type = config.get("project_type")
    if project_type is None:
        msg = get_type_not_found_msg(curr_dir)
        click.echo(msg)
        ctx.exit()
    elif project_type not in ("node", "rails", "php"):
        msg = get_invalid_type_msg(project_type)
        click.echo(msg)
        ctx.exit()
    else:
        return value


def detect_app_connect(ctx, params, value):
    """Detect app by .funpinpin-cli.yml and env."""
    # check .funpinpin-cli.yml
    curr_dir = os.getcwd()
    yaml_file = os.path.join(curr_dir, Project.config_name)
    if not pathlib.Path(yaml_file).exists():
        msg = get_missing_yml_msg(curr_dir, Project.config_name)
        click.echo(msg)
        ctx.exit()
    config = load_yaml_file(curr_dir, Project.config_name)
    project_type = config.get("project_type")
    if project_type is None:
        msg = get_type_not_found_msg(curr_dir)
        click.echo(msg)
        ctx.exit()
    elif project_type not in ("node", "rails", "php"):
        msg = get_invalid_type_msg(project_type)
        click.echo(msg)
        ctx.exit()

    # check current directory
    try:
        proj.current()
    except NotInProjError:
        click.echo(NOT_IN_PROJ_MSG)

    # check .env
    try:
        if proj.env:
            click.echo(CONNECT_PROD_WARNING)
            click.echo(ALREADY_CONNECTED_WARNING)
    except NotInProjError:
        return value
    return value
