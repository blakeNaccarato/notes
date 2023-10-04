"""Generate a report."""

from contextlib import chdir
from os import walk
from pathlib import Path
from re import MULTILINE, compile
from shlex import join, quote, split
from subprocess import run


def main():
    vault_root = Path("C:/Users/Blake/Code/mine/notes/data/local/vaults/grad")
    report_root = vault_root / "projects"
    text = ""
    for folder, _, files in walk(report_root):
        for file in sorted(Path(folder) / f for f in files if f.endswith(".md")):
            text += f"\n{indent_from_root(file, report_root)}"
    report(
        text=text,
        destination=Path("C:/Users/Blake/Desktop/report.docx"),
        template=Path("C:/Users/Blake/Code/mine/boilercv/data/scripts/template.dotx"),
        workdir=vault_root,
    )


def indent_from_root(file: Path, root: Path) -> str:
    """Indent Markdown headings in `file` based on their depth relative to `root`."""
    depth = len(file.relative_to(root).parts) - (1 if "_" in file.stem else 0)
    return f"\n{indent_headings(file.read_text(encoding='utf-8'), depth)}"


def indent_headings(text: str, repeat: int) -> str:
    """Indent Markdown headings `repeat` times."""
    first_heading_token = compile(pattern=r"^#", flags=MULTILINE)
    indented_heading_tokens = f"#{'#' * repeat}"
    return first_heading_token.sub(repl=indented_heading_tokens, string=text)


def report(text: str, destination: Path, template: Path, workdir: Path):
    """Generate a DOCX report from a notebook.

    Requires changing the active directory to the Markdown folder outside of this
    asynchronous function, due to how Pandoc generates links inside the documents.
    """
    with chdir(workdir):  # Pandoc expects links relative to working directory
        run(
            input=text,
            encoding="utf-8",
            shell=True,
            args=spacefold(
                # fmt: off
                 "pandoc"
                 "  --standalone"  # Produce standalone document
                 "  --from markdown-auto_identifiers"  # Avoid bookmarked headers
                 "  --to docx"  # Need to specify output format
                f"  --reference-doc {pathfold(template)}"  # Use this template
                f"  --output {pathfold(destination)}"
                # fmt: on
            ),
        )


def spacefold(string: str):
    """Normalize spaces."""
    return join(split(string))


def pathfold(path: Path):
    """Resolve path to a quoted POSIX path."""
    return quote(path.resolve().as_posix())


if __name__ == "__main__":
    main()
