"""Hash quotes exported from PDFs."""

from cappa import Subcommands
from cappa.base import command, invoke

from notes.cli import AssociatePdfs, Pom


def main():
    """CLI entry-point."""
    invoke(Notes)


@command
class Notes:
    """Notes operations."""

    commands: Subcommands[AssociatePdfs | Pom]


if __name__ == "__main__":
    main()
