"""Unit tests for genesis brief command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from genesis.cli import app


def test_brief_valid_brief(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that genesis brief parses a valid brief and generates all templates."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    brief_content = """---
project_name: Bill Manager
project_type: fastapi-web
project_owner: Kiran
archetype: default
---

# Purpose

Manage personal and company bills.

# Requirements

- Accounts
- Bills
- Payments

# Constraints

- FastAPI
- PostgreSQL
- HTMX
"""
    brief_file = project_root / "brief.md"
    brief_file.write_text(brief_content, encoding="utf-8")

    result = runner.invoke(app, ["brief", str(brief_file)])
    assert result.exit_code == 0
    assert "Processed project brief." in result.output
    assert "Files written: 26" in result.output
    assert "Sections discovered: Purpose, Requirements, Constraints" in result.output

    # Verify key output files exist
    assert (project_root / ".ai-eos.yaml").is_file()
    assert (project_root / "ai/00-project-charter.md").is_file()
    assert (project_root / "ai/01-architecture.md").is_file()

    # Verify charter contains the purpose and requirements
    charter_content = (project_root / "ai/00-project-charter.md").read_text(
        encoding="utf-8"
    )
    assert "Manage personal and company bills." in charter_content
    assert "- Accounts" in charter_content
    assert "- Bills" in charter_content

    # Verify architecture contains constraints
    arch_content = (project_root / "ai/01-architecture.md").read_text(encoding="utf-8")
    assert "- FastAPI" in arch_content
    assert "- PostgreSQL" in arch_content


def test_brief_missing_sections(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that brief works when some target sections are missing."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    brief_content = """---
project_name: Minimal Proj
---

# Purpose

Keep it simple.
"""
    brief_file = project_root / "brief.md"
    brief_file.write_text(brief_content, encoding="utf-8")

    result = runner.invoke(app, ["brief", str(brief_file)])
    assert result.exit_code == 0
    assert "Sections discovered: Purpose" in result.output

    charter_content = (project_root / "ai/00-project-charter.md").read_text(
        encoding="utf-8"
    )
    assert "Keep it simple." in charter_content
    assert "Key goal 1" in charter_content  # default fallback


def test_brief_missing_front_matter(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that brief works even without front matter by using defaults."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    brief_content = """# Purpose

No metadata provided.
"""
    brief_file = project_root / "brief.md"
    brief_file.write_text(brief_content, encoding="utf-8")

    result = runner.invoke(app, ["brief", str(brief_file)])
    assert result.exit_code == 0
    assert "Sections discovered: Purpose" in result.output

    # Check that default metadata is used (e.g. project name is folder name)
    yaml_content = (project_root / ".ai-eos.yaml").read_text(encoding="utf-8")
    assert f'name: "{project_root.name}"' in yaml_content


def test_brief_force_overwrite(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that existing files are skipped by default, but overwritten with --force."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    brief_content = """# Purpose
Original purpose.
"""
    brief_file = project_root / "brief.md"
    brief_file.write_text(brief_content, encoding="utf-8")

    # Run once to initialize
    runner.invoke(app, ["brief", str(brief_file)])

    # Modify charter file manually
    charter_path = project_root / "ai/00-project-charter.md"
    charter_path.write_text("# CUSTOM CHARTER", encoding="utf-8")

    # Run again without force -> should skip
    result = runner.invoke(app, ["brief", str(brief_file)])
    assert result.exit_code == 0
    assert "Files skipped: 26" in result.output
    assert charter_path.read_text(encoding="utf-8") == "# CUSTOM CHARTER"

    # Run again with --force -> should overwrite
    result = runner.invoke(app, ["brief", str(brief_file), "--force"])
    assert result.exit_code == 0
    assert "Files written: 26" in result.output
    assert charter_path.read_text(encoding="utf-8") != "# CUSTOM CHARTER"
    assert "Original purpose." in charter_path.read_text(encoding="utf-8")


def test_brief_no_unresolved_jinja(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that the generated output contains no unresolved Jinja syntax."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    brief_content = """---
project_name: JinjaTest
project_type: python-cli
project_owner: Tester
---
# Purpose
Verify syntax.
"""
    brief_file = project_root / "brief.md"
    brief_file.write_text(brief_content, encoding="utf-8")

    result = runner.invoke(app, ["brief", str(brief_file)])
    assert result.exit_code == 0

    for p in project_root.rglob("*"):
        if p.is_file() and p != brief_file:
            content = p.read_text(encoding="utf-8")
            assert "{%" not in content, f"Jinja leak in {p}"
            assert "%}" not in content, f"Jinja leak in {p}"
            assert "{{" not in content, f"Jinja leak in {p}"
            assert "}}" not in content, f"Jinja leak in {p}"
