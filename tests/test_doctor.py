"""Unit tests for genesis doctor command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from genesis.cli import app


def test_doctor_reports_missing_ai_eos_files(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that doctor reports missing canonical files in an empty project."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 1
    assert "AI-EOS doctor" in result.output
    assert "MISSING_CANONICAL_FILE" in result.output
    assert "MISSING_MANIFEST" in result.output


def test_doctor_accepts_fresh_scaffold_with_warnings(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that generated scaffolds pass structurally while surfacing warnings."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "Errors:   0" in result.output
    assert "PLACEHOLDER_TEXT" in result.output
    assert "BROAD_CONTEXT_PACK" not in result.output


def test_doctor_strict_fails_on_warnings(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that strict mode turns warnings into a non-zero health gate."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["doctor", "--strict"])

    assert result.exit_code == 1
    assert "PLACEHOLDER_TEXT" in result.output


def test_doctor_detects_manifest_drift(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that files declared in .ai-eos.yaml must exist."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    runner.invoke(app, ["init"])
    (project_root / "ai/00-project-charter.md").unlink()

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 1
    assert "MISSING_CANONICAL_FILE" in result.output
    assert "MISSING_DECLARED_FILE" in result.output
    assert "ai/00-project-charter.md" in result.output


def test_doctor_detects_unresolved_template_tokens(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that unresolved Jinja tokens are treated as errors."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    runner.invoke(app, ["init"])
    (project_root / "ai/01-architecture.md").write_text(
        "# Broken\n\n{{ project_name }}\n", encoding="utf-8"
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 1
    assert "UNRESOLVED_TEMPLATE_TOKEN" in result.output
    assert "ai/01-architecture.md" in result.output


def test_doctor_detects_stale_review_date(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that old Last reviewed dates create warnings."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    runner.invoke(app, ["init"])
    repo_map = project_root / "ai/03-repo-map.md"
    repo_map.write_text(
        "# Repo Map\n\n**Last reviewed:** 2000-01-01\n", encoding="utf-8"
    )

    result = runner.invoke(app, ["doctor", "--max-age-days", "1"])

    assert result.exit_code == 0
    assert "STALE_REVIEW_DATE" in result.output
    assert "ai/03-repo-map.md" in result.output
