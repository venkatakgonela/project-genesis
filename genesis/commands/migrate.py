"""genesis migrate — add missing AI-EOS files to an existing project."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import typer

from genesis import __version__
from genesis.manifest import TEMPLATES, parse_ai_eos_yaml
from genesis.scaffold import write_file
from genesis.template_engine import render


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
    target_dir = Path.cwd()
    created_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Read existing yaml metadata if present
    yaml_path = target_dir / ".ai-eos.yaml"
    parsed_meta = parse_ai_eos_yaml(yaml_path)

    # Form the context using defaults, overriding with parsed metadata if found
    context: dict[str, object] = {
        "genesis_version": parsed_meta.get("genesis_version", __version__),
        "created": created_time,
        "project_name": parsed_meta.get("project_name", target_dir.name),
        "project_type": parsed_meta.get("project_type", "default"),
        "project_owner": parsed_meta.get("project_owner", "TBD"),
        "project_description": parsed_meta.get("project_description", "TBD"),
        "archetype": parsed_meta.get("archetype", "default"),
    }

    # Classify files into missing and existing lists
    would_create: list[tuple[str, Path]] = []
    already_exists: list[tuple[str, Path]] = []

    for _template_name, rel_path in TEMPLATES.items():
        dest_path = target_dir / rel_path
        if dest_path.is_file():
            already_exists.append((rel_path, dest_path))
        else:
            would_create.append((rel_path, dest_path))

    if dry_run:
        typer.echo("Dry-run: no files will be written.")
        # Sort files by path for deterministic output
        for rel_path, _ in sorted(would_create, key=lambda x: x[0]):
            typer.echo(f"  [would create]  {rel_path}")
        for rel_path, _ in sorted(already_exists, key=lambda x: x[0]):
            typer.echo(f"  [already exists] {rel_path}")

        typer.echo(f"  Target directory: {target_dir}")
        typer.echo(f"  Would create:   {len(would_create)}")
        typer.echo(f"  Already exists: {len(already_exists)}")
        typer.echo("  Dry run:        True")
    else:
        written = 0
        skipped = 0

        # Render and write missing files
        for template_name, rel_path in TEMPLATES.items():
            dest_path = target_dir / rel_path
            if dest_path.is_file():
                skipped += 1
            else:
                content = render(template_name, context)
                if write_file(dest_path, content, force=False):
                    written += 1
                else:
                    skipped += 1

        typer.echo("Migrating AI-EOS structure...")
        typer.echo(f"  Target directory: {target_dir}")
        typer.echo(f"  Files created:  {written}")
        typer.echo(f"  Files skipped:  {skipped}")
        typer.echo("  Dry run:        False")
