"""genesis new — create a new project folder with AI-EOS scaffolding."""

from __future__ import annotations

import typer


def run(
    name: str = typer.Option(..., "--name", "-n", help="Project name."),
    type_: str = typer.Option(
        "default",
        "--type",
        "-t",
        help="Project archetype type (e.g. python-api, data-pipeline).",
    ),
) -> None:
    """Create a new sub-folder with full AI-EOS scaffolding.

    Creates ``<name>/`` inside the current directory, writes the AI-EOS
    structure into it, and records the project metadata in ``.ai-eos.yaml``.
    """
    typer.echo("⚠  genesis new is not yet implemented.", err=True)
    raise typer.Exit(code=1)
