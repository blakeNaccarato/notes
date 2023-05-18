"""Generate expected results."""

from pathlib import Path
from tempfile import TemporaryDirectory

import notes


def main():
    """Generate expected results."""
    with TemporaryDirectory() as tmpdir:
        notes.PARAMS_FILE = Path(tmpdir) / "params.yaml"
        notes.DATA_DIR = Path("tests/data/cloud")
        notes.LOCAL_DATA = Path("tests/data/local")

        from notes.stages import schema

        for module in (schema,):
            module.main()


if __name__ == "__main__":
    main()
