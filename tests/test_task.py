"""Unit tests for genesis task command."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from genesis.cli import app


def test_task_first_creates_task_001(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that the first task generated defaults to TASK-001 when directory is empty."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    result = runner.invoke(app, ["task", "Add new endpoint"])
    assert result.exit_code == 0
    assert "ai/tasks/TASK-001-add-new-endpoint.md" in result.output

    expected_path = project_root / "ai/tasks/TASK-001-add-new-endpoint.md"
    assert expected_path.is_file()

    content = expected_path.read_text(encoding="utf-8")
    assert "# TASK-001: Add new endpoint" in content
    assert "**Status:** Draft" in content
    assert "**Created Date:**" in content
    assert datetime.today().strftime("%Y-%m-%d") in content


def test_task_sequential_numbering(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that multiple tasks generated sequentially increments numbers correctly."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Create task 1
    result1 = runner.invoke(app, ["task", "First Task"])
    assert result1.exit_code == 0
    assert "ai/tasks/TASK-001-first-task.md" in result1.output

    # Create task 2
    result2 = runner.invoke(app, ["task", "Second Task"])
    assert result2.exit_code == 0
    assert "ai/tasks/TASK-002-second-task.md" in result2.output

    # Create task 3
    result3 = runner.invoke(app, ["task", "Third Task"])
    assert result3.exit_code == 0
    assert "ai/tasks/TASK-003-third-task.md" in result3.output


def test_task_respects_existing_tasks(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that number matches the highest existing task index even if there are gaps."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Create TASK-005 manually to simulate gap
    tasks_dir = project_root / "ai/tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / "TASK-005-gap.md").write_text("dummy", encoding="utf-8")

    result = runner.invoke(app, ["task", "Next Task"])
    assert result.exit_code == 0
    assert "ai/tasks/TASK-006-next-task.md" in result.output
    assert (tasks_dir / "TASK-006-next-task.md").is_file()


def test_task_reads_owner_from_ai_eos_yaml(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that project owner is loaded from .ai-eos.yaml and rendered into the template."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    yaml_content = """genesis_version: "0.1.0"
project:
  name: "Bill Manager"
  owner: "Venkat"
"""
    (project_root / ".ai-eos.yaml").write_text(yaml_content, encoding="utf-8")

    result = runner.invoke(app, ["task", "Endpoint Task"])
    assert result.exit_code == 0

    task_file = project_root / "ai/tasks/TASK-001-endpoint-task.md"
    assert task_file.is_file()
    content = task_file.read_text(encoding="utf-8")
    assert "**Assigned To:** Venkat" in content


def test_task_uses_local_template_override(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that when a local TASK-000-template.md exists, the tool uses it and substitutes fields correctly."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    tasks_dir = project_root / "ai/tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    custom_template = """# TASK-000: [Task Name]
**Status:** Todo / In Progress / Completed
Custom layout details here.
"""
    (tasks_dir / "TASK-000-template.md").write_text(custom_template, encoding="utf-8")

    result = runner.invoke(app, ["task", "My Custom Task"])
    assert result.exit_code == 0
    assert "ai/tasks/TASK-001-my-custom-task.md" in result.output

    created_file = tasks_dir / "TASK-001-my-custom-task.md"
    content = created_file.read_text(encoding="utf-8")
    assert "# TASK-001: My Custom Task" in content
    assert "**Status:** Draft  " in content or "**Status:** Draft" in content
    assert "**Created Date:**" in content
    assert "Custom layout details here." in content


def test_task_fails_if_task_exists(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that task command fails if the destination task file already exists."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    tasks_dir = project_root / "ai/tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    task_file = tasks_dir / "TASK-001-duplicate-task.md"
    task_file.write_text("existing task content", encoding="utf-8")

    # Monkeypatch Path.glob to return empty list, forcing computed next task number to be 1
    original_glob = Path.glob

    def mock_glob(self: Path, pattern: str) -> list[Path]:
        if "TASK-*.md" in pattern:
            return []
        return list(original_glob(self, pattern))

    monkeypatch.setattr(Path, "glob", mock_glob)

    result = runner.invoke(app, ["task", "Duplicate Task"])
    assert result.exit_code == 1
    assert "Error: task file already exists" in result.output
    # Content should not be overwritten
    assert task_file.read_text(encoding="utf-8") == "existing task content"
