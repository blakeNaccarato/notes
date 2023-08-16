"""Update files common to all vaults."""

from shutil import copytree

from notes.models.params import PARAMS


def main():
    for destination in [PARAMS.paths.grad, PARAMS.paths.personal]:
        copytree(PARAMS.paths.common, destination, dirs_exist_ok=True)
        copytree(
            PARAMS.paths.obsidian_common, destination / ".obsidian", dirs_exist_ok=True
        )


if __name__ == "__main__":
    main()
