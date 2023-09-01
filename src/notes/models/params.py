"""Parameters for the data pipeline."""

from pathlib import Path

from boilercore.models import SynchronizedPathsYamlModel
from pydantic import Field

from notes import get_params_file
from notes.models.paths import Paths

PARAMS_FILE = get_params_file()


class Params(SynchronizedPathsYamlModel):
    """Project parameters."""

    paths: Paths = Field(default_factory=Paths)

    def __init__(self, data_file: Path = PARAMS_FILE, **kwargs):
        """Initialize, propagate paths to the parameters file, and update the schema."""
        super().__init__(data_file, **kwargs)


PARAMS = Params()
"""All project parameters, including paths."""
