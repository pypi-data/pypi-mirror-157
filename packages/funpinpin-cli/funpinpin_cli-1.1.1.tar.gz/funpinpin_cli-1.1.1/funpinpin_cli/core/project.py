"""Capture the current project that the user is working on."""
import os
import re

import pathlib
import yaml

from .env_file import EnvFile

from funpinpin_cli.core.util.exception import (
    YamlDataError, NotInProjError
)


class Project(object):
    """Project module."""

    config_name = ".funpinpin-cli.yml"

    def __init__(self):
        """Init."""
        self._at = self._dir = None

    def clear(self):
        """Clear."""
        self._at = self._dir = None

    def current(self, force_reload=False):
        """Get current project directory."""
        if force_reload:
            self.clear()
        return self.at(os.getcwd())

    def has_current(self):
        """Whether user in project directory."""
        if self.directory(os.getcwd()):
            return True
        return False

    def at(self, dir):
        """Get current project directory."""
        proj_dir = self.directory(dir)
        if not proj_dir:
            raise NotInProjError("not in a valid project directory.")
        if not self._at:
            self._at = {
                proj_dir: dir
            }
        return self._at.get(proj_dir)

    def directory(self, dir):
        """Get current project directory."""
        if not self._dir:
            self._dir = {
                dir: self.__directory(dir)
            }
        return self._dir.get(dir)

    def __directory(self, curr):
        while True:
            if curr == "/" or re.match(r"^[A-Z]:\/$", curr):
                return None
            yaml_file = os.path.join(curr, Project.config_name)
            if pathlib.Path(yaml_file).exists():
                return curr
            curr = os.path.dirname(curr)

    def current_project_type(self):
        """Get the current project type."""
        if self.has_current():
            config = load_yaml_file(
                self.directory(
                    os.getcwd()
                ),
                Project.config_name
            )
            return config.get("project_type")
        return None

    def current_project_id(self):
        """Get the current project id."""
        if self.has_current():
            config = load_yaml_file(
                self.directory(
                    os.getcwd()
                ),
                Project.config_name
            )
            return config.get("project_id")
        return None

    def current_project_name(self):
        """Get the current project name."""
        if self.has_current():
            return os.path.basename(
                self.directory(os.getcwd())
            )
        return None

    def write(self, data):
        """Write project configuration."""
        with open(Project.config_name, "w") as fd:
            yaml.dump(
                data, fd,
                # default_flow_style=False
            )
        self.clear()

    @property
    def env(self):
        """Get project env."""
        proj_dir = self.directory(os.getcwd())
        if not proj_dir:
            raise NotInProjError("not in a valid project directory.")
        try:
            env_file = EnvFile.read(proj_dir)
        except FileNotFoundError:
            return None
        return env_file


proj = Project()


def load_yaml_file(directory, relative_path):
    """Load yaml file.

    Args:
        directory: project directory
        relative_path: yaml file
    """
    yaml_path = os.path.join(directory, relative_path)
    try:
        with open(yaml_path) as fd:
            config = yaml.safe_load(fd)
    except Exception as e:
        raise(e)

    if not isinstance(config, dict):
        raise YamlDataError("Yaml data is not dict.")
    return config
