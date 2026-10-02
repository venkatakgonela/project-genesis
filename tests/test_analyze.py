"""Unit tests for genesis analyze command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from genesis.cli import app
from genesis.commands.analyze import analyze_project


def test_analyze_reports_empty_project(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that analyze handles an empty project without failing."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    result = runner.invoke(app, ["analyze"])

    assert result.exit_code == 0
    assert "Project analysis" in result.output
    assert "AI-EOS files: 0/26" in result.output
    assert "None detected" in result.output


def test_analyze_detects_python_fastapi_project(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that analyze detects common backend project markers."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    (project_root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    (project_root / "app").mkdir()
    (project_root / "app/main.py").write_text("from fastapi import FastAPI\n", encoding="utf-8")
    (project_root / "tests").mkdir()
    (project_root / "alembic.ini").write_text("[alembic]\n", encoding="utf-8")

    result = runner.invoke(app, ["analyze"])

    assert result.exit_code == 0
    assert "Python project: pyproject.toml" in result.output
    assert "FastAPI app: app/main.py" in result.output
    assert "uv run ruff check ." in result.output
    assert "uv run pytest" in result.output
    assert "uv run alembic upgrade head" in result.output


def test_analyze_detects_frontend_package_scripts(project_root: Path) -> None:
    """Verify that analyze infers frontend quality gates from package scripts."""
    frontend = project_root / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(
        """
{
  "scripts": {
    "lint": "eslint .",
    "test": "vitest",
    "build": "vite build",
    "test:e2e": "playwright test"
  }
}
""",
        encoding="utf-8",
    )
    (frontend / "playwright.config.ts").write_text("export default {}", encoding="utf-8")
    (frontend / "vitest.config.ts").write_text("export default {}", encoding="utf-8")

    analysis = analyze_project(project_root)

    assert "cd frontend && npm run lint" in analysis.quality_gates
    assert "cd frontend && npm run test" in analysis.quality_gates
    assert "cd frontend && npm run build" in analysis.quality_gates
    assert "cd frontend && npm run test:e2e" in analysis.quality_gates
    assert any(signal.name == "Frontend E2E tests" for signal in analysis.stack_signals)


def test_analyze_counts_ai_inventory(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that analyze summarizes common AI-EOS artifact counts."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["analyze"])

    assert result.exit_code == 0
    assert "AI-EOS files: 26/26" in result.output
    assert "specs: 1" in result.output
    assert "tasks: 1" in result.output
    assert "context packs: 1" in result.output
