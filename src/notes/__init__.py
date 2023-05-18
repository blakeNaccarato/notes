"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""

from pathlib import Path

# Monkeypatch these when testing.
PARAMS_FILE = Path("params.yaml")
"""Location of the parameters file."""
DATA_DIR = Path("data")
"""Data directory."""
LOCAL_DATA = Path("~").expanduser() / ".local/notes"
"""Local data directory."""
