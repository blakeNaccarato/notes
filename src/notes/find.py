"""Find all sections in a Markdown document matching a given regex."""

import re
from collections.abc import MutableSequence, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from marko import Markdown
from marko.block import BlockElement, Document, Heading
from marko.md_renderer import MarkdownRenderer
from typer import Typer

APP = Typer()

MARKDOWN = Markdown(renderer=MarkdownRenderer)
"""Parses and renders Markdown as Markdown."""


@APP.command()
def main(source: Path, regex: str):
    """Find all sections in a Markdown document matching a given regex.

    Args:
        source: Markdown document to search.
        regex: Regex to search for.

    Returns
    -------
        Markdown document containing all sections matching the regex.
    """
    document = MARKDOWN.parse(source.read_text(encoding="utf-8"))
    splits = split_by_headings(document)
    section_text = [MARKDOWN.render(split) for split in splits]
    matches = [text for text in section_text if re.search(regex, text)]
    timestamp = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    (Path("_exports") / f"find_{timestamp}.md").write_text(
        encoding="utf-8", data="".join(matches)
    )
    # TODO: Write function to find all in nested structure, with "context depth" param
    # sections = section(splits)


# * -------------------------------------------------------------------------------- * #


def section(document: Document) -> list[Any]:
    """Section a document by heading level.

    Args:
        document: The document to section.

    Returns
    -------
        A nested sequence of document sections.
    """
    splits = split_by_headings(document)
    sections: list[Any] = []
    for split in splits:
        level = document.children[0].level  # pyright: ignore[reportAttributeAccessIssue]
        append_at_depth(seq=sections, item=split, depth=(level - 1))
    return sections


def append_at_depth(seq: MutableSequence[Any], item: Any, depth: int):
    """Append an item to a sequence (in-place) at a given depth.

    If necessary, creates sequences of the type last encountered during traversal.
    Modifies the sequence in-place rather than returning a new sequence due to the
    significant performance overhead of making deep copies of even moderately-nested
    sequences.

    Args:
        seq: The sequence to append to.
        item: The item to append.
        depth: The depth at which to append the item.

    Raises
    ------
        ValueError: If the input is not a sequence.
    """
    # TODO: Annotate as a recursive/cyclic type
    # TODO: See https://github.com/python/mypy/issues/731
    # TODO: See https://github.com/python/mypy/issues/14219
    if not isinstance(seq, MutableSequence):  # type: ignore
        raise TypeError(f"`seq` must be a mutable sequence. Got {type(seq)}.")
    for _ in range(depth):
        if len(seq) and isinstance(seq[-1], MutableSequence):
            seq = seq[-1]
        else:
            seq.append(seq := type(seq)())
    seq.append(item)


def split_by_headings(document: Document) -> list[Document]:
    """Split elements by headings.

    Args:
        document: The document to split.

    Returns
    -------
        A list of documents, each starting with a heading.
    """
    levels = map_headings(document)
    levels_iter = iter(levels.items())
    first_element, first_element_level = next(levels_iter)
    prev_level = first_element_level
    splits = [make_document([first_element])]
    for element, level in levels_iter:
        if level == prev_level and not isinstance(element, Heading):
            splits[-1].children.append(element)  # pyright: ignore[reportAttributeAccessIssue]
        else:
            prev_level = level
            splits.append(make_document([element]))
    return splits


def map_headings(document: Document) -> dict[BlockElement, int]:
    """Map elements to their heading level.

    Args:
        document: Document to map.

    Returns
    -------
        Mapping of elements to heading level.
    """
    level = 0
    levels: dict[BlockElement, int] = {}
    for child in document.children:
        if isinstance(child, Heading):
            level = child.level
        levels[child] = level  # pyright: ignore[reportArgumentType]
    return levels


def make_document(elements: Sequence[BlockElement]) -> Document:
    """Create a document from a sequence of elements.

    Args:
        elements: Elements to assign to the document.

    Returns
    -------
        A document with the given elements.
    """
    document = MARKDOWN.parse("")  # Need to start with a blank document
    document.children = elements
    return document


# * -------------------------------------------------------------------------------- * #

if __name__ == "__main__":
    APP()
