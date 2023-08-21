"""Centralized repository of my Obsidian vaults and shared tooling."""

from pathlib import Path

PROJECT_DIR = Path()
"""Project directory."""
# Monkeypatch these when testing.
PARAMS_FILE = Path("params.yaml")
"""Location of the parameters file."""
DATA_DIR = Path("data")
"""Data directory."""
