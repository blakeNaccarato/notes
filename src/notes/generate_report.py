from contextlib import chdir
from os import walk
from pathlib import Path
from re import MULTILINE, compile
from shlex import join, quote, split
from subprocess import run

RE = compile(r"^#", flags=MULTILINE)
WORKDIR = Path("C:/Users/Blake/Code/mine/notes/data/local/vaults/grad")
SOURCE = Path("C:/Users/Blake/Code/mine/notes/data/local/vaults/grad/projects")
TEMPLATE = Path("C:/Users/Blake/Code/mine/boilercv/data/scripts/template.dotx")
DOCX = Path("C:/Users/Blake/Desktop/report.docx")
MD = Path("C:/Users/Blake/Desktop/report.md")


def main():
    md_full = ""
    for w in walk(SOURCE):
        for md in sorted(Path(w[0]) / file for file in w[2] if file.endswith(".md")):
            depth = 1 + len(md.relative_to(SOURCE).parts) - (1 if "_" in md.stem else 0)
            md_full += "\n" + RE.sub("#" * depth, md.read_text(encoding="utf-8"))
    MD.write_text(encoding="utf-8", data=md_full)
    with chdir(WORKDIR):
        report(TEMPLATE, DOCX, MD)


def report(template: Path, docx: Path, md: Path):
    """Generate a DOCX report from a notebook.

    Requires changing the active directory to the Markdown folder outside of this
    asynchronous function, due to how Pandoc generates links inside the documents.
    """
    run(
        join(
            split(
                " pandoc"
                # Pandoc configuration
                "   --standalone"  # Don't produce a document fragment.
                "   --from markdown-auto_identifiers"  # Avoids bookmark pollution around Markdown headers
                "   --to docx"  # The output format
                f"  --reference-doc {fold(template)}"  # The template to export literature reviews to
                # I/O
                f"  --output {fold(docx)}"
                f"  {fold(md)}"
            )
        ),
        shell=True,  # noqa: S602
    )


def fold(path: Path):
    """Resolve and normalize a path to a POSIX string path with forward slashes."""
    return quote(path.as_posix())


if __name__ == "__main__":
    main()
