"""File and directory scaffolding helpers.

All functions are pure filesystem operations with no side effects beyond
the paths they are given. Output / logging is the caller's responsibility.
"""

from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> None:
    """Create *path* and all its parents if they do not already exist.

    Idempotent — safe to call on an existing directory.
    """
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str, *, force: bool = False) -> bool:
    """Write *content* to *path*.

    Creates any missing parent directories automatically.

    Args:
        path:    Destination file path.
        content: Text content to write (UTF-8).
        force:   If ``True``, overwrite an existing file.
                 If ``False`` (default), skip existing files.

    Returns:
        ``True`` if the file was written, ``False`` if it was skipped.
    """
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def file_exists(path: Path) -> bool:
    """Return ``True`` if *path* points to an existing regular file."""
    return path.is_file()
