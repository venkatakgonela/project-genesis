"""Unit tests for genesis migrate command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from genesis.cli import app
from genesis.manifest import TEMPLATES


def test_migrate_creates_full_structure_in_empty_dir(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that genesis migrate creates the full AI-EOS structure in an empty directory."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    result = runner.invoke(app, ["migrate"])
    assert result.exit_code == 0
    assert "Migrating AI-EOS structure..." in result.output
    assert "Files created:  26" in result.output

    # Check all manifest outputs are generated
    for rel_path in TEMPLATES.values():
        assert (project_root / rel_path).is_file(), f"File {rel_path} was not created"


def test_migrate_preserves_existing_files(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that migrate preserves existing files and only creates missing files."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Pre-create some files with custom content
    custom_agents_content = "# Custom Agents Header"
    agents_path = project_root / "AGENTS.md"
    agents_path.write_text(custom_agents_content, encoding="utf-8")

    result = runner.invoke(app, ["migrate"])
    assert result.exit_code == 0
    assert "Files created:  25" in result.output
    assert "Files skipped:  1" in result.output

    # Check the custom file was preserved
    assert agents_path.read_text(encoding="utf-8") == custom_agents_content

    # Check other files were created
    assert (project_root / "ai/00-project-charter.md").is_file()


def test_migrate_dry_run_writes_nothing(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that genesis migrate --dry-run does not write any files."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    result = runner.invoke(app, ["migrate", "--dry-run"])
    assert result.exit_code == 0
    assert "Dry-run: no files will be written." in result.output
    assert "Would create:   26" in result.output
    assert "Already exists: 0" in result.output

    # Verify no files were created
    for rel_path in TEMPLATES.values():
        assert not (
            project_root / rel_path
        ).exists(), f"File {rel_path} was written in dry-run"


def test_migrate_dry_run_reports_missing_files(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that genesis migrate --dry-run reports which files are missing/existing."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Pre-create one file
    (project_root / "AGENTS.md").write_text("# Existing", encoding="utf-8")

    result = runner.invoke(app, ["migrate", "--dry-run"])
    assert result.exit_code == 0
    assert "Dry-run: no files will be written." in result.output
    assert "[would create]  ai/00-project-charter.md" in result.output
    assert "[already exists] AGENTS.md" in result.output
    assert "Would create:   25" in result.output
    assert "Already exists: 1" in result.output


def test_migrate_uses_existing_yaml_metadata(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that migrate parses and uses existing .ai-eos.yaml metadata."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Write a custom .ai-eos.yaml manually
    yaml_content = """
genesis_version: "0.9.0"
project:
  name: "CustomName"
  type: "custom-type"
  owner: "CustomOwner"
  description: "CustomDescription"
archetype: "custom-arch"
"""
    (project_root / ".ai-eos.yaml").write_text(yaml_content, encoding="utf-8")

    # Run migrate (which should skip writing .ai-eos.yaml because it already exists)
    result = runner.invoke(app, ["migrate"])
    assert result.exit_code == 0
    assert "Files created:  25" in result.output

    # Verify rendered files contain metadata from .ai-eos.yaml
    project_charter = (project_root / "ai/00-project-charter.md").read_text(
        encoding="utf-8"
    )
    assert "CustomName" in project_charter
    assert "CustomOwner" in project_charter

    context_pack = (
        project_root / "ai/context-packs/context-pack-default.md"
    ).read_text(encoding="utf-8")
    assert "CustomDescription" in context_pack


def test_migrate_fallback_defaults_without_yaml(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify migrate falls back to CWD name and defaults when .ai-eos.yaml is missing."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Rename temp dir to something recognizable
    test_dir = project_root / "my-awesome-test-proj"
    test_dir.mkdir()
    monkeypatch.chdir(test_dir)

    result = runner.invoke(app, ["migrate"])
    assert result.exit_code == 0

    # Read the generated YAML
    yaml_content = (test_dir / ".ai-eos.yaml").read_text(encoding="utf-8")
    assert 'name: "my-awesome-test-proj"' in yaml_content
    assert 'owner: "TBD"' in yaml_content
    assert 'type: "default"' in yaml_content


def test_migrate_never_overwrites_agents_md(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that migrate never overwrites AGENTS.md."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Run init to get a full structure
    runner.invoke(app, ["init"])

    # Overwrite AGENTS.md with custom content
    agents_path = project_root / "AGENTS.md"
    custom_content = "# MY AGENTS"
    agents_path.write_text(custom_content, encoding="utf-8")

    # Run migrate
    result = runner.invoke(app, ["migrate"])
    assert result.exit_code == 0
    assert agents_path.read_text(encoding="utf-8") == custom_content


def test_migrate_creates_ai_eos_yaml_if_missing(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that migrate creates .ai-eos.yaml if it is missing."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Run init, then delete .ai-eos.yaml
    runner.invoke(app, ["init"])
    (project_root / ".ai-eos.yaml").unlink()

    assert not (project_root / ".ai-eos.yaml").exists()

    result = runner.invoke(app, ["migrate"])
    assert result.exit_code == 0
    assert (project_root / ".ai-eos.yaml").is_file()
    assert "Files created:  1" in result.output


def test_migrate_no_unresolved_jinja_in_output(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that all files created by migrate have no unresolved Jinja2 tags."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    result = runner.invoke(app, ["migrate"])
    assert result.exit_code == 0

    for p in project_root.rglob("*"):
        if p.is_file():
            content = p.read_text(encoding="utf-8")
            assert "{{" not in content, f"Leak '{{{{' in {p.relative_to(project_root)}"
            assert "}}" not in content, f"Leak '}}}}' in {p.relative_to(project_root)}"
            assert "{%" not in content, f"Leak '{{%' in {p.relative_to(project_root)}"
            assert "%}" not in content, f"Leak '%}}' in {p.relative_to(project_root)}"


def test_migrate_works_after_partial_manual_ai_folder(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that migrate works when a partial manual ai/ folder exists."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Create partial folder manually
    (project_root / "ai").mkdir()
    (project_root / "ai/00-project-charter.md").write_text(
        "# Existing Charter", encoding="utf-8"
    )

    result = runner.invoke(app, ["migrate"])
    assert result.exit_code == 0
    assert "Files created:  25" in result.output
    assert "Files skipped:  1" in result.output

    assert (project_root / "ai/00-project-charter.md").read_text(
        encoding="utf-8"
    ) == "# Existing Charter"
    assert (project_root / "ai/01-architecture.md").is_file()


def test_migrate_with_corrupt_ai_eos_yaml(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that migrate does not crash with a corrupt .ai-eos.yaml, and applies defaults."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    # Create a corrupt .ai-eos.yaml manually
    (project_root / ".ai-eos.yaml").write_text(
        "corrupt: yaml\nthis is invalid yaml: {", encoding="utf-8"
    )

    # Run migrate (which should skip writing .ai-eos.yaml because it exists)
    result = runner.invoke(app, ["migrate"])
    assert result.exit_code == 0
    assert "Files created:  25" in result.output

    # Since it is corrupt, it should fallback to defaults, name = project_root name
    # Verify other files rendered with fallback project name
    charter_content = (project_root / "ai/00-project-charter.md").read_text(
        encoding="utf-8"
    )
    assert project_root.name in charter_content
