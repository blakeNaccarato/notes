"""Update files common to all vaults."""

from copy import deepcopy
from enum import StrEnum, auto
from json import dumps, loads
from pathlib import Path
from shutil import copy
from typing import Any, Literal

import typer

from notes.models.params import PATHS


class Source(StrEnum):
    grad = auto()
    personal = auto()


def main(source: Source):
    if source == "grad":
        copy_settings(
            settings=PATHS.grad_settings,
            source_dir=PATHS.grad_obsidian,
            dest_dir=PATHS.personal_obsidian,
            dest_shell_settings_to_postprocess=PATHS.personal_shell_settings,
            dest_repl="personal",
        )
    elif source == "personal":
        copy_settings(
            settings=PATHS.personal_settings,
            source_dir=PATHS.personal_obsidian,
            dest_dir=PATHS.grad_obsidian,
            dest_shell_settings_to_postprocess=PATHS.grad_shell_settings,
            dest_repl="grad",
        )


def copy_settings(
    settings: list[Path],
    source_dir: Path,
    dest_dir: Path,
    dest_shell_settings_to_postprocess: Path,
    dest_repl: Literal["grad", "personal"],
):
    """Copy settings from one vault to another."""
    for source_file in settings:
        destination_file = dest_dir / source_file.relative_to(source_dir)
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        copy(source_file, destination_file)
    repl_shell_settings(dest_shell_settings_to_postprocess, dest_repl)


def repl_shell_settings(
    shell_settings_file: Path,
    replacement: Literal["grad", "personal"],
):
    """Update the vault-specific shell command after sync."""
    shell_settings = loads(shell_settings_file.read_text(encoding="utf-8"))
    for i, cmd in enumerate(shell_settings["shell_commands"]):
        if cmd["id"] == "ec1o3s5qeo":
            shell_settings = update_command(shell_settings, i, replacement)
    shell_settings_file.write_text(
        encoding="utf-8", data=dumps(shell_settings, indent=4)
    )


def update_command(
    shell_settings: dict[str, Any], i: int, replacement: Literal["grad", "personal"]
) -> dict[str, Any]:
    """Return a copy of the dictionary with an updated command."""
    if replacement == "grad":
        command_order = "sync_grad_settings sync_personal_settings"
    elif replacement == "personal":
        command_order = "sync_personal_settings sync_grad_settings"
    shell_settings = deepcopy(shell_settings)
    shell_settings["shell_commands"][i]["platform_specific_commands"]["default"] = (
        # fmt: off
         "Set-Location ../../../.."
         " && Set-PsEnv"
        f" && dvc repro {command_order}"
        f" && git commit -m 'Update {replacement} settings'"
         " && git push"
        # fmt: on
    )
    return shell_settings


if __name__ == "__main__":
    typer.run(main)