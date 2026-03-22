import marimo

__generated_with = "0.20.4"
app = marimo.App()

with app.setup:
    from calendar import day_name
    from collections import defaultdict
    from collections.abc import Iterable
    from dataclasses import dataclass, field
    from datetime import datetime, time, timedelta
    from functools import reduce
    from io import StringIO
    from json import loads
    from operator import add
    from pathlib import Path
    from re import Match, finditer
    from subprocess import run

    import marimo as mo
    from more_itertools import only
    from pandas import (
        CategoricalDtype,
        DataFrame,
        Series,
        col,  # ty:ignore[unresolved-import]
        read_csv,
    )

    from notes.times import get_now, get_time_today, min_datetime
    from notes_pipeline.data import get_data

    data = get_data(Path.cwd())
    mo.json(data)


@app.class_definition
@dataclass
class Plan:
    """A plan item."""

    cutoff: datetime
    destination: str


@app.class_definition
@dataclass
class Kind:
    """A plan kind."""

    content: str = ""
    match: Match[str] | None = None
    plans: list[str] = field(default_factory=list)


@app.function
def get_plan(match: Match[str], plans: Iterable[str]) -> str:
    """Get plan string."""
    plans_ = f" ⛔ {','.join(plans)}" if plans else ""
    return match.expand(rf"[ ] #hide \g<kind>\g<id>{plans_}")


@app.function
def get_days(priority: Series, days: dict[str, str]) -> Series:
    day_ = priority.astype(str)
    for day, priority_ in days.items():
        day_ = day_.replace(priority_, day)
    return day_.astype(CategoricalDtype(ordered=True, categories=list(days)))


@app.function
def extract_task_data(df: DataFrame, priorities: Iterable[str]) -> DataFrame:
    return df.assign(
        **df["text"].str.extract(
            "".join([
                r"^",
                r"(?P<checkbox>\s*-\s*\[[^\]]\])",  # Markdown-style checkbox
                r"\s*",
                r"(?P<tags>(?:#\w+\s)*)",  # Tags
                r"\s*",
                r"(?P<task>.*)",
                r"(?P<id_tok>\s*🆔\s*)",
                r"(?P<id>[^\s]+)",
                r"\s*",
                rf"(?P<priority>[{''.join(priorities)}])",
                r"(?P<rest>.*)",
                r"$",
            ])
        )
    )


@app.function
def get_plans(tasks: DataFrame) -> DataFrame:
    return tasks.loc[~col("done")].loc[
        col("id").isin(
            dict(
                zip(
                    ["Reminders", "Now", "Today", "This week", "Reprioritize"],
                    [
                        plan.split("⛔ ")[1].split(",")
                        for plan in tasks.loc[
                            col("path") == "__reps/2025-01-30T084608-0700-plans.md"
                        ]["text"].tolist()
                    ],
                    strict=True,
                )
            )["This week"]
        )
    ]


@app.cell
def _():
    priorities = ["🔺", "⏫", "🔼", "🔽", "⏬"]
    _days = [day_name[(datetime.today() + timedelta(days=i)).weekday()] for i in range(7)]
    days = {
        _days[i]: priorities[j] for i, j in {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4}.items()
    }
    tasks = (
        DataFrame(
            columns=[
                "path",
                "line",
                "text",
                "checkbox",
                "tags",
                "task",
                "entry",
                "id_tok",
                "id",
                "priority",
                "rest",
                "status",
                "done",
                "day",
            ],
            data=read_csv(
                StringIO(
                    run(
                        args=["obsidian", "tasks", "format=csv"],
                        capture_output=True,
                        check=True,
                        encoding="utf-8",
                    ).stdout
                ),
                header=None,
                names=["status", "text", "path", "line"],
            ),
        )
        .pipe(extract_task_data, priorities)
        .assign(**{
            "task": col("task")
            .str.replace(r"\[([^\]]+)\]\([^)]*\)", r"\1", regex=True)
            .str.replace(r"\s{2,}", " ", regex=True)
            .str.strip()
            .str.replace(r"\[([^\]]+)\]\([^)]*\)", r"\1", regex=True)
            .str.replace(r"\s{2,}", " ", regex=True)
            .str.strip(),
            "entry": "[" + col("task") + "](" + col("path") + ")",
            "done": col("status") == "x",
            "priority": col("priority").astype(
                CategoricalDtype(ordered=True, categories=priorities)
            ),
            "day": col("priority").pipe(get_days, days),
        })
        .pipe(get_plans)
        .sort_values("day", na_position="first")
    )
    mo.ui.table(tasks)
    return (tasks,)


@app.cell
def _(tasks):
    week_plan = """\
    ## <% `Week plan (${tp.obsidian.moment().format(tp.user.getDateFmt())})` %>
    """ + "".join(
        (
            tasks
            .set_index("day")[["entry"]]
            .groupby("day")
            .agg(
                lambda ser: (
                    f"""
    - **{ser.index.get_level_values("day")[0]}**
    - 04
    - 07
    - 10
    - 13
    - 16
    - 19
    - **Plan**"""
                    + reduce(
                        add,
                        [
                            f"""
    - {entry}"""
                            for entry in ser
                        ],
                    )
                )
            )
        )["entry"].tolist()
    )
    (data["personal"] / "_Ω/Snip/Week plan.md").write_text(encoding="utf-8", data=week_plan)
    mo.md(week_plan)
    return


@app.cell
def _(plans, tasks):
    # TODO: Implement plan reprioritization

    mo.stop(True)

    # # Render to Markdown and save the times that items were first seen
    # PARAMS.paths.plan.write_text(encoding="utf-8", data=render(tokens))
    # PARAMS.paths.seen_plans.write_text(
    #     encoding="utf-8",
    #     data=f"{ser_json({k: ser_datetime(v) for k, v in seen.items()})}\n",
    # )
    # invoke_obsidian_command("app:reload")

    START_OF_DAY = get_time_today(time(0))
    PLANS = {
        "Reminders": Plan(min_datetime, ""),
        "Now": Plan(get_now() - timedelta(hours=2), "Today"),
        "Today": Plan(START_OF_DAY, "This week"),
        "This week": Plan(START_OF_DAY - timedelta(days=7), "Reprioritize"),
        "Reprioritize": Plan(min_datetime, ""),
    }
    PLAN_PAT = r"^-\s\[\s\]\s#hide\s(?P<kind>.+)(?P<id>\s🆔.+?)(?:\s⛔\s(?P<items>.+))?$"
    last_seen: dict[str, datetime] = {
        k: datetime.fromisoformat(v)
        for k, v in loads(data["seen_plans"].read_text(encoding="utf-8")).items()
    }
    seen: dict[str, datetime] = {}
    kinds: dict[str, Kind] = defaultdict(Kind)
    for plan in plans:
        if not (match := only(finditer(PLAN_PAT, plan))) or not (
            plan := PLANS.get(match["kind"])
        ):
            continue
        # Check for old items in the plan
        for item in match["items"].split(","):
            if (
                False  # noqa: SIM223 # TODO: Reimplement done filter
                and not (
                    matches := tasks[tasks.text.str.contains(rf"\s🆔 {item}", na=False)][
                        ["text", "done"]
                    ]
                ).empty
                and all(matches.done)
            ):
                continue
            kinds[match["kind"]].match = match
            if not match["items"]:
                continue
            seen_time = last_seen.get(item) or get_now()
            # TODO: Reimplement cutoff
            if False or seen_time < plan.cutoff:
                # An item seen before the cutoff will be moved, forget that it was seen
                kinds[plan.destination].plans.append(item)
            else:
                # Otherwise the item stays put and the first time it was seen is kept
                kinds[match["kind"]].plans.append(item)
                seen[item] = seen_time
    # Update plan items
    for kind in kinds.values():
        if not kind.match:
            continue
        kind.content = get_plan(kind.match, kind.plans)
        if not kind.content or not kind.match:
            continue
        if match := only(finditer(PLAN_PAT, kind.content)):
            if match["items"] and match["kind"] == "Now":
                ", ".join([f"🆔 {i}" for i in match["items"].split(",")])
            kind.match = match
    kinds
    return


if __name__ == "__main__":
    app.run()
