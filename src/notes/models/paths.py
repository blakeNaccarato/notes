"""Paths for this project."""

from pathlib import Path
from typing import Any

from pydantic import DirectoryPath, FilePath, validator
from ruamel.yaml import YAML

from notes import DATA_DIR, LOCAL_DATA
from notes.models import MyBaseModel


def init():
    """Synchronize project paths. Run on initial import of `paths` module."""
    from notes import PARAMS_FILE
    from notes.models.paths import Paths, repl_path

    yaml = YAML()
    yaml.indent(offset=2)
    params = yaml.load(PARAMS_FILE) if PARAMS_FILE.exists() else {}
    paths = Paths()
    params["paths"] = repl_path(paths.dict(exclude_none=True))
    yaml.dump(params, PARAMS_FILE)


def repl_path(dirs_dict: dict[str, Path]):
    """Replace Windows path separator with POSIX separator."""
    return {k: str(v).replace("\\", "/") for k, v in dirs_dict.items()}


def get_sorted_paths(path: Path) -> list[Path]:
    """Iterate over a sorted directory."""
    return sorted(path.iterdir())


class LocalPaths(MyBaseModel):
    """Local paths for larger files not stored in the cloud."""

    data: DirectoryPath = LOCAL_DATA

    # "always" so it'll run even if not in YAML
    # "pre" because dir must exist pre-validation
    @validator(
        "data",
        always=True,
        pre=True,
    )
    def validate_output_directories(cls, directory: Path) -> Path:
        """Re-create designated output directories each run, for reproducibility."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory


class Paths(MyBaseModel):
    """Directories relevant to the project."""

    class Config(MyBaseModel.Config):
        @staticmethod
        def schema_extra(schema: dict[str, Any]):
            for prop in schema.get("properties", {}).values():
                default = prop.get("default")
                if isinstance(default, str):
                    prop["default"] = default.replace("\\", "/")

    # ! REQUIREMENTS
    requirements: FilePath = Path("requirements.txt")
    dev_requirements: DirectoryPath = Path(".tools/requirements")

    # ! PACKAGE
    package: DirectoryPath = Path("src") / "notes"
    stages: DirectoryPath = package / "stages"
    models: DirectoryPath = package / "models"
    paths_module: FilePath = models / "paths.py"

    # ! STAGES
    stage_schema: FilePath = stages / "schema.py"

    # ! DATA
    data: DirectoryPath = DATA_DIR
    examples: DirectoryPath = data / "examples"

    # ! SCHEMA
    # Can't be "schema", which is a special member of BaseClass
    project_schema: DirectoryPath = data / "schema"

    # "always" so it'll run even if not in YAML
    # "pre" because dir must exist pre-validation
    @validator(
        "data",
        "examples",
        "project_schema",
        always=True,
        pre=True,
    )
    def validate_output_directories(cls, directory: Path) -> Path:
        """Re-create designated output directories each run, for reproducibility."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory


init()
