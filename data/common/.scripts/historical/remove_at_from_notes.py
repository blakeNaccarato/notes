"""Remove `@` from note titles."""

from pathlib import Path

for file in Path("notes").glob("@*.md"):
    file.rename(file.with_name(f"{file.stem.strip('@')}.md"))
