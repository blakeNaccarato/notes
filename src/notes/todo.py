"""Will eventually use this API to work with Obsidian backlinks."""

from pathlib import Path

from aiopath import AsyncPath
from mdformat.renderer import MDRenderer
from mdformat_frontmatter import plugin
from obsidiantools.api import Vault
from requests import get

# sourcery skip: remove-redundant-if
if False:
    # ? `notebooks/sunshine.ipynb`
    get  # noqa: B018
    # ? `notebooks/sync_bullet_overflow.ipynb`
    MDRenderer().render(
        tokens=[], options={"parser_extension": [plugin]}, env={}, finalize=False
    )
    # ? Other
    vault = Vault(Path("data/local/vaults/personal"))
    foo = AsyncPath("")
