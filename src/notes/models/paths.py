"""Paths for this project."""

from itertools import chain
from pathlib import Path

from pydantic import BaseModel, FilePath

import notes
from notes import PROJECT_PATH


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


class Paths(BaseModel):
    """Paths associated with project data."""

    # * Roots
    # ! Project
    project: Path = PROJECT_PATH
    # ! Package
    package: Path = Path(notes.__spec__.submodule_search_locations[0])
    # ! Data
    data: Path = project / "data"
    stages: dict[str, FilePath] = (  # noqa: PLC3002
        lambda package: {
            stage: package / "stages" / f"{stage}.py"
            for stage in ["sanitize_source_tags", "sync_settings"]
        }
    )(package)

    # * Git-tracked
    # * Local
    local: Path = data / "local"
    # ! Vaults
    vaults: Path = local / "vaults"
    personal: Path = vaults / "personal"
    # ! .obsidian folders
    personal_obsidian: Path = personal / ".obsidian"
    personal_plugins: Path = personal_obsidian / "plugins"
    # ! Inputs
    personal_links: Path = personal / "_sources/links"
    # ! Results
    personal_timestamped: Path = personal / "_timestamped"
    # ! Settings
    personal_settings: list[Path] = get_settings(personal_obsidian)

    # * AMSL
    amsl: Path = vaults / "amsl"
    amsl_obsidian: Path = amsl / ".obsidian"
    amsl_plugins: Path = amsl_obsidian / "plugins"
    amsl_settings: list[Path] = get_settings(amsl_obsidian)
