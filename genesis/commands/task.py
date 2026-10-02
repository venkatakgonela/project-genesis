"""genesis task — create a numbered task file in ai/tasks/."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import typer


def slugify(text: str) -> str:
    """Slugify the task name (lower-case, spaces/underscores to hyphens)."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def get_project_owner() -> str:
    """Parse the project owner from the local .ai-eos.yaml manifest if it exists."""
    yaml_path = Path(".ai-eos.yaml")
    if yaml_path.is_file():
        try:
            content = yaml_path.read_text(encoding="utf-8")
            in_project_section = False
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("project:"):
                    in_project_section = True
                    continue
                if in_project_section:
                    if (
                        line.strip()
                        and not line.startswith(" ")
                        and not line.startswith("\t")
                    ):
                        in_project_section = False
                    elif "owner:" in stripped:
                        parts = stripped.split("owner:", 1)
                        return parts[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return "TBD"


def run(
    task_name: str = typer.Argument(
        ...,
        help="Task name — will be slugified for the filename.",
    ),
) -> None:
    """Create a new numbered task file in ``ai/tasks/``.

    Auto-numbers by counting existing ``TASK-*.md`` files in ``ai/tasks/``.
    The task name is slugified (lower-cased, spaces to hyphens) to form
    the filename::

        genesis task "Add retry logic to payment processor"
        → ai/tasks/TASK-001-add-retry-logic-to-payment-processor.md
    """
    tasks_dir = Path("ai/tasks")
    existing_numbers: list[int] = []

    if tasks_dir.exists():
        for f in tasks_dir.glob("TASK-*.md"):
            match = re.match(r"^TASK-(\d+)", f.name)
            if match:
                val = int(match.group(1))
                if val > 0:
                    existing_numbers.append(val)

    next_num = max(existing_numbers) + 1 if existing_numbers else 1
    next_num_str = f"{next_num:03d}"
    task_id = f"TASK-{next_num_str}"

    task_slug = slugify(task_name)
    dest_filename = f"{task_id}-{task_slug}.md"
    dest_path = tasks_dir / dest_filename

    if dest_path.exists():
        typer.echo(f"Error: task file already exists at {dest_path}", err=True)
        raise typer.Exit(code=1)

    created_date = datetime.today().strftime("%Y-%m-%d")
    project_owner = get_project_owner()

    local_template_path = tasks_dir / "TASK-000-template.md"

    if not local_template_path.is_file():
        # Prefer rendering packaged Jinja2 template directly with context
        from genesis.template_engine import render

        context: dict[str, object] = {
            "task_id": task_id,
            "task_name": task_name,
            "task_slug": task_slug,
            "created_date": created_date,
            "status": "Draft",
            "project_owner": project_owner,
        }
        content = render("ai/tasks/TASK-000-template.md.j2", context)
    else:
        # Fallback to local custom template override using careful string replacement
        try:
            raw_content = local_template_path.read_text(encoding="utf-8")
        except Exception as e:
            typer.echo(f"Error reading local template: {e}", err=True)
            raise typer.Exit(code=1) from None

        content = raw_content
        content = content.replace("TASK-000", task_id)
        content = content.replace("[Task Name]", task_name)

        if "Todo / In Progress / Completed" in content:
            content = content.replace(
                "**Status:** Todo / In Progress / Completed",
                f"**Status:** Draft  \n**Created Date:** {created_date}",
            )
            content = content.replace(
                "Status: Todo / In Progress / Completed",
                f"Status: Draft  \nCreated Date: {created_date}",
            )
        else:
            lines = content.split("\n")
            status_idx = -1
            has_created_date = False
            for i, line in enumerate(lines):
                if "status:" in line.lower():
                    status_idx = i
                if "created date:" in line.lower():
                    has_created_date = True

            if status_idx != -1:
                status_line = lines[status_idx]
                if "**Status:**" in status_line:
                    lines[status_idx] = "**Status:** Draft  "
                elif "Status:" in status_line:
                    lines[status_idx] = "Status: Draft  "

                if not has_created_date:
                    lines.insert(status_idx + 1, f"**Created Date:** {created_date}  ")

            content = "\n".join(lines)

    # Ensure parent directory exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        dest_path.write_text(content, encoding="utf-8")
    except Exception as e:
        typer.echo(f"Error writing task file: {e}", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(dest_path)
