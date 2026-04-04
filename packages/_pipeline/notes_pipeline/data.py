"""Data."""

from dataclasses import asdict, dataclass
from pathlib import Path


def get_data(root: Path | None = None) -> dict[str, Path]:
    root_ = walk_to_path(root or Path.cwd(), Path("data"))

    @dataclass
    class _Data:
        # * Git-tracked
        # * Local
        root: Path = root_
        local: Path = root_ / "local"
        # ! Vaults
        vaults: Path = local / "vaults"
        personal: Path = vaults / "personal"
        # ! .obsidian folders
        personal_obsidian: Path = personal / ".obsidian"
        personal_plugins: Path = personal_obsidian / "plugins"
        # ! Inputs
        personal_links: Path = personal / "_sources/links"
        plan: Path = personal / "__reps/2025-01-30T084608-0700-plans.md"
        # ! Results
        seen_plans: Path = root_ / "seen_plans.json"
        personal_timestamped: Path = personal / "_timestamped"

    return asdict(_Data())


def walk_to_path(start: Path, target: Path) -> Path:
    if target.is_absolute():
        if target.exists():
            return target
        raise FileNotFoundError(
            f"Target path {target} given as an absolute path, but it does not exist."
        )
    path = start
    while not (path / target).exists():
        path = path.parent
    return path / target
