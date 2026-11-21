import marimo

__generated_with = "0.25.2"
app = marimo.App()

with app.setup:
    from collections.abc import Iterable
    from dataclasses import dataclass, field
    from datetime import date, datetime
    from functools import reduce
    from io import StringIO
    from json import dumps, loads
    from operator import add
    from pathlib import Path
    from re import Match, sub
    from subprocess import run
    from textwrap import dedent
    from typing import Any

    import marimo as mo
    from marimo._output.hypertext import Html
    from marimo._output.mime import MIME
    from marimo._plugins.core.web_component import JSONType
    from marimo._plugins.ui._impl.utils.dataframe import ListOrTuple
    from more_itertools import one
    from narwhals._native import IntoDataFrame, IntoLazyFrame
    from pandas import (
        CategoricalDtype,
        DataFrame,
        DateOffset,
        NaT,
        Series,
        Timestamp,
        col,
        read_csv,
        to_timedelta,
    )

    from notes.times import current_tz, get_now
    from notes_pipeline.data import get_data

    data = get_data(Path.cwd())
    mo.json(data)


@app.function
def disp(
    **kwds: ListOrTuple[str | int | float | bool | MIME | None]
    | ListOrTuple[dict[str, JSONType]]
    | dict[str, ListOrTuple[JSONType]]
    | list[dict[str, Any]]
    | dict[str, list[Any]]
    | IntoDataFrame
    | IntoLazyFrame,
) -> Html:
    return mo.vstack(
        items=[mo.ui.table(label=label, data=data) for label, data in kwds.items()]
    )


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
    plans_ = f" ⛔ {','.join(plans)}" if plans else ""  # ty: ignore[truthiness-test-of-iterable]
    return match.expand(rf"[ ] #hide \g<kind>\g<id>{plans_}")


@app.function
def get_days(priority: Series, days: dict[str, str]) -> Series:
    day_ = priority.astype(str)
    for day, priority_ in days.items():
        day_ = day_.replace(priority_, day)
    return day_.astype(CategoricalDtype(ordered=True, categories=list(days)))


@app.function
def extract_task_data(df: DataFrame, priorities: Iterable[str]) -> DataFrame:
    sym = rf"🆔⛔{''.join(priorities)}🔁➕🛫⏳📅❌✅🏁"  # ruff: ignore[ambiguous-unicode-character-string]
    return df.assign(
        **df["text"].str.extract(
            "".join([
                r"^\s*(?:>\s*)?-\s*\[[^\]]\]",  # Markdown-style checkbox
                r"\s*(?P<tags>(?:#\w+\s)*)",
                rf"(?P<task>[^{sym}]+)",
                r"(?=.*🆔\s*(?P<id>[^\s]*))?",
                r"(?=.*⛔\s*(?P<deps>[^\s]*))?",
                rf"(?=.*(?P<priority>[{''.join(priorities)}]))?",
                rf"(?=.*🔁\s*(?P<recurs>[^\{sym}]*))?",
                r"(?=.*➕\s*(?P<created>[^\s]*))?",  # ruff: ignore[ambiguous-unicode-character-string]
                r"(?=.*🛫\s*(?P<starts>[^\s]*))?",
                r"(?=.*⏳\s*(?P<scheduled>[^\s]*))?",
                r"(?=.*📅\s*(?P<due>[^\s]*))?",
                r"(?=.*❌\s*(?P<cancelled>[^\s]*))?",
                r"(?=.*✅\s*(?P<done>[^\s]*))?",
                r"(?=.*🏁\s*(?P<after>[^\s]*))?",
                r".*$",
            ])
        )
    )


@app.function
def compute_last_planned(df):
    return df["last_seen"] + to_timedelta(
        df["day"]
        .map({
            "Monday": 0,
            "Tuesday – Thursday": 1,  # ruff: ignore[ambiguous-unicode-character-string],
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
        })
        .sub(df["last_seen"].dt.weekday)
        .add(7)
        .mod(7)
        .replace(0, 7)
        .fillna(NaT),
        unit="D",
    )


@app.function
def update_task(row):
    q = row.to_dict()
    path = data["personal"] / q["path"]
    lines = path.read_text(encoding="utf-8").splitlines(True)
    lines[q["line"] - 1] = sub(
        rf"\s+{q['priority']}", q["new_priority"], lines[q["line"] - 1]
    )
    path.write_text("".join(lines), encoding="utf-8")
    return row


@app.function
def get_tasks() -> DataFrame:
    last_seen: dict[str, datetime] = {
        k: datetime.fromisoformat(v)
        for k, v in loads(data["seen_plans"].read_text(encoding="utf-8")).items()
    }
    priorities = ["", "🔺", "⏫", "🔼", "🔽", "⏬"]
    days = dict(
        zip(
            [
                "This week",
                "Friday",
                "Saturday",
                "Sunday",
                "Monday",
                "Tuesday – Thursday",  # ruff: ignore[ambiguous-unicode-character-string]
            ],
            priorities,
            strict=True,
        )
    )
    return DataFrame(
        columns=[
            "status",
            "text",
            "path",
            "line",
            "tags",
            "task",
            "id",
            "deps",
            "priority",
            "recurs",
            "created",
            "starts",
            "scheduled",
            "due",
            "cancelled",
            "done",
            "after",
            "last_seen",
            "entry",
            "day",
            "last_planned",
            "new_priority",
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
        )
        .pipe(extract_task_data, priorities)
        .loc[~col("path").str.contains("_Ω")]
        .assign(**{
            "task": col("task")
            .str.replace(r"\[([^\]]+)\]\([^)]*\)", r"\1", regex=True)
            .str.replace(r"\s{2,}", " ", regex=True)
            .str.strip(),
            "entry": "[" + col("task") + "](" + col("path") + ")",
            "created": col("created").astype("datetime64[s, UTC]"),
            "starts": col("starts").astype("datetime64[s, UTC]"),
            "scheduled": col("scheduled").astype("datetime64[s, UTC]"),
            "due": col("due").astype("datetime64[s, UTC]"),
            "cancelled": col("cancelled")
            .where((col("status") != "-") | col("cancelled").notna(), date.min)
            .astype("datetime64[s, UTC]"),
            "done": col("done")
            .where((col("status") != "x") | col("done").notna(), date.min)
            .astype("datetime64[s, UTC]"),
            "priority": col("priority")
            .fillna("")
            .astype(CategoricalDtype(ordered=True, categories=priorities)),
            "day": col("priority").pipe(get_days, days),
            "last_seen": lambda df: (
                df["id"]
                .map(last_seen)
                .fillna(get_now())
                .astype("datetime64[s, UTC]")
                .dt.tz_convert(current_tz)
                .dt.normalize()
            ),
            "last_planned": lambda df: df.pipe(compute_last_planned),
            "new_priority": col("priority").where(col("last_planned") > get_now(), ""),
        }),
    )


@app.function
def demote_task(row):
    task = row.to_dict()
    path = data["personal"] / task["path"]
    lines = path.read_text(encoding="utf-8").splitlines(True)
    lines[task["line"] - 1] = sub(
        rf"- \[{task['status']}\]", "- #task", lines[task["line"] - 1]
    )
    path.write_text("".join(lines), encoding="utf-8")
    return row


@app.cell
def _():
    tasks = get_tasks()
    disp(tasks=tasks)
    return (tasks,)


@app.cell
def _(tasks):
    DEMOTE_TASKS = False  # ! Don't enable this unless you want to modify the vault
    DEMOTE_TASKS_DONE_LATER_THAN_MONTHS_AGO = 3
    TASKS_TO_DEMOTE = 0

    planned_meta_task = tasks.loc[(col("id") == "zzzzzz")]
    reprioritize_meta_task = tasks.loc[(col("id") == "xxxxxx")]
    is_planned = col("id").isin(one(planned_meta_task["deps"].str.split(",")))
    do_reprioritize = col("id").isin(one(reprioritize_meta_task["deps"].str.split(",")))
    is_active = col("cancelled").isna() & col("done").isna()
    demotable_tasks = tasks.loc[
        col("deps").isna()
        & col("id").isna()
        & col("done").notna()
        & ~is_planned
        & ~do_reprioritize
        & (
            col("done")
            < (
                Timestamp.today().normalize()
                - DateOffset(months=DEMOTE_TASKS_DONE_LATER_THAN_MONTHS_AGO)
            ).tz_localize("UTC")
        )
    ].sort_values("done")
    tasks_to_demote = demotable_tasks.head(TASKS_TO_DEMOTE)
    if DEMOTE_TASKS:
        tasks_to_demote.apply(demote_task, axis="columns")
    disp(tasks_to_demote=tasks_to_demote, demotable_tasks=demotable_tasks)
    return do_reprioritize, is_active, is_planned


@app.cell
def _(do_reprioritize, is_active, is_planned, tasks):
    plans = tasks.sort_values("day", na_position="first")
    inactive_plans = plans.loc[~is_active & (is_planned | do_reprioritize)]
    active_plans = plans.loc[is_active & is_planned]
    reprioritize = tasks.loc[is_active & do_reprioritize]
    mo.vstack(
        items=[
            mo.md(
                "No inactive plans"
                if inactive_plans.empty
                else dedent(f"""
            Regular expression to strip inactive plans from `__plan/plans.md`. **NOTE: Fix any double-commas after manually find/replace!**:

            {inactive_plans.id.str.cat(sep=",|")}
        """)
            ),
            mo.ui.table(label="inactive_plans", data=inactive_plans),
            mo.ui.table(label="active_plans", data=active_plans),
            mo.ui.table(label="reprioritize", data=reprioritize),
        ]
    )
    return active_plans, plans


@app.cell
def _(active_plans, is_active, tasks):
    eternal_active_plans = active_plans.loc[
        col("status").isin(["A", "d"]) & ~col("path").str.startswith("__")
    ]
    related_tasks = (
        tasks
        .merge(
            eternal_active_plans[["path", "id"]].rename(columns={"id": "related_id"}),
            on="path",
            how="left",
            validate="many_to_one",
        )
        .loc[
            is_active
            & ~col("path").str.startswith("__")
            & col("path").isin(eternal_active_plans["path"])
            & (col("id") != col("related_id"))
            & (col("priority") == "")
        ]
        .assign(**{
            "entry": (
                col("entry").fillna("").astype(str)
                + " 🆔 "
                + col("related_id").fillna("").astype(str)
            ).str.strip()
        })
    )
    mo.vstack(
        items=[
            mo.ui.table(label="eternal_plans", data=eternal_active_plans),
            mo.ui.table(label="related_tasks", data=related_tasks),
        ]
    )
    return (related_tasks,)


@app.cell
def _(is_planned, plans):
    _planned_no_priority = plans.loc[is_planned & (col("priority") == "")]
    mo.vstack(
        items=[
            mo.md(
                "Regular expression to strip unprioritized plans from `__plan/plans.md`. **NOTE: Fix any double-commas after manually find/replace!**:"
            ),
            mo.md(
                "No unprioritized plans"
                if _planned_no_priority.empty
                else _planned_no_priority.id.str.cat(sep=",|")
            ),
            mo.md(
                'IDs to add to the "Reprioritize" meta plan (🆔 xxxxxx) in `__plan/plans.md`.:'
            ),
            mo.md(
                "No unprioritized plans"
                if _planned_no_priority.empty
                else _planned_no_priority.id.str.cat(sep=",")
            ),
            mo.ui.table(label="_planned_no_priority", data=_planned_no_priority),
        ]
    )
    return


@app.cell
def _(active_plans):
    # sourcery skip: remove-redundant-if
    DEMOTE_PLANS = False  # ! Don't enable this unless you want to modify the vault

    to_reset = active_plans.loc[col("priority") != col("new_priority")]
    if DEMOTE_PLANS:  # ty: ignore[redundant-condition-strict]
        # TODO: Remove entries from "seen_plans" if they were updated here
        data["seen_plans"].write_text(
            dumps(
                active_plans
                .set_index("id")["last_seen"]
                .apply(lambda ts: ts.isoformat())
                .to_dict()
            ),
            encoding="utf-8",
        )
        to_reset.apply(update_task, axis="columns")
    mo.ui.table(to_reset)
    return


@app.cell
def _(active_plans, related_tasks):
    # sourcery skip: move-assign-in-block, use-fstring-for-concatenation
    UPDATE_WEEK_PLAN = False  # ! Don't enable this unless you want to modify the vault

    day_plan = """
    - 08
    - 10
    - 12
    - 14
    - 16
    - 18
    - **Plan**"""
    weekday_group_index = {
        4: 0,  # Friday
        5: 1,  # Saturday
        6: 2,  # Sunday
        0: 3,  # Monday
        1: 4,  # Tuesday
        2: 4,  # Wednesday
        3: 4,  # Thursday
    }
    start = weekday_group_index[get_now().weekday()]
    groups = ["Friday", "Saturday", "Sunday", "Monday", "Tuesday – Thursday"]  # ruff: ignore[ambiguous-unicode-character-string]
    ordered_groups = groups[start:] + groups[:start]
    day_plans = {
        day: "" if day == "Tuesday – Thursday" else day_plan  # ruff: ignore[ambiguous-unicode-character-string]
        for day in ordered_groups
    }
    week_plan = (
        """\
    ### <% `Week plan (${tp.obsidian.moment().format(tp.user.getDateFmt())})` %>
    """
        + "".join(
            active_plans
            .loc[col("day") != "This week"]
            .set_index("day")[["entry"]]
            .groupby("day")
            .agg(
                lambda ser: (
                    f"""
    - **{ser.index.get_level_values("day")[0]}**{day_plans[ser.index.get_level_values("day")[0]]}"""
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
            .reindex(ordered_groups)
            .dropna(subset=["entry"])["entry"]
            .tolist()
        )
        + """
    - **This week**
    """
        + "\n".join(
            active_plans.loc[col("day") == "This week"]["entry"].apply(
                lambda ser: "- " + ser
            )
        )
        +
        # TODO: Task headers for the parent task for each related task
        """
    - **Related**
    """
        + "\n".join(related_tasks["entry"].apply(lambda ser: "- " + ser))
    )

    if UPDATE_WEEK_PLAN:
        (data["personal"] / "_Ω/Snip/Week plan.md").write_text(
            encoding="utf-8", data=week_plan
        )

    mo.md(week_plan)
    return


@app.cell
def _():
    # TODO: Implement plan reprioritization
    REPRIORITIZE_TASKS = (  # ! Don't enable this unless you want to modify the vault
        False
    )

    if not REPRIORITIZE_TASKS:  # ty: ignore[redundant-condition-strict]
        mo.stop(True)

    # # # Render to Markdown and save the times that items were first seen
    # # PARAMS.paths.plan.write_text(encoding="utf-8", data=render(tokens))
    # # PARAMS.paths.seen_plans.write_text(
    # #     encoding="utf-8",
    # #     data=f"{ser_json({k: ser_datetime(v) for k, v in seen.items()})}\n",
    # # )
    # # invoke_obsidian_command("app:reload")

    # START_OF_DAY = get_time_today(time(0))
    # PLANS = {
    #     "Reminders": Plan(min_datetime, ""),
    #     "Now": Plan(get_now() - timedelta(hours=2), "Today"),
    #     "Today": Plan(START_OF_DAY, "This week"),
    #     "This week": Plan(START_OF_DAY - timedelta(days=7), "Reprioritize"),
    #     "Reprioritize": Plan(min_datetime, ""),
    # }
    # PLAN_PAT = r"^-\s\[\s\]\s#hide\s(?P<kind>.+)(?P<id>\s🆔.+?)(?:\s⛔\s(?P<items>.+))?$"
    # seen: dict[str, datetime] = {}
    # kinds: dict[str, Kind] = defaultdict(Kind)
    # for plan in plans:
    #     if not (match := only(finditer(PLAN_PAT, plan))) or not (
    #         plan := PLANS.get(match["kind"])
    #     ):
    #         continue
    #     # Check for old items in the plan
    #     for item in match["items"].split(","):
    #         if (
    #             False  # TODO: Reimplement done filter
    #             and not (
    #                 matches := tasks[tasks.text.str.contains(rf"\s🆔 {item}", na=False)][
    #                     ["text", "done"]
    #                 ]
    #             ).empty
    #             and all(matches.done)
    #         ):
    #             continue
    #         kinds[match["kind"]].match = match
    #         if not match["items"]:
    #             continue
    #         seen_time = last_seen.get(item) or get_now()
    #         # TODO: Reimplement cutoff
    #         if False or seen_time < plan.cutoff:
    #             # An item seen before the cutoff will be moved, forget that it was seen
    #             kinds[plan.destination].plans.append(item)
    #         else:
    #             # Otherwise the item stays put and the first time it was seen is kept
    #             kinds[match["kind"]].plans.append(item)
    #             seen[item] = seen_time
    # # Update plan items
    # for kind in kinds.values():
    #     if not kind.match:
    #         continue
    #     kind.content = get_plan(kind.match, kind.plans)
    #     if not kind.content or not kind.match:
    #         continue
    #     if match := only(finditer(PLAN_PAT, kind.content)):
    #         if match["items"] and match["kind"] == "Now":
    #             ", ".join([f"🆔 {i}" for i in match["items"].split(",")])
    #         kind.match = match
    # kinds
    return


if __name__ == "__main__":
    app.run()
