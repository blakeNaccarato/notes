"""Dev."""

from collections.abc import Collection
from pathlib import Path
from shlex import quote


def escape(path: str | Path) -> str:
    """Escape a path, suitable for passing to e.g. {func}`~subprocess.run`."""
    return quote(Path(path).as_posix())


def log(obj):
    """Send object to `stdout`."""
    match obj:
        case str():
            print(obj)  # ruff: ignore[print]
        case Collection():
            for o in obj:
                log(o)
        case Path():
            log(escape(obj))
        case _:
            print(obj)  # ruff: ignore[print]
