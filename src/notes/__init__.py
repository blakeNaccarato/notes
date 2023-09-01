"""Centralized repository of my Obsidian vaults and shared tooling."""

from pathlib import Path

from ruamel.yaml import YAML

PROJECT_PATH = Path()
"""The project directory, where a `params.yaml` file will go."""


def get_yaml():
    """Get a configured YAML parser."""
    yaml = YAML()
    yaml.indent(mapping=(spaces := 2), sequence=spaces, offset=spaces)
    yaml.preserve_quotes = True
    return yaml


yaml = get_yaml()
