"""Synchronize settings across vaults if there are no pending changes."""

from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from shutil import copy

from dulwich.porcelain import status, submodule_list
from dulwich.repo import Repo
from typer import Typer

from notes.models.params import PATHS

app = Typer()

ALLOWED_CHANGES = [
    Path(path)
    for path in ["dvc.lock", "params.yaml", "requirements/requirements_dev.txt"]
]
"""These files have CRLF line endings or some other issue that we can't control."""


@app.command()
def main():  # noqa: D103
    changes = get_changes()
    if changes and any(change not in ALLOWED_CHANGES for change in changes):
        raise ChangesPendingError("Cannot sync settings. There are pending changes.")
    copy_settings(
        settings=PATHS.personal_settings,
        source_dir=PATHS.personal_obsidian,
        dest_dir=PATHS.amsl_obsidian,
    )


class ChangesPendingError(Exception): ...  # noqa: D101


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
    """Get submodules."""
    with closing(repo := Repo(str(Path.cwd()))):
        return [Submodule(*item) for item in list(submodule_list(repo))]


def copy_settings(settings: list[Path], source_dir: Path, dest_dir: Path):
    """Copy settings from one vault to another."""
    for source_file in settings:
        destination_file = dest_dir / source_file.relative_to(source_dir)
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        copy(source_file, destination_file)


if __name__ == "__main__":
    app()
