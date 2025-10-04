"""Sync plan."""

from __future__ import annotations

from collections import UserList, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, replace
from datetime import datetime, time, timedelta
from json import loads
from re import Match, finditer
from textwrap import indent
from typing import Generic, Self, TypeVar

from markdown_it.token import Token
from mdformat.renderer import MDRenderer
from mdformat_frontmatter import plugin
from more_itertools import islice_extended, one, only
from pydantic.alias_generators import to_snake

from notes.markdown import MD
from notes.serialization import ser_datetime, ser_json
from notes.times import get_now, get_time_today, min_datetime
from notes_pipeline.models.params import PARAMS
from notes_pipeline.sync_lists import sync_lists


def main():  # noqa: C901, D103  # sourcery skip: low-code-quality
    tokens = MD.parse(PARAMS.paths.plan.read_text(encoding="utf-8"))
    lists = sync_lists(
        PARAMS.paths.data / "lists.md",
        PARAMS.paths.personal / "_data" / "unsynced" / "lists.md",
    )
    (PARAMS.paths.data / "lists.csv").unlink(missing_ok=True)
    lists.to_csv(PARAMS.paths.data / "lists.csv", index=False)
    tasks = lists[lists.task & lists.text.str.contains(r"\s🆔\s", na=False)].assign(
        link_text=lambda df: df.outlinks.str.extract(
            r"^.+\|(?P<link_text>.+)\]\]</li></ul>$"
        )["link_text"].astype(str),
        text=lambda df: df.apply(
            lambda row: row["text"].replace(
                row["link_text"], rf"{row['link_text'].split(' 🆔')[0]}"
            ),
            axis="columns",
        ),
        done=lambda df: df.status == "x",
    )
    # Advance to first "Plans" second-level heading
    idx = -1
    while (
        len(t := tokens[(idx := idx + 1) : idx + HEADING_COUNT]) == HEADING_COUNT
    ) and (t[0].type != "heading_open" or t[0].tag != "h2" or t[1].content != "Plans"):
        pass
    # Parse plan task list items up to next heading
    kinds: dict[str, Kind] = defaultdict(Kind)
    last_seen: dict[str, datetime] = {
        k: datetime.fromisoformat(v)
        for k, v in loads(PARAMS.paths.seen_plans.read_text(encoding="utf-8")).items()
    }
    seen: dict[str, datetime] = {}
    idx += HEADING_COUNT - 1
    while (token := one(tokens[(idx := idx + 1) : idx + 1])) and (
        token.type != "heading_open"
    ):
        # Only get inline items with contents matching the plan pattern
        if (
            token.type != "inline"
            or not (children := token.children)
            or not (child := only(children))
            or not (match := only(finditer(PLAN_PAT, child.content)))
            or not (plan := PLANS.get(match["kind"]))
        ):
            continue
        # Store child items for later content modification
        kinds[match["kind"]].child = child
        kinds[match["kind"]].match = match
        if not match["items"]:
            continue
        # Check for old items in the plan
        for item in match["items"].split(","):
            if not (
                matches := tasks[tasks.text.str.contains(rf"\s🆔 {item}", na=False)][
                    ["text", "done"]
                ]
            ).empty and all(matches.done):
                continue
            seen_time = last_seen.get(item) or get_now()
            if seen_time < plan.cutoff:
                # An item seen before the cutoff will be moved, forget that it was seen
                kinds[plan.destination].plans.append(item)
            else:
                # Otherwise the item stays put and the first time it was seen is kept
                kinds[match["kind"]].plans.append(item)
                seen[item] = seen_time
    # Update plan items
    for kind in kinds.values():
        if not kind.match or not kind.child:
            continue
        kind.child.content = get_plan(kind.match, kind.plans)
        if match := only(finditer(PLAN_PAT, kind.child.content)):
            if match["items"] and match["kind"] == "Now":
                ", ".join([f"🆔 {i}" for i in match["items"].split(",")])
            kind.match = match
    # Render to Markdown and save the times that items were first seen
    PARAMS.paths.plan.write_text(encoding="utf-8", data=render(tokens))
    PARAMS.paths.seen_plans.write_text(
        encoding="utf-8",
        data=f"{ser_json({k: ser_datetime(v) for k, v in seen.items()})}\n",
    )


def sync_dataview_plan(tokens: Iterable[Token], items: Sequence[str]) -> list[Token]:
    """Sync DataView query."""
    tokens = Sublist(tokens)
    while (tokens := tokens.walk()) and one(tokens).type != "fence":
        pass
    sp = " "
    one(tokens).content = (
        (
            "\n".join([
                "list without id text",
                "flatten file.tasks.text as text",
                "where",
                indent(
                    prefix=sp * 4,
                    text="\nor ".join(
                        rf'regexmatch(".*🆔 {item}[^\]]*", text)' for item in items
                    ),
                ),
            ])
            + "\n"
        )
        if items
        else ""
    )
    return list(tokens.seq)


T = TypeVar("T")


@dataclass(frozen=True)
class Sublist(UserList[T], Generic[T]):
    """Sublist."""

    seq: Iterable[T]
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


@dataclass
class Plan:
    """A plan item."""

    cutoff: datetime
    destination: str


HEADING_COUNT = 3
START_OF_DAY = get_time_today(time(0))
PLANS = {
    "Now": Plan(get_now() - timedelta(hours=2), "Today"),
    "Today": Plan(START_OF_DAY, "This week"),
    "This week": Plan(START_OF_DAY - timedelta(days=7), "Reprioritize"),
    "Reprioritize": Plan(min_datetime, ""),
}
PLAN_PAT = r"^\[\s\]\s#hide\s(?P<kind>.+)(?P<id>\s🆔.+?)(?:\s⛔\s(?P<items>.+))?$"


def get_plan(match: Match[str], plans: Iterable[str]) -> str:
    """Get plan string."""
    plans_ = f" ⛔ {','.join(plans)}" if plans else ""
    return match.expand(rf"[ ] #hide \g<kind>\g<id>{plans_}")


@dataclass
class Kind:
    """A plan kind."""

    child: Token | None = None
    match: Match[str] | None = None
    plans: list[str] = field(default_factory=list)


def to_kebab(string: str) -> str:
    """Convert string to kebab case."""
    return to_snake(string).replace(" ", "-").replace("_", "-")


def render(tokens: list[Token], finalize: bool = True) -> str:
    """Render."""
    return MDRenderer().render(
        tokens=tokens, options={"parser_extension": [plugin]}, env={}, finalize=finalize
    )


if __name__ == "__main__":
    main()
