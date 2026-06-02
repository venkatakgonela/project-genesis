"""genesis init — initialise AI-EOS in the current directory."""

from __future__ import annotations

import typer


def run(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files instead of skipping them.",
    ),
) -> None:
    """Initialise AI-EOS in the current directory.

    Writes the full AI-EOS folder structure (AGENTS.md, ai/, .ai-eos.yaml)
    into the current working directory. Existing files are skipped unless
    ``--force`` is passed.
    """
    typer.echo("⚠  genesis init is not yet implemented.", err=True)
    raise typer.Exit(code=1)
