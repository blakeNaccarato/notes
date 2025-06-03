"""Markdown parsing utilities."""

from re import findall
from string import whitespace

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.front_matter.index import front_matter_plugin
from more_itertools import one
from yaml import safe_load

MD = MarkdownIt().use(front_matter_plugin)
"""Markdown parser."""


def get_frontmatter_tags(parsed: list[Token]) -> set[str]:
    """Get tags from frontmatter."""
    return set(safe_load(get_frontmatter(parsed).content).get("tags")) or set()


def get_frontmatter(parsed: list[Token]) -> Token:
    """Get frontmatter."""
    yaml_markup = "---"
    if frontmatter_tokens := [
        token
        for token in parsed
        if token.type == "front_matter" and token.markup == yaml_markup
    ]:
        return one(frontmatter_tokens)
    return Token(type="front_matter", tag="", nesting=0)


def get_inline_tags(parsed: list[Token]) -> set[str]:
    """Get inline tags, as in `#tag` in the text."""
    inline_tags: list[str] = []
    for inline_text in [
        token.content
        for token in [t for t in parsed if t.type == "inline" and "#" in t.content]
    ]:
        inline_tags.extend(findall(rf"(?<=#)[^{whitespace}]+", inline_text))
    return set(inline_tags)
