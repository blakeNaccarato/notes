"""Centralized repository of my Obsidian vaults and shared tooling."""

from pathlib import Path

PROJECT_PATH = Path()


def get_params_file():
    return PROJECT_PATH / "params.yaml"
