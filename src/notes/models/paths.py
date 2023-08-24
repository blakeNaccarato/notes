"""Paths for this project."""

from pathlib import Path

from boilercore.models import CreatePathsModel
from pydantic import DirectoryPath, FilePath

from notes import DATA_DIR, PROJECT_DIR

TEXT_EXPAND_SOURCE = Path(".obsidian/plugins/mrj-text-expand/main.js")


class Paths(CreatePathsModel):
    """Paths associated with project data."""

    data: DirectoryPath = DATA_DIR
    project: DirectoryPath = PROJECT_DIR

    external: DirectoryPath = data / "external"

    packages: DirectoryPath = project / "src" / "notes"
    models: DirectoryPath = packages / "models"
    stages: DirectoryPath = packages / "stages"

    common: DirectoryPath = data / "common"
    obsidian_common: DirectoryPath = data / "obsidian_common"
    stage_update_common: FilePath = stages / "update_common.py"

    local: DirectoryPath = data / "local"
    vaults: DirectoryPath = local / "vaults"
    grad: DirectoryPath = vaults / "grad"
    grad_vscode: DirectoryPath = grad / ".vscode"
    grad_scripts: DirectoryPath = grad / ".scripts"
    grad_text_expand_source = grad / TEXT_EXPAND_SOURCE
    personal: DirectoryPath = vaults / "personal"
    personal_vscode: DirectoryPath = personal / ".vscode"
    personal_scripts: DirectoryPath = personal / ".scripts"
    personal_text_expand_source = personal / TEXT_EXPAND_SOURCE
