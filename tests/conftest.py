"""Shared pytest fixtures for Genesis tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """A temporary directory that acts as a fake project root.

    Each test gets a fresh isolated directory via pytest's built-in
    ``tmp_path`` fixture.
    """
    return tmp_path
