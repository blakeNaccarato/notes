"""Paths for this project."""

from pydantic import DirectoryPath, FilePath

from notes import DATA_DIR, PROJECT_DIR
from notes.models import CreatePathsModel


class Paths(CreatePathsModel):
    """Paths associated with project data."""

    data: DirectoryPath = DATA_DIR
    project: DirectoryPath = PROJECT_DIR
    packages: DirectoryPath = project / "src" / "notes"
    models: DirectoryPath = packages / "models"
    stages: DirectoryPath = packages / "stages"
    common: DirectoryPath = data / "common"
    stage_update_common: FilePath = stages / "update_common.py"
    vaults: DirectoryPath = data / "local" / "vaults"
    grad: DirectoryPath = vaults / "grad"
    grad_vscode: DirectoryPath = grad / ".vscode"
    grad_scripts: DirectoryPath = grad / "scripts"
    local: DirectoryPath = vaults / "local"
    local_vscode: DirectoryPath = local / ".vscode"
    local_scripts: DirectoryPath = local / "scripts"
