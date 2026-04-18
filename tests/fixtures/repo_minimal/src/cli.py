"""Typer CLI with no --json flag -- intentionally bad."""

import typer

app = typer.Typer()


@app.command()
def run(path: str = ".") -> None:
    """Run without --json."""
