"""Sanitize source tags."""

import re

from notes.markdown import MD, get_frontmatter, get_frontmatter_tags, get_inline_tags

TAGS = r"tags:[\s\S]*(?=id)"
"""Tags frontmatter entry, assuming `id` field comes afterwards.

This assumption is good in `_sources/links` due to Obsidian Linter sort settings."""


def remove_common_tags(string):
    """Compare frontmatter and inline tags, removing common tags.

    Tags may not be identical in frontmatter and inline text, as the Obsidian Linter
    truncates tags at illegal characters.
    """
    parsed = MD.parse(string)
    fm = get_frontmatter(parsed).content
    for fm_tag, inl_tag in sorted({
        (fm_tag, inl_tag)
        for fm_tag in get_frontmatter_tags(parsed)
        for inl_tag in get_inline_tags(parsed)
        if fm_tag in inl_tag
    }):
        fm = fm.replace(f'  - "{fm_tag}"\n', "")
        string = re.sub(rf"#({re.escape(inl_tag)})", r"\\#\1", string)
    string = string.replace(get_frontmatter(MD.parse(string)).content, fm)
    return string


UNQUOTED_TAG = r"^(\s{2}-\s)([^\"\n]+)$"
"""Unquoted tag."""
QUOTED_TAG = r'\1"\2"'
"""Quoted tag."""


def quote_tags(string: str) -> str:
    """Quote tags in frontmatter."""
    parsed = MD.parse(string)
    fm_span = (
        fm_begin := string.find(fm := get_frontmatter(parsed).content),
        fm_begin + len(fm),
    )
    if match := re.compile(TAGS).search(string, *fm_span):
        keys = match.group()
        string = string.replace(
            keys, re.sub(UNQUOTED_TAG, QUOTED_TAG, keys, flags=re.MULTILINE)
        )
    return string
