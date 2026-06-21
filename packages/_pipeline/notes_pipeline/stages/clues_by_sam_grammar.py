import marimo

__generated_with = "0.23.9"
app = marimo.App()

with app.setup:
    from dataclasses import asdict, fields
    from itertools import chain
    from pathlib import Path

    import marimo as mo
    from lark import Lark, Tree
    from pandas import DataFrame, col

    from notes_pipeline.data import get_data
    from notes_pipeline.stages.clues_by_sam import Suspect, parse_suspects

    data = get_data(Path.cwd())
    mo.json(data)


@app.function
def parse_hint(text: str) -> Tree:
    return Lark(Path("clues-by-sam.lark").read_text(encoding="utf-8")).parse(text)


@app.cell
def _():
    # TODO: Assign coordinate position and special positions (e.g. edge, corner)
    # TODO: Consider precomputing neighbors
    hidden_suspect_cols = [
        _field.name
        for _field in fields(Suspect)
        if _field.name not in ["name", "profession", "hint"]
    ]
    suspects = DataFrame(
        data=[
            asdict(_sus)
            for _sus in chain.from_iterable([
                parse_suspects(
                    Path(data["clues_by_sam"] / f"2026-06-{_day}-card-grid.html").read_text(
                        encoding="utf-8"
                    )
                ).stack()
                for _day in range(14, 21)
            ])
        ]
    )
    mo.vstack(
        items=[
            mo.ui.table(
                label="Suspect",
                hidden_columns=hidden_suspect_cols,
                wrapped_columns=["hint"],
                data=suspects.loc[col("hint") != ""],
            )
        ]
    )
    return hidden_suspect_cols, suspects


@app.cell
def _(hidden_suspect_cols, suspects):
    suspects_with_hints = suspects.loc[col("hint") != ""].assign(**{
        "tree": col("hint").map(parse_hint),
        "pretty": col("tree").map(lambda tree: tree.pretty().strip()),
        "rule": col("tree").map(lambda tree: tree.data),
        "children": col("tree").map(lambda tree: tree.children),
    })
    mo.vstack(
        items=[
            mo.ui.table(
                label="Suspects with hints",
                hidden_columns=[
                    *hidden_suspect_cols,
                    "profession",
                    "tree",
                    "rule",
                    "children",
                ],
                wrapped_columns=["hint", "pretty"],
                data=suspects_with_hints.sort_values("rule").reset_index(drop=True),
            )
        ]
    )
    return


@app.cell
def _(suspects):
    _hints = [
        f'h{_i}: "{_hint}"'
        for _i, _hint in enumerate(suspects["hint"].drop_duplicates().sort_values())
        if _hint
    ]
    mo.vstack(
        items=[
            mo.md("#### Start"),
            mo.ui.code_editor(
                disabled=True,
                value="?start: "
                + " | ".join([_hint.split(":")[0].strip() for _hint in _hints])
                + " | unknown",
            ),
            mo.md("#### Trivial rules"),
            mo.ui.code_editor(disabled=True, value="\n".join(_hints)),
            mo.md("#### Names"),
            mo.ui.code_editor(
                disabled=True,
                value=" | ".join([
                    f'"{_name}"i'
                    for _name in suspects["name"].drop_duplicates().sort_values()
                ]),
            ),
            mo.md("#### Professions"),
            mo.ui.code_editor(
                disabled=True,
                value=" | ".join([
                    f'"{_prof}"i'
                    for _prof in suspects["profession"].drop_duplicates().sort_values()
                ]),
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
