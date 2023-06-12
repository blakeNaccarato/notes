"""Update files common to all vaults."""

from shutil import copytree

from notes.models.params import PARAMS


def main():
    copytree(PARAMS.paths.common, PARAMS.paths.grad, dirs_exist_ok=True)
    copytree(PARAMS.paths.common, PARAMS.paths.personal, dirs_exist_ok=True)


if __name__ == "__main__":
    main()
