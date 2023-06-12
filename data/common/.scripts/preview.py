"""Preview a Markdown document by rendering to HTML with MyST."""

from pathlib import Path
from shutil import copy
from subprocess import run
from tempfile import TemporaryDirectory
from time import sleep

from typer import Typer

APP = Typer()


@APP.command()
def main(source: Path):
    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        copy(source, tmp / "index.md")
        copy(".scripts/conf.py", tmp / "conf.py")
        site = tmp / "_site"
        result = site / "index.html"
        run(["pwsh", "-C", f"python -m sphinx {tmp} {site}"])  # noqa: S603, S607
        run(["pwsh", "-C", f"Invoke-Item {result}"])  # noqa: S603, S607
        sleep(1)


if __name__ == "__main__":
    APP()
