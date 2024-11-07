"""Hash quotes exported from PDFs."""

from pathlib import Path
from re import sub
from textwrap import dedent

from cappa import Subcommands
from cappa.base import command, invoke
from pydantic import BaseModel, DirectoryPath


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
class Notes:
    """Notes operations."""

    commands: Subcommands[AssociatePdfs]


if __name__ == "__main__":
    main()
