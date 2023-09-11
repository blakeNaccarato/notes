"""Paths for this project."""

from pathlib import Path

from boilercore.models import CreatePathsModel
from boilercore.paths import get_package_dir, map_stages
from pydantic import DirectoryPath, FilePath

import notes
from notes import PROJECT_PATH

TEXT_EXPAND_SOURCE = Path(".obsidian/plugins/mrj-text-expand/main.js")


def get_common(root: Path, dirs: list[Path]):
    return [root / dir_.name for dir_ in dirs]


class Paths(CreatePathsModel):
    """Paths associated with project data."""

    # * ROOTS
    # ! Project
    project: DirectoryPath = PROJECT_PATH
    # ! Package
    package: DirectoryPath = get_package_dir(notes)
    # ! Data
    data: DirectoryPath = project / "data"
    external: DirectoryPath = data / "external"
    stages: dict[str, FilePath] = map_stages(package / "stages", package)

    # * GIT-TRACKED
    common: DirectoryPath = data / "common"
    common_dirs: list[DirectoryPath] = list(common.iterdir())  # noqa: RUF012
    obsidian_common: DirectoryPath = data / "obsidian_common"

    # * LOCAL
    local: DirectoryPath = data / "local"
    vaults: DirectoryPath = local / "vaults"
    grad: DirectoryPath = vaults / "grad"
    personal: DirectoryPath = vaults / "personal"
    personal_obsidian: DirectoryPath = personal / ".obsidian"
    grad_obsidian: DirectoryPath = grad / ".obsidian"

    # * Inputs
    grad_timestamped: DirectoryPath = grad / "_timestamped"
    # * Results
    personal_timestamped: DirectoryPath = personal / "_timestamped"

    # * Settings
    settings_sources: list[FilePath] = (  # noqa: PLC3002
        lambda personal_obsidian: [
            personal_obsidian / path
            for path in [
                "app.json",
                "appearance.json",
                "backlink.json",
                "bookmarks.json",
                "canvas.json",
                "community-plugins.json",
                "core-plugins-migration.json",
                "core-plugins.json",
                "daily-notes.json",
                "global-search.json",
                "graph.json",
                "hotkeys.json",
                "note-composer.json",
                "starred.json",
                "templates.json",
                "zk-prefixer.json",
            ]
        ]
    )(personal_obsidian)
    settings_destinations: list[Path] = (  # noqa: PLC3002
        lambda personal_obsidian, grad_obsidian, settings_sources: [
            grad_obsidian / file.relative_to(personal_obsidian)
            for file in settings_sources
        ]
    )(personal_obsidian, grad_obsidian, settings_sources)

    # * Plugin settings
    plugin_settings_sources: list[FilePath] = (  # noqa: PLC3002
        lambda personal_obsidian: [
            personal_obsidian / "plugins" / path / "data.json"
            for path in [
                "dataview",
                "folder-notes",
                "mrj-text-expand",
                "OA-file-hider",
                "obsidian-citation-plugin",
                "obsidian-excalidraw-plugin",
                "obsidian-full-calendar",
                "obsidian-html-plugin",
                "obsidian-link-converter",
                "obsidian-linter",
                "obsidian-outliner",
                "obsidian-pandoc",
                "obsidian-plugin-toc",
                "obsidian-shellcommands",
                "obsidian-zotero-desktop-connector",
                "omnisearch",
                "reference-map",
                "templater-obsidian",
                "text-extractor",
            ]
        ]
    )(personal_obsidian)
    plugin_settings_destinations: list[Path] = (  # noqa: PLC3002
        lambda personal_obsidian, grad_obsidian, plugin_settings_sources: [
            grad_obsidian / file.relative_to(personal_obsidian)
            for file in plugin_settings_sources
        ]
    )(personal_obsidian, grad_obsidian, plugin_settings_sources)

    # * DVC-Tracked Results
    grad_common: list[DirectoryPath] = get_common(grad, common_dirs)
    grad_text_expand_source = grad / TEXT_EXPAND_SOURCE
    personal_common: list[DirectoryPath] = get_common(personal, common_dirs)
    personal_text_expand_source = personal / TEXT_EXPAND_SOURCE
