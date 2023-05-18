"""Test the pipeline."""

from dataclasses import InitVar, dataclass, field
from pathlib import Path
from types import ModuleType

import pytest

TEST_DATA = Path("tests/data")


@pytest.mark.slow()
def test_pipeline(check, monkeypatch, tmp_path):
    """Test the pipeline."""

    def main():
        stage_result_paths = get_stages()
        for module, result_paths in stage_result_paths.items():
            stage = Stage(module, result_paths, tmp_path)
            skip_asserts = ("schema",)
            if stage.name in skip_asserts:
                continue
            for result, expected in stage.expectations.items():
                with check:
                    assert_stage_result(result, expected)

    def get_stages() -> dict[ModuleType, tuple[Path, ...]]:
        """Test the pipeline by patching constants before importing stages."""

        import notes

        monkeypatch.setattr(notes, "PARAMS_FILE", tmp_path / "params.yaml")
        monkeypatch.setattr(notes, "DATA_DIR", tmp_path / "cloud")
        monkeypatch.setattr(notes, "LOCAL_DATA", tmp_path / "local")

        from notes.models.params import PARAMS
        from notes.stages import schema

        return {
            schema: (PARAMS.paths.project_schema,),
        }

    main()


def assert_stage_result(result_file: Path, expected_file: Path):
    """Assert that the result of a stage is as expected.

    Args:
        result_file: The file produced by the stage.
        expected_file: The file that the stage should produce.

    Raises:
        AssertionError: If the result is not as expected.
    """
    assert result_file.read_bytes() == expected_file.read_bytes()


@dataclass
class Stage:
    """Results of running a pipeline stage.

    Args:
        module: The module corresponding to this pipeline stage.
        result_paths: The directories or a single file produced by the stage.
        tmp_path: The results directory.

    Attributes:
        name: The name of the pipeline stage.
        expectations: A mapping from resulting to expected files.
    """

    module: InitVar[ModuleType]
    result_paths: InitVar[tuple[Path, ...]]
    tmp_path: InitVar[Path]

    name: str = field(init=False)
    expectations: dict[Path, Path] = field(init=False)

    def __post_init__(
        self, module: ModuleType, result_paths: tuple[Path, ...], tmp_path: Path
    ):
        self.name = module.__name__.removeprefix(f"{module.__package__}.")
        module.main()
        results: list[Path] = []
        expectations: list[Path] = []
        for path in result_paths:
            expected = TEST_DATA / path.relative_to(tmp_path)
            if expected.is_dir():
                results.extend(sorted(path.iterdir()))
                expectations.extend(sorted(expected.iterdir()))
            else:
                results.append(path)
                expectations.append(expected)
        self.expectations = dict(zip(results, expectations, strict=True))
