"""Unit tests for genesis.scaffold — file and directory helpers."""

from __future__ import annotations

from pathlib import Path

from genesis.scaffold import ensure_dir, file_exists, write_file


class TestEnsureDir:
    def test_creates_directory(self, tmp_path: Path) -> None:
        target = tmp_path / "newdir"
        ensure_dir(target)
        assert target.is_dir()

    def test_creates_nested_directories(self, tmp_path: Path) -> None:
        target = tmp_path / "a" / "b" / "c"
        ensure_dir(target)
        assert target.is_dir()

    def test_idempotent_on_existing_directory(self, tmp_path: Path) -> None:
        target = tmp_path / "existing"
        target.mkdir()
        ensure_dir(target)  # must not raise
        assert target.is_dir()

    def test_does_not_affect_sibling_directories(self, tmp_path: Path) -> None:
        sibling = tmp_path / "sibling"
        sibling.mkdir()
        ensure_dir(tmp_path / "target")
        assert sibling.is_dir()


class TestWriteFile:
    def test_creates_file_with_content(self, tmp_path: Path) -> None:
        path = tmp_path / "hello.md"
        result = write_file(path, "hello")
        assert result is True
        assert path.read_text(encoding="utf-8") == "hello"

    def test_returns_false_when_file_exists_no_force(self, tmp_path: Path) -> None:
        path = tmp_path / "existing.md"
        path.write_text("original", encoding="utf-8")
        result = write_file(path, "new content")
        assert result is False

    def test_skips_content_when_not_forced(self, tmp_path: Path) -> None:
        path = tmp_path / "existing.md"
        path.write_text("original", encoding="utf-8")
        write_file(path, "new content")
        assert path.read_text(encoding="utf-8") == "original"

    def test_overwrites_when_forced(self, tmp_path: Path) -> None:
        path = tmp_path / "existing.md"
        path.write_text("original", encoding="utf-8")
        result = write_file(path, "new content", force=True)
        assert result is True
        assert path.read_text(encoding="utf-8") == "new content"

    def test_creates_missing_parent_directories(self, tmp_path: Path) -> None:
        path = tmp_path / "nested" / "deep" / "file.md"
        write_file(path, "content")
        assert path.exists()
        assert path.read_text(encoding="utf-8") == "content"

    def test_writes_empty_content(self, tmp_path: Path) -> None:
        path = tmp_path / "empty.md"
        result = write_file(path, "")
        assert result is True
        assert path.read_text(encoding="utf-8") == ""

    def test_writes_multiline_content(self, tmp_path: Path) -> None:
        content = "# Title\n\nParagraph one.\n\nParagraph two.\n"
        path = tmp_path / "doc.md"
        write_file(path, content)
        assert path.read_text(encoding="utf-8") == content

    def test_unicode_content(self, tmp_path: Path) -> None:
        content = "# Ünïcödé héàding\n"
        path = tmp_path / "unicode.md"
        write_file(path, content)
        assert path.read_text(encoding="utf-8") == content

    def test_force_on_nonexistent_file_still_creates(self, tmp_path: Path) -> None:
        path = tmp_path / "new.md"
        result = write_file(path, "content", force=True)
        assert result is True
        assert path.exists()


class TestFileExists:
    def test_returns_false_for_missing_file(self, tmp_path: Path) -> None:
        assert file_exists(tmp_path / "missing.md") is False

    def test_returns_true_for_existing_file(self, tmp_path: Path) -> None:
        path = tmp_path / "present.md"
        path.write_text("", encoding="utf-8")
        assert file_exists(path) is True

    def test_returns_false_for_directory(self, tmp_path: Path) -> None:
        d = tmp_path / "mydir"
        d.mkdir()
        assert file_exists(d) is False
