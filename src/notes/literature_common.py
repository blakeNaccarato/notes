"""Common logic for literature scripts."""

import json
import sys
from collections.abc import Callable
from datetime import datetime, timedelta
from itertools import chain
from pathlib import Path
from time import sleep
from typing import Any, Self

from loguru import logger
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger.configure(handlers=[{"sink": sys.stderr, "format": "<level>{message}</level>"}])


def concat_json(files: list[Path]) -> list[dict[str, Any]]:
    """Concatenate JSON files as a list of entries."""
    return list(
        chain.from_iterable(
            list(json.loads(file.read_text(encoding="utf-8"))) for file in files
        )
    )


class DirWatcher:
    """Run a function when a directory changes."""

    min_cooldown = 2

    def __init__(
        self,
        watch_dir: Path,
        on_modified: Callable[[FileSystemEvent], None],
        interval: int = 5,
        cooldown: int = 2,
    ):
        if interval < self.min_cooldown:
            raise ValueError(self.error_message("interval", interval))
        if cooldown < self.min_cooldown:
            raise ValueError(self.error_message("cooldown", cooldown))
        self.watch_dir = watch_dir
        self.on_modified = on_modified
        self.interval = interval
        self.cooldown = cooldown
        self.observer = Observer()

    def __enter__(self) -> Self:
        self.observer.schedule(
            ModifiedFileHandler(self.on_modified, self.cooldown),
            self.watch_dir,  # pyright: ignore[reportArgumentType]
        )
        self.observer.start()
        return self

    def run(self):
        """Check for changes on an interval."""
        while True:
            sleep(self.interval)

    def __exit__(self, exc_type: type[BaseException] | None, *_) -> bool:
        if exc_type and exc_type is KeyboardInterrupt:
            self.observer.stop()
            handled_exception = True
        elif exc_type:
            handled_exception = False
        else:
            handled_exception = True
        self.observer.join()
        return handled_exception

    def error_message(self, interval_name: str, interval: int) -> str:  # noqa: D102
        return (
            f"{interval_name.capitalize()} of {interval} seconds is less than the"
            f" minimum cooldown of {self.min_cooldown} seconds."
        )


class ModifiedFileHandler(FileSystemEventHandler):
    """Handle modified files."""

    def __init__(self, func: Callable[[FileSystemEvent], None], cooldown: int):
        self.func = func
        self.cooldown = timedelta(seconds=cooldown)
        self.triggered_time = datetime.min

    def on_modified(self, event: FileSystemEvent):  # noqa: D102
        if (datetime.now() - self.triggered_time) > self.cooldown:
            self.func(event)
            self.triggered_time = datetime.now()
