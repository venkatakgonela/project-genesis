"""Unit tests for genesis new command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from genesis.cli import app
from genesis.manifest import TEMPLATES


def test_new_creates_subfolder_and_all_files(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that genesis new creates a target subfolder with full scaffolding."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    result = runner.invoke(
        app, ["new", "--name", "my-new-project", "--type", "python-api"]
    )
    assert result.exit_code == 0
    assert "Created new AI-EOS project." in result.output

    target_dir = project_root / "my-new-project"
    assert target_dir.is_dir()

    # Verify all manifest outputs are generated in the subfolder
    for rel_path in TEMPLATES.values():
        assert (target_dir / rel_path).is_file(), f"File {rel_path} was not created"

    # Verify no files were created in the cwd except the target subfolder itself
    cwd_files = [p for p in project_root.iterdir() if p != target_dir]
    assert len(cwd_files) == 0, f"Unexpected files created in CWD: {cwd_files}"


def test_new_injects_metadata_and_no_jinja_leak(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify project metadata injection and check for Jinja leakage."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    result = runner.invoke(
        app, ["new", "--name", "injected-proj", "--type", "data-pipeline"]
    )
    assert result.exit_code == 0

    target_dir = project_root / "injected-proj"

    # Verify metadata in .ai-eos.yaml
    yaml_content = (target_dir / ".ai-eos.yaml").read_text(encoding="utf-8")
    assert "genesis_version:" in yaml_content
    assert "created:" in yaml_content
    assert 'name: "injected-proj"' in yaml_content
    assert 'type: "data-pipeline"' in yaml_content

    # Check for no unresolved Jinja syntax
    for p in target_dir.rglob("*"):
        if p.is_file():
            content = p.read_text(encoding="utf-8")
            assert "{%" not in content, f"Leak '{{%' in {p.relative_to(target_dir)}"
            assert "%}" not in content, f"Leak '%}}' in {p.relative_to(target_dir)}"
            assert "{{" not in content, f"Leak '{{{{' in {p.relative_to(target_dir)}"
            assert "}}" not in content, f"Leak '}}}}' in {p.relative_to(target_dir)}"


def test_new_handles_existing_folder_safely(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that genesis new runs safely if the target directory already exists."""
    monkeypatch.chdir(project_root)
    runner = CliRunner()

    target_dir = project_root / "existing-dir"
    target_dir.mkdir()

    # Pre-create a file to simulate an existing file in the directory
    charter_file = target_dir / "ai/00-project-charter.md"
    charter_file.parent.mkdir(parents=True, exist_ok=True)
    custom_content = "# EXISTING CHARTER"
    charter_file.write_text(custom_content, encoding="utf-8")

    # Run command targeting existing-dir
    result = runner.invoke(app, ["new", "--name", "existing-dir"])
    assert result.exit_code == 0
    assert "Files skipped: 1" in result.output

    # The existing file should not be overwritten (since force is not supported or supplied)
    assert charter_file.read_text(encoding="utf-8") == custom_content

    # The rest of the files should be successfully created
    for rel_path in TEMPLATES.values():
        assert (target_dir / rel_path).is_file()
