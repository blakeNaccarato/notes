"""Parameters for the data pipeline."""

from pathlib import Path
from subprocess import run

from pydantic import BaseModel, Field
from yaml import safe_dump

from notes_pipeline.models.paths import Paths


class Params(BaseModel):
    """Project parameters."""

    paths: Paths = Field(default_factory=Paths)


PARAMS = Params()
"""All project parameters, including paths."""

PATHS = PARAMS.paths
"""All project paths."""

Path("params.yaml").write_text(
    encoding="utf-8",
    data=safe_dump(
        indent=2,
        width=float("inf"),
        data=(_params := PARAMS.model_dump())
        | {
            "paths": {
                k: v.resolve().relative_to(Path.cwd()).as_posix()
                if isinstance(v, Path)
                else (
                    [v.resolve().relative_to(Path.cwd()).as_posix() for v in v]
                    if isinstance(v, list)
                    else {
                        k: v.resolve().relative_to(Path.cwd()).as_posix()
                        for k, v in v.items()
                    }
                )
                for k, v in _params["paths"].items()
            }
        },
    ),
)
run(
    check=False,
    capture_output=True,
    args=[*["pwsh", "-Command"], "./Invoke-Uv.ps1 pre-commit run --all-files prettier"],
)
