"""Sync lists."""

from collections import UserList
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from shutil import copy
from subprocess import run
from time import sleep
from typing import Generic, Self, TypeVar

from markdown_it_pyrs import MarkdownIt
from more_itertools import islice_extended
from pandas import DataFrame
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


def sync_lists(src: Path, dst: Path) -> DataFrame:
    """Sync lists."""
    dst.unlink(missing_ok=True)
    copy(src, dst)
    invoke_obsidian_command("app:reload")
    sleep(5)
    for command in [
        "plugin-manager:toggle-omnisearch",
        "dataview-publisher:update-blocks",
    ]:
        invoke_obsidian_command(command)
    for _ in watch(dst.parent):
        break
    sleep(1)
    lists = dst.read_text(encoding="utf-8")
    dst.unlink(missing_ok=True)
    invoke_obsidian_command("app:reload")
    tokens = Sublist(list(MarkdownIt("commonmark").enable("table").tree(lists).walk()))
    while (tokens := tokens.walk()) and ((_token := one(tokens)).name != "table"):
        pass
    table = tokens.seq[tokens.idx]
    (head, body) = table.children
    return DataFrame(
        columns=[
            cell_child.meta["content"]
            for cell in head.children[0].children
            for cell_child in cell.children
        ],
        data=[[cell.children for cell in row.children] for row in body.children],
    ).assign(
        file=lambda df: df["file"].apply(
            lambda nodes: "".join([node.meta.get("content", "") for node in nodes])
        ),
        annotated=lambda df: df["annotated"].apply(
            lambda nodes: "".join([
                node.meta.get("content", "") for node in nodes
            ]).casefold()
            == "true"
        ),
        block_id=lambda df: df["block_id"]
        .apply(lambda nodes: "".join([node.meta.get("content", "") for node in nodes]))
        .astype(str),
        children=lambda df: df["children"]
        .apply(lambda nodes: "".join([node.meta.get("content", "") for node in nodes]))
        .astype(str),
        line=lambda df: df["line"]
        .apply(lambda nodes: "".join([node.meta.get("content", "") for node in nodes]))
        .replace("", 0)
        .astype(int),
        # line_count=lambda df: df["line_count"].apply(
        #     lambda nodes: "".join([node.meta.get("content", "") for node in nodes])
        # ),
        link=lambda df: df["link"]
        .apply(lambda nodes: "".join([node.meta.get("content", "") for node in nodes]))
        .astype(str),
        outlinks=lambda df: df["outlinks"].apply(
            lambda nodes: "".join([node.meta.get("content", "") for node in nodes])
        ),
        parent=lambda df: df["parent"]
        .apply(lambda nodes: "".join([node.meta.get("content", "") for node in nodes]))
        .astype(str),
        section=lambda df: df["section"]
        .apply(lambda nodes: "".join([node.meta.get("content", "") for node in nodes]))
        .astype(str),
        status=lambda df: df["status"]
        .apply(lambda nodes: "".join([node.meta.get("content", "") for node in nodes]))
        .astype(str),
        tags=lambda df: df["tags"]
        .apply(lambda nodes: "".join([node.meta.get("content", "") for node in nodes]))
        .astype(str),
        task=lambda df: df["task"].apply(
            lambda nodes: "".join([
                node.meta.get("content", "") for node in nodes
            ]).casefold()
            == "true"
        ),
        links=lambda df: df["text"].apply(
            lambda ser: [n.meta["url"] for n in ser if n.name == "link"]
        ),
        text=lambda df: df["text"]
        .apply(
            lambda ser: "".join([
                n.meta.get("content", "")
                if n.name == "text"
                else (n.children[0].meta.get("content", "") if n.name == "link" else "")
                for n in ser
            ])
        )
        .astype(str),
    )


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
