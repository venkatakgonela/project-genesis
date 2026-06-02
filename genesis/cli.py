"""Genesis CLI — Typer application entry point."""

from __future__ import annotations

import typer

from genesis import __version__
from genesis.commands import brief, init, migrate, new, task

app = typer.Typer(
    name="genesis",
    help=(
        "**Genesis** — AI Engineering Operating System (AI-EOS) generator.\n\n"
        "Bootstrap and maintain a structured AI operating context inside any "
        "software project."
    ),
    no_args_is_help=True,
    rich_markup_mode="markdown",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"genesis {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show the genesis version and exit.",
    ),
) -> None:
    """Genesis — AI-EOS generator."""


# ---------------------------------------------------------------------------
# v1 commands
# ---------------------------------------------------------------------------
app.command("init")(init.run)
app.command("new")(new.run)
app.command("brief")(brief.run)
app.command("task")(task.run)
app.command("migrate")(migrate.run)


# ---------------------------------------------------------------------------
# Reserved commands — stubs only, not implemented in v1
# ---------------------------------------------------------------------------
def _reserved(name: str) -> None:
    typer.echo(
        f"  `genesis {name}` is reserved for a future version of Genesis.",
        err=True,
    )
    raise typer.Exit(code=1)


@app.command(hidden=True)
def analyze() -> None:
    """[v2] Analyse project structure against AI-EOS standards."""
    _reserved("analyze")


@app.command(hidden=True)
def doctor() -> None:
    """[v2] Diagnose AI-EOS health and surface configuration issues."""
    _reserved("doctor")


@app.command(hidden=True)
def refresh() -> None:
    """[v2] Refresh AI-EOS documents from updated templates."""
    _reserved("refresh")
