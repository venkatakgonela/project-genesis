"""Unit tests for genesis init command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from genesis.cli import app
from genesis.manifest import TEMPLATES


def test_init_creates_all_files_and_directories(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that genesis init bootstraps the full AI-EOS structure."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Initialized AI-EOS project." in result.output

    # 1. Creates .ai-eos.yaml
    assert (project_root / ".ai-eos.yaml").is_file()

    # 2. Creates AGENTS.md
    assert (project_root / "AGENTS.md").is_file()

    # 3. Creates ai/00-project-charter.md
    assert (project_root / "ai/00-project-charter.md").is_file()

    # 4. Creates ai/08-risk-register.md
    assert (project_root / "ai/08-risk-register.md").is_file()

    # 5. Creates nested folders
    expected_dirs = [
        "ai/specs",
        "ai/tasks",
        "ai/skills",
        "ai/runs",
        "ai/roadmap",
        "ai/epics",
        "ai/features",
        "ai/agents",
        "ai/context-packs",
    ]
    for d in expected_dirs:
        assert (project_root / d).is_dir(), f"Directory {d} was not created"

    # Check all manifest outputs are generated
    for rel_path in TEMPLATES.values():
        assert (project_root / rel_path).is_file(), f"File {rel_path} was not created"


def test_init_rendered_defaults_and_no_jinja_leak(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify default values exist and no unresolved Jinja delimiters remain."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # 8. Rendered output contains project metadata defaults
    yaml_content = (project_root / ".ai-eos.yaml").read_text(encoding="utf-8")
    assert "genesis_version:" in yaml_content
    assert "created:" in yaml_content
    assert f'name: "{project_root.name}"' in yaml_content
    assert 'type: "default"' in yaml_content
    assert 'owner: "TBD"' in yaml_content
    assert 'description: "TBD"' in yaml_content
    assert 'archetype: "default"' in yaml_content

    # 9. No unresolved Jinja syntax remains in generated files
    for p in project_root.rglob("*"):
        if p.is_file():
            content = p.read_text(encoding="utf-8")
            assert "{{" not in content, f"Leak '{{{{' in {p.relative_to(project_root)}"
            assert "}}" not in content, f"Leak '}}}}' in {p.relative_to(project_root)}"
            assert "{%" not in content, f"Leak '{{%' in {p.relative_to(project_root)}"
            assert "%}" not in content, f"Leak '%}}' in {p.relative_to(project_root)}"


def test_init_skips_existing_by_default(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that genesis init skips overwriting existing files by default."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Run once to initialize
    runner.invoke(app, ["init"])

    # Modify a file manually
    risk_reg = project_root / "ai/08-risk-register.md"
    custom_content = "# CUSTOM RISK REGISTER"
    risk_reg.write_text(custom_content, encoding="utf-8")

    # Run again without force
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Files skipped: 26" in result.output

    # Verify custom content remains (skipped)
    assert risk_reg.read_text(encoding="utf-8") == custom_content


def test_init_overwrites_with_force(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that genesis init overwrites existing files when --force is supplied."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Run once to initialize
    runner.invoke(app, ["init"])

    # Modify a file manually
    risk_reg = project_root / "ai/08-risk-register.md"
    risk_reg.write_text("# CUSTOM RISK REGISTER", encoding="utf-8")

    # Run again with --force (or -f)
    result = runner.invoke(app, ["init", "--force"])
    assert result.exit_code == 0
    assert "Files written: 26" in result.output

    # Verify custom content was overwritten
    assert risk_reg.read_text(encoding="utf-8") != "# CUSTOM RISK REGISTER"
    assert "# Risk Register" in risk_reg.read_text(encoding="utf-8")
