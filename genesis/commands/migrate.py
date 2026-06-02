"""genesis migrate — add missing AI-EOS files to an existing project."""

from __future__ import annotations

import typer


def run(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be added without writing any files.",
    ),
) -> None:
    """Migrate project to the current AI-EOS structure.

    Compares the project's existing ``ai/`` structure against the canonical
    AI-EOS manifest (the same file list used by ``genesis init``).

    Only **missing** files and directories are added — existing content is
    never modified.

    Use ``--dry-run`` to preview changes without writing to disk.
    """
    typer.echo("⚠  genesis migrate is not yet implemented.", err=True)
    raise typer.Exit(code=1)
