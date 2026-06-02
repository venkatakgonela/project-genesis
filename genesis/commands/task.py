"""genesis task — create a numbered task file in ai/tasks/."""

from __future__ import annotations

import typer


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
    typer.echo("⚠  genesis task is not yet implemented.", err=True)
    raise typer.Exit(code=1)
