"""Notes CLI."""

from datetime import time
from pathlib import Path
from re import sub
from textwrap import dedent

from cappa.base import command
from pydantic import BaseModel, DirectoryPath, Field

from notes.times import current_tz


@command(default_long=True)
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


@command(default_long=True, invoke="notes.pomodouroboros_at_home.main")
class Pom(BaseModel):
    """Start Pomodoros."""

    begin: time = time(hour=9, tzinfo=current_tz)
    end: time = time(hour=17, tzinfo=current_tz)
    allow: list[str] = Field(default_factory=list)
    data: Path | None = None
    event_data: Path | None = None
