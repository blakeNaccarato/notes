from pathlib import Path
from shutil import copy

DESTINATION = Path("data/obsidian_common_json_destination")
COMMON_SETTINGS = Path("data/obsidian_common_json")
SETTINGS = [
    *[
        COMMON_SETTINGS / path
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
    ],
    *[
        COMMON_SETTINGS / "plugins" / path / "data.json"
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
    ],
]

for file in SETTINGS:
    copy(file, DESTINATION / file.relative_to(COMMON_SETTINGS))
