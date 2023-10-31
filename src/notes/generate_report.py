"""Generate a report."""

from contextlib import chdir
from os import walk
from pathlib import Path
from re import MULTILINE, compile
from shlex import join, quote, split
from subprocess import run


def main():
    vault_root = Path("C:/Users/Blake/Code/mine/notes/data/local/vaults/grad")
    report_as_docx(
        text=report(root=vault_root / "projects"),
        destination=Path("C:/Users/Blake/Desktop/report.docx"),
        template=Path("C:/Users/Blake/Code/mine/boilercv/data/scripts/template.dotx"),
        workdir=vault_root,
    )


def report(root: Path) -> str:
    """Report in combined Markdown from a folder of possibly nested Markdown files."""
    text = ""
    for folder, _, files in walk(root):
        for file in sorted(Path(folder) / f for f in files if f.endswith(".md")):
            text += f"\n{indent_from_root(file, root)}"
    return text


def indent_from_root(file: Path, root: Path) -> str:
    """Indent Markdown headings in `file` based on their depth relative to `root`."""
    depth = len(file.relative_to(root).parts) - (1 if "_" in file.stem else 0)
    return f"\n{indent_headings(file.read_text(encoding='utf-8'), depth)}"


def indent_headings(text: str, repeat: int) -> str:
    """Indent Markdown headings `repeat` times."""
    first_heading_token = compile(pattern=r"^#", flags=MULTILINE)
    indented_heading_tokens = f"#{'#' * repeat}"
    return first_heading_token.sub(repl=indented_heading_tokens, string=text)


def report_as_docx(text: str, destination: Path, template: Path, workdir: Path):
    """Report in DOCX format.

    Since result would be `bytes`, write directly to `destination`.
    """
    with chdir(workdir):  # Pandoc expects links relative to working directory
        run(
            encoding="utf-8",
            input=text,
            check=False,
            args=spacefold(
                 "pandoc"
                 "  --standalone"  # Produce standalone document
                 "  --from markdown-auto_identifiers"  # Avoid bookmarked headers
                 "  --to docx"  # Need to specify output format
                f"  --reference-doc {pathfold(template)}"  # Use this template
                f"  --output {pathfold(destination)}"
            )
        )  # fmt: skip


def spacefold(string: str):
    """Normalize spaces."""
    return join(split(string))


def pathfold(path: Path):
    """Resolve path to a quoted POSIX path."""
    return quote(path.resolve().as_posix())


if __name__ == "__main__":
    main()
