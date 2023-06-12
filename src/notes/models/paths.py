"""Paths for this project."""

from pathlib import Path

from pydantic import DirectoryPath

from notes import DATA_DIR
from notes.models import CreatePathsModel


def get_sorted_paths(path: Path) -> list[Path]:
    """Iterate over a sorted directory."""
    return sorted(path.iterdir())


class Paths(CreatePathsModel):
    """Paths associated with project data."""

    data: DirectoryPath = DATA_DIR
