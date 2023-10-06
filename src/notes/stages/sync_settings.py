"""Synchronize settings across vaults if there are no pending changes."""

from contextlib import closing
from copy import deepcopy
from dataclasses import dataclass
from enum import StrEnum, auto
from json import dumps, loads
from pathlib import Path
from shutil import copy
from typing import Any, Literal

import typer
from dulwich.porcelain import status, submodule_list
from dulwich.repo import Repo

from notes.models.params import PATHS


class Source(StrEnum):
    grad = auto()
    personal = auto()


class ChangesPendingError(SystemExit):
    code = 3


def main(source: Source):
    changes = get_changes()
    if changes and any(change.name not in {"dvc.lock"} for change in changes):
        raise ChangesPendingError("Cannot sync settings. There are pending changes.")
    order = copy_grad_settings, copy_personal_settings
    for copy_settings in order if source == "grad" else reversed(order):
        copy_settings()


def copy_grad_settings():
    copy_settings(
        settings=PATHS.grad_settings,
        source_dir=PATHS.grad_obsidian,
        dest_dir=PATHS.personal_obsidian,
        dest_shell_settings_to_postprocess=PATHS.personal_shell_settings,
        dest_repl="personal",
    )


def copy_personal_settings():
    copy_settings(
        settings=PATHS.personal_settings,
        source_dir=PATHS.personal_obsidian,
        dest_dir=PATHS.grad_obsidian,
        dest_shell_settings_to_postprocess=PATHS.grad_shell_settings,
        dest_repl="grad",
    )


def get_changes() -> list[Path]:
    """Get pending changes."""
    staged, unstaged, _ = status(untracked_files="no")
    changes = {
        # Many dulwich functions return bytes for legacy reasons
        Path(path.decode("utf-8")) if isinstance(path, bytes) else path
        for change in (*staged.values(), unstaged)
        for path in change
    }
    # Exclude submodules from the changeset (submodules are considered always changed)
    return sorted(
        change
        for change in changes
        if change not in {submodule.path for submodule in get_submodules()}
    )


@dataclass
class Submodule:
    """Represents a git submodule."""

    _path: str | bytes
    """Submodule path as reported by the submodule source."""
    commit: str
    """Commit hash currently tracked by the submodule."""
    path: Path = Path()
    """Submodule path."""
    name: str = ""
    """Submodule name."""

    def __post_init__(self):
        """Handle byte strings reported by some submodule sources, like dulwich."""
        # Many dulwich functions return bytes for legacy reasons
        self.path = Path(
            self._path.decode("utf-8") if isinstance(self._path, bytes) else self._path
        )
        self.name = self.path.name


def get_submodules() -> list[Submodule]:
    """Get the special template and typings submodules, as well as the rest."""
    with closing(repo := Repo(str(Path.cwd()))):
        return [Submodule(*item) for item in list(submodule_list(repo))]


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
    shell_settings: dict[str, Any], i: int, source: Literal["grad", "personal"]
) -> dict[str, Any]:
    """Return a copy of the dictionary with an updated command."""
    destination = "grad" if source == "personal" else "personal"
    shell_settings = deepcopy(shell_settings)
    shell_settings["shell_commands"][i]["platform_specific_commands"]["default"] = (
        # fmt: off
         "Set-Location ../../../.."
         " && Set-PsEnv"
        f" && dvc repro sync_{source}_settings sync_{destination}_settings"
         " && git add -A"
        f" && git commit -m 'Sync {source} settings to {destination} settings'"
         " && git push"
        # fmt: on
    )
    return shell_settings


if __name__ == "__main__":
    typer.run(main)
