"""Update files common to all vaults."""

from enum import StrEnum, auto
from pathlib import Path
from shutil import copy

import typer

from notes.models.params import PATHS


class Source(StrEnum):
    grad = auto()
    personal = auto()


def main(source: Source):
    if source == "grad":
        copy_settings(PATHS.grad_settings, PATHS.grad_obsidian, PATHS.personal_obsidian)
    elif source == "personal":
        copy_settings(
            PATHS.personal_settings, PATHS.personal_obsidian, PATHS.grad_obsidian
        )


def copy_settings(settings: list[Path], source: Path, destination: Path):
    for source_file in settings:
        destination_file = destination / source_file.relative_to(source)
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        copy(source_file, destination_file)


if __name__ == "__main__":
    typer.run(main)
