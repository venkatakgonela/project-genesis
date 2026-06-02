"""genesis brief — generate AI-EOS documents from a project brief file."""

from __future__ import annotations

from pathlib import Path

import typer


def run(
    brief_file: Path = typer.Argument(  # noqa: B008
        ...,
        help="Path to the project brief Markdown file (with YAML front matter).",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing AI-EOS documents.",
    ),
) -> None:
    """Generate AI-EOS documents from a project brief.

    Reads the brief file, extracts front matter metadata (title, type, owner,
    description), and renders the AI-EOS document templates with those values
    into the current directory's ``ai/`` folder.

    Brief format::

        ---
        title: Payments Service
        type: python-api
        owner: platform-team
        description: Handles all payment processing workflows.
        ---

        Free-form background text...
    """
    typer.echo("⚠  genesis brief is not yet implemented.", err=True)
    raise typer.Exit(code=1)
