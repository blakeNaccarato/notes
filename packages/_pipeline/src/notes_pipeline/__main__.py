"""Command-line interface."""

from notes_pipeline.cli import Pipeline
from notes_pipeline.parser import invoke


def main():
    """CLI entry-point."""
    invoke(Pipeline)


if __name__ == "__main__":
    main()
