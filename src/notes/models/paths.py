"""Paths for this project."""

from itertools import chain
from pathlib import Path

from boilercore.models import CreatePathsModel
from boilercore.paths import get_package_dir, map_stages
from pydantic.v1 import DirectoryPath, FilePath

import notes
from notes import PROJECT_PATH


def get_common(root: Path, dirs: list[Path]) -> list[Path]:
    """Get directories common to both vaults."""
    return [root / dir_.name for dir_ in dirs]


def get_settings(dot_obsidian: Path) -> list[Path]:
    """Get files in `.obsidian` to be synchronized.

    Looks for `json`, `css`, and `js` files in `.obsidian` and immediate folders.
    Because of this, plugin subfolders (such as text extractor caches) are not synced.
    This is sensible as long as plugin subfolders contain caches and other
    vault-specific items.
    """
    return [
        *[
            path
            for path in dot_obsidian.glob("*.json")
            if path.name not in ["workspace.json", "workspaces.json"]
        ],
        *(dot_obsidian / "snippets").glob("*.css"),
        *chain.from_iterable(
            (dot_obsidian / "plugins").glob(f"*/*.{extension}")
            for extension in ["json", "css", "js"]
        ),
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
    stages: dict[str, FilePath] = map_stages(package / "stages")

    # * Git-tracked
    obsidian_common: DirectoryPath = data / "obsidian_common"
    # * Local
    local: DirectoryPath = data / "local"
    # ! Vaults
    vaults: DirectoryPath = local / "vaults"
    personal: DirectoryPath = vaults / "personal"
    # ! .obsidian folders
    personal_obsidian: DirectoryPath = personal / ".obsidian"
    personal_plugins: DirectoryPath = personal_obsidian / "plugins"
    # ! Inputs
    personal_links: DirectoryPath = personal / "_sources/links"
    # ! Results
    personal_timestamped: Path = personal / "_timestamped"
    # ! Settings
    personal_settings: list[Path] = get_settings(personal_obsidian)

    # * AMSL
    amsl: Path = vaults / "amsl"
    amsl_obsidian: Path = amsl / ".obsidian"
    amsl_plugins: Path = amsl_obsidian / "plugins"
    amsl_settings: list[Path] = get_settings(amsl_obsidian)
