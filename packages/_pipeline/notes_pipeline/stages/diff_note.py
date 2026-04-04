from pathlib import Path
from re import MULTILINE, finditer

from unidiff import PatchSet

text = Path("data/_notetaking.diff").read_text(encoding="utf-8")
print(  # noqa: T201
    *(
        m.group("content")
        for m in finditer(
            pattern=r"^[^\s]\s+(?P<content>.+)$", string=text, flags=MULTILINE
        )
    ),
    end="\n",
)
print(PatchSet.from_string(text))  # noqa: T201
