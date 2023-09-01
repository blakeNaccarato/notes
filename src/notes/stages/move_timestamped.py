"""Move certain timestamped files from the grad vault to the personal vault."""

from pathlib import Path
from re import compile
from string import whitespace

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.front_matter.index import front_matter_plugin

from notes import yaml
from notes.models.params import PARAMS

EXCLUDE = "grad"


def main():
    PARAMS.paths.grad_timestamped
    for source in (p for p in PARAMS.paths.grad_timestamped.iterdir() if p.is_file()):
        target = PARAMS.paths.personal_timestamped / source.name
        if target.exists():
            continue
        tags = get_tags(source)
        if EXCLUDE not in tags:
            source.rename(target)


TAG = compile(rf"(?<=#)[^{whitespace}]+")


def get_tags(file: Path) -> list[str]:
    """Get the tags in a Markdown file."""
    p = MarkdownIt().use(front_matter_plugin).parse(file.read_text(encoding="utf-8"))
    return list(get_front_matter_tags(p) | get_inline_tags(p))


def get_front_matter_tags(parsed: list[Token]) -> set[str]:
    """Get tags from front matter."""
    yaml_markup = "---"
    if front_matter_tokens := [
        token
        for token in parsed
        if token.type == "front_matter" and token.markup == yaml_markup
    ]:
        front_matter = yaml.load(front_matter_tokens[0].content)
        return set(front_matter.get("tags")) or set()
    return set()


def get_inline_tags(parsed: list[Token]) -> set[str]:
    """Get inline tags, as in `#tag` in the text."""
    inline_tags: list[str] = []
    for inline_text in [
        token.content
        for token in [t for t in parsed if t.type == "inline" and "#" in t.content]
    ]:
        inline_tags.extend(TAG.findall(inline_text))
    return set(inline_tags)


if __name__ == "__main__":
    main()
