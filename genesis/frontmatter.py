"""Manual YAML front matter parser.

Handles the minimal subset needed by Genesis brief files:

    ---
    title: My Project
    type: python-api
    owner: platform-team
    ---

    Free-form body text.

Rules
-----
- Only flat ``key: value`` pairs are supported (no nested YAML).
- Lines inside the front matter block that do not contain ``:`` are ignored.
- Keys and values are stripped of surrounding whitespace.
- If no opening ``---`` is found, returns ``({}, original_text)``.
- If an opening ``---`` is found but no closing ``---``, raises ``ValueError``.

No external dependencies.
"""

from __future__ import annotations


def parse(text: str) -> tuple[dict[str, str], str]:
    """Parse simple YAML front matter from a Markdown string.

    Args:
        text: Raw file content, potentially starting with a ``---`` block.

    Returns:
        A ``(metadata, body)`` tuple where ``metadata`` is a flat
        ``{key: value}`` dict and ``body`` is the remaining text after
        the closing ``---``, stripped of leading newlines.

    Raises:
        ValueError: If a front matter block is opened but never closed.
    """
    lines = text.split("\n")

    if not lines or lines[0].strip() != "---":
        return {}, text

    # Find the closing delimiter (start searching from line index 1)
    close_idx: int | None = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            close_idx = i
            break

    if close_idx is None:
        raise ValueError(
            "Front matter block opened with '---' but never closed with '---'."
        )

    meta: dict[str, str] = {}
    for line in lines[1:close_idx]:
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()

    body = "\n".join(lines[close_idx + 1 :]).lstrip("\n")
    return meta, body
