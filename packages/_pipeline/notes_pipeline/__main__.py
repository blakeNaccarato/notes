"""Command-line interface."""

from cappa import invoke

from notes_pipeline.cli import Pipeline


def main():
    """CLI entry-point."""
    invoke(Pipeline)  # ty: ignore[not-callable]


if __name__ == "__main__":
    main()
