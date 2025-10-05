"""Sync lists."""

from collections import UserList
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from subprocess import run
from time import sleep
from typing import Generic, Self, TypeVar

from markdown_it_pyrs import MarkdownIt, Node
from more_itertools import islice_extended
from pandas import DataFrame
from pydantic.alias_generators import to_camel
from watchfiles import watch

from notes.markdown import one

T = TypeVar("T")


@dataclass(frozen=True)
class Sublist(UserList[T], Generic[T]):
    """Sublist."""

    seq: Sequence[T]
    data: list[T] = field(default_factory=list)
    idx: int = -1

    def jump(self, idx: int, count: int = 1) -> Self:
        """Jump to an index."""
        return replace(
            self, data=list(islice_extended(self.seq, idx, idx + count)), idx=idx
        )

    def walk(self, count: int = 1, step: int = 1) -> Self:
        """Walk the list."""
        return replace(
            self,
            data=list(islice_extended(self.seq, (idx := self.idx + step), idx + count)),
            idx=idx,
        )


def sync_lists(path: Path, backup: Path, dry: bool = False) -> DataFrame:
    """Sync lists."""
    # sourcery skip: extract-method, low-code-quality
    if dry:
        if not backup.exists():
            raise FileNotFoundError(f"Can't do a dry run: {backup} does not exist.")
        lists = backup.read_text(encoding="utf-8")
    else:
        path.unlink(missing_ok=True)
        path.write_text(
            encoding="utf-8", newline="\n", data=DATAVIEW_PUBLISHER_NOTE_CONTENT
        )
        invoke_obsidian_command("app:reload")
        sleep(7)
        invoke_obsidian_command("dataview-publisher:update-blocks")
        for _ in watch(path):
            break
        sleep(2)
        lists = path.read_text(encoding="utf-8")
        if backup.exists():
            backup.unlink(missing_ok=True)
        path.rename(backup)
    tokens = Sublist(list(MarkdownIt("commonmark").enable("table").tree(lists).walk()))
    while (tokens := tokens.walk()) and (one(tokens).name != "table"):
        pass
    (head, body) = tokens.seq[tokens.idx].children
    return (
        DataFrame(
            columns=[
                cell_child.meta["content"]
                for cell in head.children[0].children
                for cell_child in cell.children
            ],
            data=[[cell.children for cell in row.children] for row in body.children],
        )
        .assign(**{
            col: lambda df, col=col: df[col].apply(join_nodes).astype("string[pyarrow]")
            for col in [
                "annotated",
                "block_id",
                "children",
                "file",
                "line_count",
                "line",
                "parent",
                "section",
                "status",
                "tags",
                "task",
            ]
        })
        .assign(
            **{
                "outlinks": lambda df: df["outlinks"].apply(join_nodes),
                "links": lambda df: df["text"].apply(
                    lambda ser: [n.meta["url"] for n in ser if n.name == "link"]
                ),
                "text": lambda df: df["text"]
                .apply(
                    lambda ser: "".join([
                        n.meta.get("content", "")
                        if n.name == "text"
                        else (
                            n.children[0].meta.get("content", "")
                            if n.name == "link"
                            else ""
                        )
                        for n in ser
                    ])
                )
                .astype("string[pyarrow]"),
            },
            **{
                col: (
                    lambda df, col=col: df[col]
                    .replace("", "0")
                    .astype(int)
                    .astype("int64[pyarrow]")
                )
                for col in ["line", "line_count"]
            },
            **{
                col: lambda df, col=col: df[col]
                .apply(lambda text: text.casefold() == "true")
                .astype("bool[pyarrow]")
                for col in ["annotated", "task"]
            },
        )
    )


def join_nodes(nodes: Iterable[Node]) -> str:
    """Join nodes."""
    return "".join([node.meta.get("content", "") for node in nodes])


def invoke_obsidian_command(command: str):
    """Invoke Obsidian command."""
    run(
        args=[
            "powershell",
            "-NonInteractive",
            "-NoProfile",
            "-Command",
            "Start-Process",
            f"obsidian://adv-uri?commandid={command}",
        ],
        check=True,
    )


DATAVIEW_TABLE_COLUMNS = ",\n    ".join([
    f"item.{to_camel(col)} as {col}"
    for col in [
        "annotated",
        "block_id",
        "children",
        "line_count",
        "line",
        "link",
        "outlinks",
        "parent",
        "section",
        "status",
        "tags",
        "task",
        "text",
    ]
])
DATAVIEW_PUBLISHER_NOTE_CONTENT = f"""\
---
tags:
  - dataview-publisher
---

%% DATAVIEW_PUBLISHER: start

```
table
    {DATAVIEW_TABLE_COLUMNS}
from -"_data"
flatten file.lists as item
where contains(item.text, "🆔")
```

%%
%% DATAVIEW_PUBLISHER: end %%
"""
