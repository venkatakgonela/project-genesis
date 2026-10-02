"""genesis new — create a new project folder with AI-EOS scaffolding."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import typer

from genesis import __version__
from genesis.scaffold import ensure_dir, scaffold_project


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
    target_dir = Path.cwd() / name
    ensure_dir(target_dir)

    created_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    context: dict[str, object] = {
        "genesis_version": __version__,
        "created": created_time,
        "project_name": name,
        "project_type": type_,
        "project_owner": "TBD",
        "project_description": "TBD",
        "archetype": "default",
    }

    written, skipped = scaffold_project(target_dir, context, force=False)

    typer.echo("Created new AI-EOS project.")
    typer.echo(f"  Project folder: {target_dir}")
    typer.echo(f"  Files written: {written}")
    typer.echo(f"  Files skipped: {skipped}")
