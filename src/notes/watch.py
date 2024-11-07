"""Keep libraries up to date."""

import json
from pathlib import Path
from time import sleep

from watchdog.events import FileSystemEvent

from notes.literature_common import DirWatcher, concat_json, logger

WATCH_DIR = Path("_zotero")
INTERVAL = 5
IDLE_TIME = 5
INPUT_FILES = list(WATCH_DIR.glob("library*.json"))
OUTPUT_FILE = WATCH_DIR / "libraries.json"


def main():  # noqa: D103
    with DirWatcher(WATCH_DIR, on_modified, INTERVAL) as watcher:
        logger.info(
            f"Watching for changes in {[file.name for file in INPUT_FILES]}."
            f" Changes will trigger an update to '{OUTPUT_FILE.name}'."
        )
        log_idle()
        watcher.run()


def on_modified(event: FileSystemEvent):
    """Concatenate JSON libraries into one main library."""
    logger.info("Modification detected.")
    modified_file = Path(event.src_path)  # pyright: ignore[reportArgumentType]
    if modified_file in INPUT_FILES:
        OUTPUT_FILE.write_text(
            encoding="utf-8", data=json.dumps(concat_json(INPUT_FILES))
        )
        logger.success(f"Updated '{OUTPUT_FILE.name}'")
    else:
        logger.warning(
            f"Modified file '{modified_file.name}' is not one of the input files."
            " Not updating the output file."
        )
    log_idle()


def log_idle():
    """Log a message to clear the Obsidian status bar."""
    sleep(IDLE_TIME)
    logger.info("...")


if __name__ == "__main__":
    main()
