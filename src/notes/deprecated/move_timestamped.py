"""Move certain timestamped files from the grad vault to the personal vault."""

from pathlib import Path

from notes.markdown import MD, get_frontmatter_tags, get_inline_tags
from notes.models.params import PATHS

EXCLUDE = "grad"


def main():
    for source in (p for p in PATHS.grad_timestamped.iterdir() if p.is_file()):
        target = PATHS.personal_timestamped / source.name
        if target.exists():
            continue
        tags = get_tags(source)
        if EXCLUDE not in tags:
            source.rename(target)


def get_tags(file: Path) -> list[str]:
    """Get the tags in a Markdown file."""
    p = MD.parse(file.read_text(encoding="utf-8"))
    return list(get_frontmatter_tags(p) | get_inline_tags(p))


if __name__ == "__main__":
    main()
