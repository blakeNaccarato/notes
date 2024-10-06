"""Hash quotes exported from PDFs."""

from hashlib import sha256
from pathlib import Path
from re import sub
from textwrap import dedent

from cappa import Subcommands
from cappa.base import command, invoke
from pandas import read_csv
from pydantic import BaseModel, DirectoryPath, FilePath


def main():
    """CLI entry-point."""
    invoke(Notes)


@command
class AssociatePdfs(BaseModel):
    """Associate literature notes with PDFs."""

    path: DirectoryPath = Path("data/local/vaults/personal/_notes/zotero")
    """Path to literature notes."""

    def __call__(self):
        """Associate literature notes with PDFs."""
        for file in self.path.glob("*.md"):
            pdf = f'pdf: "[[_sources/zotero/{file.stem}.pdf|{file.stem}]]"'
            contents = file.read_text(encoding="utf-8")
            if "pdf:" in contents and pdf not in contents:
                raise ValueError(f"Note `{file.name}` has unexpected PDF link.")
            if pdf in contents:
                continue
            file.write_text(
                encoding="utf-8",
                data=sub(
                    dedent(
                        r"""
                        ---
                        """
                    ),
                    dedent(
                        f"""
                        {pdf}
                        ---
                        """
                    ),
                    contents,
                ),
            )


@command
class CleanQuotes(BaseModel):
    """Clean and hash quotes exported from PDFs."""

    path: FilePath = Path(
        "data/local/vaults/personal/_sources/zotero/allanBlueskyAheadMultiFacility2019.csv"
    )
    """Path to the CSV file containing the quotes."""

    def __call__(self):
        """Hash quotes exported from PDFs."""

        class QuotesCols(BaseModel):
            """Columns of the quotes CSV file."""

            id: str = "id"
            """Hash of quote's content."""
            content: str = "Content"
            """Quote's content."""
            page: str = "Page"
            """Page the quote is on."""

        c = QuotesCols()

        (
            read_csv(self.path)
            .assign(**{
                c.content: lambda df: df[c.content].apply(
                    lambda v: str(v).replace("\n", " ").strip()
                ),
                c.id: lambda df: df[c.content].apply(
                    lambda v: sha256(str(v).encode()).hexdigest()[:8]
                ),
            })
            .set_index("id")
            .to_csv(self.path)
        )


@command
class Notes:
    """Notes operations."""

    commands: Subcommands[AssociatePdfs | CleanQuotes]


if __name__ == "__main__":
    main()
