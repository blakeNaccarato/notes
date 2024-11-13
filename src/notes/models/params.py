"""Parameters for the data pipeline."""

from pydantic import BaseModel
from pydantic.v1 import Field

from notes.models.paths import Paths


class Params(BaseModel):
    """Project parameters."""

    paths: Paths = Field(default_factory=Paths)


PARAMS = Params()
"""All project parameters, including paths."""

PATHS = PARAMS.paths
"""All project paths."""
