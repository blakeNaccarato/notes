"""Rename filenames from paper titles to citekeys."""

import json
import re
from pathlib import Path

from csl_models import ModelItem

# Pattern that matches the year, authors, and title in a filename stem.
FILENAME_PATTERN = re.compile(
    flags=re.VERBOSE,
    pattern=r"""
    (?P<year>^\d{4}),\s
    (?P<authors>
        \w{1,3}\s\w+  # First author
        (,\s\w{1,3}\s\w+)*  # Remaining authors
    ),\s
    (?P<title>.*$)
    """,
)


def main():
    """Map titles to citekeys and rename matching PDFs to their respective citekeys."""
    # Map titles to citekeys for each reference.
    references = json.loads(Path("_zotero/libraries.json").read_text(encoding="utf-8"))
    library = [ModelItem(**reference) for reference in references]
    citekeys = {get_normalized_title(item): item.citation_key for item in library}

    # Attempt to rename reference PDFs to their respective citekeys.
    files = Path("_staging").glob("*.pdf")
    for file in files:
        matches = FILENAME_PATTERN.match(file.stem)
        if not (matches and matches["title"]):
            file.rename(Path("_oops") / file.name)
            continue

        citekey = citekeys.get(matches["title"].casefold())
        if not citekey:
            file.rename(Path("_orphans") / file.name)
            continue

        file.rename(Path("_orphans") / file.name)


def get_normalized_title(item):
    """Get the normalized title of a reference."""
    return item.title.replace(":", "").replace("?", "").replace("/", "").casefold()


if __name__ == "__main__":
    main()
