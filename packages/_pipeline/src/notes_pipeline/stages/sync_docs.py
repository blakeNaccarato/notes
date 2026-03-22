"""Sync docs."""

from shutil import copy

from notes_pipeline.models.params import PATHS


def main():  # noqa: D103
    copy(PATHS.set_up_amsl_obsidian_note, PATHS.set_up_amsl_obsidian_docs)


if __name__ == "__main__":
    main()
