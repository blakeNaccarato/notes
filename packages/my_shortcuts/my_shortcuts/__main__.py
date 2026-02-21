"""Main program."""

from cappa import invoke

from my_shortcuts.cli import MyShortcuts


def main():
    invoke(MyShortcuts)


if __name__ == "__main__":
    main()
