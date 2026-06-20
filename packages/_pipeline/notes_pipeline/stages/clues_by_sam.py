# /// script
# [tool.marimo.display]
# theme = "dark"
# width = "full"
# ///

import marimo

__generated_with = "0.23.9"
app = marimo.App()

with app.setup:
    from dataclasses import asdict, dataclass
    from pathlib import Path
    from typing import Literal

    import marimo as mo
    from bs4 import BeautifulSoup
    from more_itertools import one
    from numpy import where
    from pandas import DataFrame

    from notes_pipeline.data import get_data

    data = get_data(Path.cwd())
    mo.json(data)

    type Column = Literal["A", "B", "C", "D"]
    type Profession = Literal[
        "cop",
        "doctor",
        "dog",
        "farmer",
        "guard",
        "mech",
        "painter",
        "singer",
        "sleuth",
        "teacher",
    ]
    type Status = Literal["unknown", "criminal", "innocent"]


@app.class_definition
@dataclass
class Coord:
    col: Column
    row: int


@app.class_definition
@dataclass
class Card:
    coord: Coord
    name: str
    face: str
    profession: Profession
    flipped: bool
    innocent: bool
    hint: str


@app.class_definition
@dataclass
class Suspect:
    name: str
    face: str
    profession: Profession
    hint: str
    status: Status = "unknown"
    done: bool = False


@app.function
def parse_suspects(html: str) -> DataFrame[Suspect]:
    data: dict[Column, list[Suspect]] = {key: [] for key in ["A", "B", "C", "D"]}  # ty:ignore[invalid-assignment]
    for card in [
        Card(
            coord=Coord(*[  # ty:ignore[invalid-argument-type]
                int(e) if i else e
                for i, e in enumerate(card.select_one(".coord").get_text(strip=True))
            ]),
            name=card.select_one(".name h3.name").get_text(strip=True),
            face=(
                card.select_one(".card-front .face")
                or card.select_one(".card-back .face")
            ).get_text(strip=True),
            profession=card.select_one(".profession").get_text(strip=True),
            flipped="flipped" in (card.get("class") or []),
            innocent="innocent" in (card.get("class") or []),
            hint=hint_tag.get_text(strip=True)
            if (hint_tag := card.select_one("p.hint:not(.flavour)"))
            else "",
        )
        for card in BeautifulSoup(html, "html.parser").select(".card-container .card")
    ]:
        data[card.coord.col].append(
            Suspect(
                name=card.name,
                face=card.face,
                profession=card.profession,
                status="innocent"
                if card.innocent
                else "criminal"
                if card.flipped
                else "unknown",
                hint=card.hint,
            )
        )
    return DataFrame(index=range(1, 6), data=data)


@app.function
def get_neighbors(suspects: DataFrame[Suspect], name: str) -> list[Suspect]:
    row, col = (
        one(idx) for idx in where(suspects.map(lambda suspect: suspect.name) == name)
    )
    return [
        suspects.iloc[r, c]
        for r in range(max(row - 1, 0), min(row + 2, suspects.shape[0]))
        for c in range(max(col - 1, 0), min(col + 2, suspects.shape[1]))
        if (r, c) != (row, col)
    ]


@app.cell
def _():
    suspects = parse_suspects(
        Path(data["clues_by_sam"] / "2026-06-15-card-grid.html").read_text(encoding="utf-8")
    )
    return (suspects,)


@app.cell
def _(suspects):
    mo.vstack(
        align="stretch",
        heights="equal",
        items=[
            mo.hstack(
                align="stretch",
                widths="equal",
                items=[
                    mo.ui.button(
                        full_width=True,
                        label=" ".join([
                            v
                            for k, v in asdict(_sus).items()
                            if k not in ["hint", "done", "status"]
                        ]),
                        kind="success"
                        if _sus.status == "innocent"
                        else "danger"
                        if _sus.status == "criminal"
                        else "neutral",
                    )
                    for col in range(suspects.shape[1])
                    if (_sus := suspects.iloc[row, col]) or True
                ],
            )
            for row in range(suspects.shape[0])
        ],
    )
    return


@app.cell
def _(suspects):
    tabs = mo.ui.tabs({
        "Scenario": mo.vstack(
            align="stretch",
            heights="equal",
            items=[
                mo.hstack(
                    align="stretch",
                    widths="equal",
                    items=[
                        mo.ui.button(
                            full_width=True,
                            label=" ".join([
                                v
                                for k, v in asdict(_sus).items()
                                if k not in ["hint", "done", "status"]
                            ]),
                            kind="success"
                            if _sus.status == "innocent"
                            else "danger"
                            if _sus.status == "criminal"
                            else "neutral",
                        )
                        for col in range(suspects.shape[1])
                        if (_sus := suspects.iloc[row, col]) or True
                    ],
                )
                for row in range(suspects.shape[0])
            ],
        ),
        "A": mo.vstack(
            align="stretch",
            heights="equal",
            items=[
                mo.hstack(
                    align="stretch",
                    widths="equal",
                    items=[
                        mo.ui.button(
                            full_width=True,
                            label=" ".join([
                                v
                                for k, v in asdict(_sus).items()
                                if k not in ["hint", "done", "status"]
                            ]),
                            kind="success"
                            if _sus.status == "innocent"
                            else "danger"
                            if _sus.status == "criminal"
                            else "neutral",
                        )
                        for col in range(suspects.shape[1])
                        if (_sus := suspects.iloc[row, col]) or True
                    ],
                )
                for row in range(suspects.shape[0])
            ],
        ),
        "B": mo.vstack(
            align="stretch",
            heights="equal",
            items=[
                mo.hstack(
                    align="stretch",
                    widths="equal",
                    items=[
                        mo.ui.button(
                            full_width=True,
                            label=" ".join([
                                v
                                for k, v in asdict(_sus).items()
                                if k not in ["hint", "done", "status"]
                            ]),
                            kind="success"
                            if _sus.status == "innocent"
                            else "danger"
                            if _sus.status == "criminal"
                            else "neutral",
                        )
                        for col in range(suspects.shape[1])
                        if (_sus := suspects.iloc[row, col]) or True
                    ],
                )
                for row in range(suspects.shape[0])
            ],
        ),
    })
    tabs
    return


@app.cell
def _(suspects):
    mo.ui.table([_hint for _hint in suspects.map(lambda sus: sus.hint).stack() if _hint])
    return


@app.cell
def _():
    # statuses: dict[tuple[int, Column], Status] = {
    #     (1, "A"): "criminal",  # Amy
    #     (1, "B"): "innocent",  # Bunty
    #     (1, "C"): "innocent",  # Daniel
    #     (1, "D"): "criminal",  # Eric
    #     (2, "A"): "criminal",  # Frida
    #     (2, "B"): "innocent",  # Ghani
    #     (2, "C"): "criminal",  # Hope
    #     (2, "D"): "criminal",  # Ike
    #     (3, "A"): "criminal",  # Joy
    #     (3, "B"): "innocent",  # Martin
    #     (3, "C"): "innocent",  # Olivia
    #     (3, "D"): "innocent",  # Paul
    #     (4, "A"): "innocent",  # Quita
    #     (4, "B"): "innocent",  # Rohan
    #     (4, "C"): "innocent",  # Salil
    #     (4, "D"): "innocent",  # Uma
    #     (5, "A"): "criminal",  # Vicky
    #     (5, "B"): "innocent",  # Wally
    #     (5, "C"): "criminal",  # Xavi
    #     (5, "D"): "criminal",  # Zoe
    # }
    # for coord, status in statuses.items():
    #     row, col = coord
    #     suspects.loc[row, col].status = status

    # clues = {
    #     (1, "A"): lambda suspects: (
    #         len(
    #             suspects.loc[  # Amy
    #                 3,
    #                 (
    #                     suspects.loc[3].map(lambda suspect: suspect.status == "criminal")
    #                     & suspects.loc[4].map(lambda suspect: suspect.status == "innocent")
    #                 ),
    #             ]
    #         )
    #         == 1
    #     ),
    #     (1, "B"): lambda suspects: bool(
    #         len([
    #             suspect
    #             for suspect in get_neighbors(suspects, "ike")
    #             if suspect.status == "innocent"
    #         ])
    #         % 2
    #     ),
    #     # TODO: Encode L/R/U/D clues by simple loc operations
    #     # TODO: May also need to use set unions e.g. "|" as needed
    #     # TODO: Be sure using correct syntax for Pandas bool masks
    #     (1, "C"): lambda suspects: False,
    #     (2, "A"): lambda suspects: False,
    #     (2, "B"): lambda suspects: False,
    #     (3, "A"): lambda suspects: False,
    #     (3, "B"): lambda suspects: False,
    #     (4, "B"): lambda suspects: False,
    #     (4, "C"): lambda suspects: False,
    #     (4, "D"): lambda suspects: False,
    #     (5, "B"): lambda suspects: False,
    # }
    # mo.vstack([
    #     mo.ui.table(
    #         suspects.map(
    #             lambda suspect: " ".join(
    #                 [str(value) for value in asdict(suspect).values()][:4]
    #             )
    #         )
    #     ),
    #     mo.ui.table({
    #         suspects.loc[*coord].name: suspects.pipe(clue) for coord, clue in clues.items()
    #     }),
    # ])
    return


if __name__ == "__main__":
    app.run()
