"""Will eventually use this API to work with Obsidian backlinks."""

from pathlib import Path

from mdformat.renderer import MDRenderer
from mdformat_frontmatter import plugin
from obsidiantools.api import Vault

# ? `notebooks/sync_bullet_overflow.ipynb`
MDRenderer().render(
    tokens=[], options={"parser_extension": [plugin]}, env={}, finalize=False
)
# ? To-do
vault = Vault(Path("data/local/vaults/personal"))
