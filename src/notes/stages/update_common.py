"""Update files common to all vaults."""

from shutil import copytree

from notes.models.params import PATHS


def main():
    for destination in [PATHS.grad, PATHS.personal]:
        copytree(PATHS.common, destination, dirs_exist_ok=True)
    for destination in [PATHS.grad_obsidian, PATHS.personal_obsidian]:
        copytree(PATHS.obsidian_common, destination, dirs_exist_ok=True)


if __name__ == "__main__":
    main()
