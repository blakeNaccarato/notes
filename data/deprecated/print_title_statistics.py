"""Print population statistics.

Given a directory of PDFs with the filename format 'YYYY, Author, Title', get the
Title part and count the words in it. Print statistics on the population of titles.
"""

from pathlib import Path
from statistics import mean, median, stdev

cwd = Path()
num_words_all = []

for item in cwd.iterdir():
    if item.suffix == ".pdf":
        title = item.stem.split(", ")[-1]
        num_words = len(title.split())
        num_words_all.append(num_words)

print(  # noqa: T201
    f"Number of words in academic papers in the {cwd.resolve().stem} directory:\n"
    f"Mean: {mean(num_words_all):.1f}\n"
    f"Median: {median(num_words_all):.1f}\n"
    f"Sample standard deviaton: {stdev(num_words_all):.1f}\n"
)
