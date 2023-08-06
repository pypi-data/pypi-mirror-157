"""Extension validator."""
import click

from funpinpin_cli.core.project import proj


def verify_project_type(ctx, proj_type):
    """Verify project type."""
    if proj_type != proj.current_project_type:
        click.echo(
            f"This command can only be run within {proj_type} projects."
        )
        ctx.exit()
