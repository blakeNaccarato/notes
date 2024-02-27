"""Will eventually use this API to work with Obsidian backlinks."""

from pathlib import Path

from obsidiantools.api import Vault

vault = Vault(Path("data/local/vaults/personal"))
