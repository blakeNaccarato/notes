"""Update files common to all vaults."""

from shutil import copytree

from notes.models.params import PATHS


def main():
    copytree(PATHS.common, PATHS.personal, dirs_exist_ok=True)
    copytree(PATHS.obsidian_common, PATHS.personal_obsidian, dirs_exist_ok=True)


if __name__ == "__main__":
    main()
