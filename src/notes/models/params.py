"""Parameters for the data pipeline."""


from pydantic import Field

from notes import PARAMS_FILE
from notes.models import SynchronizedPathsYamlModel
from notes.models.paths import Paths

YAML_INDENT = 2


class Params(SynchronizedPathsYamlModel):
    """Project parameters."""

    paths: Paths = Field(default_factory=Paths)

    def __init__(self):
        """Initialize, propagate paths to the parameters file, and update the schema."""
        super().__init__(PARAMS_FILE)


PARAMS = Params()
"""All project parameters, including paths."""
