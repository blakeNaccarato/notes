"""Sync plans, ."""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from json import loads
from re import Match, finditer

from markdown_it.token import Token
from mdformat.renderer import MDRenderer
from mdformat_frontmatter import plugin
from more_itertools import one, only

from notes.markdown import MD
from notes.serialization import ser_datetime, ser_json
from notes.times import get_now, get_time_today
from notes_pipeline.models.params import PARAMS


def main():  # noqa: D103  # sourcery skip: low-code-quality
    tokens = MD.parse(PARAMS.paths.plan.read_text(encoding="utf-8"))
    idx = -1
    # Advance to first "Plans" second-level heading
    while (
        len(t := tokens[(idx := idx + 1) : idx + HEADING_TOKEN_COUNT])
        == HEADING_TOKEN_COUNT
    ) and (t[0].type != "heading_open" or t[0].tag != "h2" or t[1].content != "Plans"):
        pass
    # Parse plan task list items up to next heading
    kinds: dict[str, Kind] = defaultdict(Kind)
    last_seen: dict[str, datetime] = {
        k: datetime.fromisoformat(v)
        for k, v in loads(PARAMS.paths.seen_plans.read_text(encoding="utf-8")).items()
    }
    seen: dict[str, datetime] = {}
    idx += HEADING_TOKEN_COUNT - 1
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
    # Render to Markdown and save the times that items were first seen
    PARAMS.paths.plan.write_text(
        encoding="utf-8",
        data=MDRenderer().render(
            tokens=tokens, options={"parser_extension": [plugin]}, env={}
        ),
    )
    PARAMS.paths.seen_plans.write_text(
        encoding="utf-8",
        data=f"{ser_json({k: ser_datetime(v) for k, v in seen.items()})}\n",
    )


@dataclass
class Plan:
    """A plan item."""

    cutoff: datetime
    destination: str


HEADING_TOKEN_COUNT = 3
START_OF_DAY = get_time_today(time(0))
PLANS = {
    "Today": Plan(START_OF_DAY, "Past week"),
    "Past week": Plan(START_OF_DAY - timedelta(days=7), "Reprioritize"),
    "Reprioritize": Plan(datetime.min, ""),
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


if __name__ == "__main__":
    main()
