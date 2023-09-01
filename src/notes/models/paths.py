"""Paths for this project."""

from pathlib import Path

from boilercore.models import CreatePathsModel
from boilercore.paths import get_package_dir, map_stages
from pydantic import DirectoryPath, FilePath

import notes
from notes import PROJECT_PATH

TEXT_EXPAND_SOURCE = Path(".obsidian/plugins/mrj-text-expand/main.js")


def get_common(root: Path, dirs: list[Path]):
    return [root / dir_.name for dir_ in dirs]


class Paths(CreatePathsModel):
    """Paths associated with project data."""

    # * Roots
    # ! Project
    project: DirectoryPath = PROJECT_PATH
    # ! Package
    package: DirectoryPath = get_package_dir(notes)
    # ! Data
    data: DirectoryPath = project / "data"
    external: DirectoryPath = data / "external"
    stages: dict[str, FilePath] = map_stages(package / "stages", package)

    # * Git-Tracked Inputs
    common: DirectoryPath = data / "common"
    common_dirs: list[DirectoryPath] = list(common.iterdir())  # noqa: RUF012
    obsidian_common: DirectoryPath = data / "obsidian_common"

    # * DVC-Tracked Inputs

    # * LOCAL
    local: DirectoryPath = data / "local"
    vaults: DirectoryPath = local / "vaults"
    grad: DirectoryPath = vaults / "grad"
    personal: DirectoryPath = vaults / "personal"
    # * Inputs
    grad_timestamped: DirectoryPath = grad / "_timestamped"
    # * Results
    personal_timestamped: DirectoryPath = personal / "_timestamped"

    # * DVC-Tracked Results
    grad_common: list[DirectoryPath] = get_common(grad, common_dirs)
    grad_text_expand_source = grad / TEXT_EXPAND_SOURCE
    personal_common: list[DirectoryPath] = get_common(personal, common_dirs)
    personal_text_expand_source = personal / TEXT_EXPAND_SOURCE
