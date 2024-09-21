"""Copy paper filenames to the clipboard given Zotero quick copy selections."""

from pathlib import Path

import clipboard  # pyright: ignore[reportMissingImports]
from rich import traceback
from rich.console import Console
from rich.markdown import Markdown

traceback.install()


def main():
    console = Console()

    # Get contents of the clipboard, check if it looks like it came from a Zotero
    # selection. Replace illegal characters the same way Windows Explorer does
    cb = clipboard.paste()
    if "*" not in cb:
        raise BadClipboardError
    cb = cb.replace(":", "").replace("?", "").replace("/", "")

    # Get a list of file patterns for finding individual files
    file_patterns = cb.removesuffix(";").split(";\r\n")
    cwd = Path()

    sources: list[str] = []
    for file_pattern in file_patterns:
        # Glob returns a generator, but we only expect one match. Make it a list and
        # check that there is only one match. Otherwise skip this iteration.
        source_list = list(cwd.glob(f"{file_pattern}.pdf"))
        if len(source_list) == 1:
            source = source_list[0]
        else:
            continue
        sources.append(source.stem)

    clipboard.copy("\n".join(sources))
    console.input(
        Markdown("Paper title(s) copied to clipboard. Press **Enter** to exit.")  # type: ignore
    )


class BadClipboardError(Exception):
    """A crude check for whether a list of titles from Zotero has been received."""

    def __init__(self):
        msg = "Clipboard doesn't appear to contain any paper titles from Zotero."
        super().__init__(msg)


if __name__ == "__main__":
    main()
