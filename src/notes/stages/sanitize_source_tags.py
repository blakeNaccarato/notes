"""Sanitize source tags of Omnivore newsletters known to have dirty tags."""

from notes import yaml
from notes.markdown import MD, get_frontmatter
from notes.models.params import PARAMS
from notes.sanitize_source_tags import quote_tags, remove_common_tags

AUTHORS = ["Embedded.fm"]
"""Authors whose tags should be sanitized."""


def main():
    for path in PARAMS.paths.personal_links.iterdir():
        string = path.read_text(encoding="utf-8")
        if yaml.load(get_frontmatter(MD.parse(string))).get("author") not in AUTHORS:
            continue
        for step in [quote_tags, remove_common_tags]:
            string = step(string)
        path.write_text(string, encoding="utf-8")


if __name__ == "__main__":
    main()
