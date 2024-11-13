"""Sanitize source tags of Omnivore newsletters known to have dirty tags."""

from yaml import safe_load

from notes.markdown import MD, get_frontmatter
from notes.sanitize_source_tags import quote_tags, remove_common_tags
from notes_pipeline.models.params import PARAMS

AUTHORS = ["Embedded.fm"]
"""Authors whose tags should be sanitized."""


def main():  # noqa: D103
    for path in PARAMS.paths.personal_links.iterdir():
        string = path.read_text(encoding="utf-8")
        if safe_load(get_frontmatter(MD.parse(string))).get("author") not in AUTHORS:
            continue
        for step in [quote_tags, remove_common_tags]:
            string = step(string)
        path.write_text(string, encoding="utf-8")


if __name__ == "__main__":
    main()
