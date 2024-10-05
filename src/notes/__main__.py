"""Hash quotes exported from PDFs."""

from hashlib import sha256
from pathlib import Path

from cappa import Subcommands
from cappa.base import command, invoke
from pandas import read_csv
from pydantic import BaseModel


def main():
    """CLI entry-point."""
    invoke(Notes)


@command
class HashQuotes(BaseModel):
    """Hash quotes exported from PDFs."""

    path: Path = Path(
        "data/local/vaults/personal/_sources/zotero/allanBlueskyAheadMultiFacility2019.csv"
    )
    """Path to the CSV file containing the quotes."""

    def __call__(self):
        """Hash quotes exported from PDFs."""
        (
            read_csv(self.path)
            .assign(**{
                "id": lambda df: df["Content"].apply(
                    lambda v: sha256(str(v).encode()).hexdigest()[:8]
                )
            })
            .set_index("id")
            .to_csv(self.path)
        )


@command
class Notes:
    """Notes operations."""

    commands: Subcommands[HashQuotes]


if __name__ == "__main__":
    main()
