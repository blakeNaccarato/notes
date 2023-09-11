"""Paths for this project."""

from itertools import chain
from pathlib import Path

from boilercore.models import CreatePathsModel
from boilercore.paths import get_package_dir, map_stages
from pydantic import DirectoryPath, FilePath

import notes
from notes import PROJECT_PATH

TEXT_EXPAND_SOURCE = Path(".obsidian/plugins/mrj-text-expand/main.js")
"""This is patched externally whenever the plugin is updated."""


def get_common(root: Path, dirs: list[Path]) -> list[Path]:
    """Get directories common to both vaults."""
    return [root / dir_.name for dir_ in dirs]


def get_settings(dot_obsidian: Path) -> list[Path]:
    """Get files in `.obsidian` to be synchronized."""
    plugins = dot_obsidian / "plugins"
    return [
        path
        for path in [
            *[
                path
                for path in dot_obsidian.glob("*.json")
                if path.name not in ["workspace.json", "workspaces.json"]
            ],
            *chain.from_iterable(
                plugins.glob(f"*/*.{extension}") for extension in ["json", "css", "js"]
            ),
        ]
        if path not in [dot_obsidian.parent / TEXT_EXPAND_SOURCE]
    ]


class Paths(CreatePathsModel):
    """Paths associated with project data."""

    # * Roots
    # ! Project
    project: DirectoryPath = PROJECT_PATH
    # ! Package
    package: DirectoryPath = get_package_dir(notes)
    # ! Data
    data: DirectoryPath = project / "data"
    external: DirectoryPath = data / "external"
    stages: dict[str, FilePath] = map_stages(package / "stages", package)

    # * Git-tracked
    common: DirectoryPath = data / "common"
    common_dirs: list[DirectoryPath] = list(common.iterdir())  # noqa: RUF012
    obsidian_common: DirectoryPath = data / "obsidian_common"

    # * Local
    local: DirectoryPath = data / "local"
    # ! Vaults
    vaults: DirectoryPath = local / "vaults"
    grad: DirectoryPath = vaults / "grad"
    personal: DirectoryPath = vaults / "personal"
    # ! .obsidian folders
    grad_obsidian: DirectoryPath = grad / ".obsidian"
    personal_obsidian: DirectoryPath = personal / ".obsidian"
    # ! Inputs
    grad_timestamped: DirectoryPath = grad / "_timestamped"
    # ! Results
    personal_timestamped: DirectoryPath = personal / "_timestamped"
    grad_common: list[DirectoryPath] = get_common(grad, common_dirs)
    personal_common: list[DirectoryPath] = get_common(personal, common_dirs)
    grad_text_expand_source = grad / TEXT_EXPAND_SOURCE
    personal_text_expand_source = personal / TEXT_EXPAND_SOURCE
    # ! Settings
    grad_settings: list[FilePath] = get_settings(grad_obsidian)
    personal_settings: list[FilePath] = get_settings(personal_obsidian)
