"""Fixture CLI with --json on every command."""

import typer

app = typer.Typer()


@app.command()
def score(path: str = ".", json: bool = typer.Option(False, "--json"), category: str = typer.Option(None, "--category")) -> None:
    """Score a path."""


@app.command()
def explain(check_id: str, json: bool = typer.Option(False, "--json")) -> None:
    """Explain a check."""
