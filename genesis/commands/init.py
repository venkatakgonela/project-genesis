"""genesis init — initialise AI-EOS in the current directory."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import typer

from genesis import __version__
from genesis.scaffold import scaffold_project


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
    target_dir = Path.cwd()
    created_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    context: dict[str, object] = {
        "genesis_version": __version__,
        "created": created_time,
        "project_name": target_dir.name,
        "project_type": "default",
        "project_owner": "TBD",
        "project_description": "TBD",
        "archetype": "default",
    }

    written, skipped = scaffold_project(target_dir, context, force=force)

    typer.echo("Initialized AI-EOS project.")
    typer.echo(f"  Target directory: {target_dir}")
    typer.echo(f"  Files written: {written}")
    typer.echo(f"  Files skipped: {skipped}")
