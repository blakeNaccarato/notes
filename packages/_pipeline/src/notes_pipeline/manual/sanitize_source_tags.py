"""Sanitize source tags."""

from pathlib import Path

from typer import run

from notes.sanitize_source_tags import quote_tags, remove_common_tags


def main(path: Path):  # noqa: D103
    string = path.read_text(encoding="utf-8")
    for step in [quote_tags, remove_common_tags]:
        string = step(string)
    path.write_text(string, encoding="utf-8")


if __name__ == "__main__":
    run(main)
