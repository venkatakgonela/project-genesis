"""genesis brief — generate AI-EOS documents from a project brief file."""

from __future__ import annotations

import re
from datetime import UTC, datetime
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
    try:
        content = brief_file.read_text(encoding="utf-8")
    except Exception as e:
        typer.echo(f"Error reading brief file: {e}", err=True)
        raise typer.Exit(code=1) from None

    from genesis import frontmatter

    try:
        meta, body = frontmatter.parse(content)
    except ValueError as e:
        typer.echo(f"Front matter parsing error: {e}", err=True)
        raise typer.Exit(code=1) from None

    # Now parse headings from body

    def normalize_section_name(name: str) -> str | None:
        norm = name.strip().lower()
        if norm == "purpose":
            return "purpose"
        if norm == "users":
            return "users"
        if norm == "requirements":
            return "requirements"
        if norm == "constraints":
            return "constraints"
        if norm == "scope":
            return "scope"
        if norm in ("non goals", "non-goals", "nongoals"):
            return "non_goals"
        return None

    lines = body.split("\n")
    parsed_sections: dict[str, list[str]] = {}
    sections_discovered: list[str] = []

    active_section: str | None = None
    active_level = 0

    for line in lines:
        stripped = line.strip()
        # Check if line is a heading: starts with one or more '#' followed by space
        if stripped.startswith("#"):
            header_match = re.match(r"^(#+)\s+(.+)$", stripped)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                sec_key = normalize_section_name(title)

                if sec_key is not None:
                    active_section = sec_key
                    active_level = level
                    if active_section not in parsed_sections:
                        parsed_sections[active_section] = []

                    standard_names = {
                        "purpose": "Purpose",
                        "users": "Users",
                        "requirements": "Requirements",
                        "constraints": "Constraints",
                        "scope": "Scope",
                        "non_goals": "Non Goals",
                    }
                    disp = standard_names[sec_key]
                    if disp not in sections_discovered:
                        sections_discovered.append(disp)
                    # Skip writing the header itself into the section content
                    continue
                else:
                    # Heading did not match target section.
                    # Deactivate if the header level is less than or equal to active heading level
                    if level <= active_level:
                        active_section = None
                        active_level = 0

        # If we have an active section and this is a regular line (or subheader), append it
        if active_section is not None:
            parsed_sections[active_section].append(line)

    # Clean sections
    cleaned_sections: dict[str, str] = {}
    for key in [
        "purpose",
        "users",
        "requirements",
        "constraints",
        "scope",
        "non_goals",
    ]:
        if key in parsed_sections:
            cleaned_sections[key] = "\n".join(parsed_sections[key]).strip()
        else:
            cleaned_sections[key] = ""

    from genesis import __version__
    from genesis.scaffold import scaffold_project

    created_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    project_name = meta.get("project_name") or meta.get("title") or Path.cwd().name
    project_type = meta.get("project_type") or meta.get("type") or "default"
    project_owner = meta.get("project_owner") or meta.get("owner") or "TBD"

    # Map Purpose section to project_description if not in meta
    purpose_val = cleaned_sections.get("purpose", "")
    project_description = (
        meta.get("project_description")
        or meta.get("description")
        or purpose_val
        or "TBD"
    )

    archetype = meta.get("archetype") or "default"

    context: dict[str, object] = {
        "genesis_version": __version__,
        "created": created_time,
        "project_name": project_name,
        "project_type": project_type,
        "project_owner": project_owner,
        "project_description": project_description,
        "archetype": archetype,
        **cleaned_sections,
    }

    # Put any custom metadata in context
    for k, v in meta.items():
        if k not in context:
            context[k] = v

    # Scaffold in current working directory
    target_dir = Path.cwd()
    written, skipped = scaffold_project(target_dir, context, force=force)

    # Print summary
    typer.echo("Processed project brief.")
    typer.echo(f"  Files written: {written}")
    typer.echo(f"  Files skipped: {skipped}")
    typer.echo(
        f"  Sections discovered: {', '.join(sections_discovered) if sections_discovered else 'None'}"
    )
