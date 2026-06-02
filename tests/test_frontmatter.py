"""Unit tests for genesis.frontmatter — manual YAML front matter parser."""

from __future__ import annotations

import pytest

from genesis.frontmatter import parse


class TestParseBasicFrontMatter:
    def test_extracts_single_key(self) -> None:
        text = "---\ntitle: My Project\n---\n"
        meta, _ = parse(text)
        assert meta["title"] == "My Project"

    def test_extracts_multiple_keys(self) -> None:
        text = "---\ntitle: My Project\ntype: python-api\nowner: platform-team\n---\n"
        meta, _ = parse(text)
        assert meta == {
            "title": "My Project",
            "type": "python-api",
            "owner": "platform-team",
        }

    def test_body_returned_without_front_matter(self) -> None:
        text = "---\ntitle: X\n---\n\nBody text here."
        _, body = parse(text)
        assert body == "Body text here."

    def test_body_stripped_of_leading_newlines(self) -> None:
        text = "---\ntitle: X\n---\n\n\nBody"
        _, body = parse(text)
        assert body == "Body"

    def test_empty_body(self) -> None:
        text = "---\ntitle: X\n---\n"
        _, body = parse(text)
        assert body == ""


class TestParseNoFrontMatter:
    def test_plain_text_returns_empty_meta(self) -> None:
        text = "Just a plain markdown file."
        meta, body = parse(text)
        assert meta == {}
        assert body == text

    def test_empty_string(self) -> None:
        meta, body = parse("")
        assert meta == {}
        assert body == ""

    def test_text_starting_with_content_not_delimiter(self) -> None:
        text = "# Heading\n\nSome content."
        meta, body = parse(text)
        assert meta == {}
        assert body == text


class TestParseMalformed:
    def test_unclosed_front_matter_raises(self) -> None:
        text = "---\ntitle: My Project\nNo closing delimiter."
        with pytest.raises(ValueError, match="never closed"):
            parse(text)

    def test_only_opening_delimiter_raises(self) -> None:
        text = "---\n"
        with pytest.raises(ValueError, match="never closed"):
            parse(text)


class TestParseWhitespaceHandling:
    def test_strips_key_whitespace(self) -> None:
        text = "---\n  title : My Project\n---\n"
        meta, _ = parse(text)
        assert meta["title"] == "My Project"

    def test_strips_value_whitespace(self) -> None:
        text = "---\ntitle:   My Project   \n---\n"
        meta, _ = parse(text)
        assert meta["title"] == "My Project"

    def test_empty_value(self) -> None:
        text = "---\ntitle: \ntype: api\n---\n"
        meta, _ = parse(text)
        assert meta["title"] == ""
        assert meta["type"] == "api"


class TestParseEdgeCases:
    def test_value_with_colon(self) -> None:
        """Values that contain colons should be preserved after the first split."""
        text = "---\nurl: http://example.com\n---\n"
        meta, _ = parse(text)
        assert meta["url"] == "http://example.com"

    def test_line_without_colon_ignored(self) -> None:
        text = "---\ntitle: Project\nthis line has no colon\ntype: api\n---\n"
        meta, _ = parse(text)
        assert "title" in meta
        assert "type" in meta
        assert len(meta) == 2

    def test_multiple_documents_only_parses_first_block(self) -> None:
        text = "---\ntitle: First\n---\n\nBody\n\n---\ntitle: Second\n---\n"
        meta, body = parse(text)
        assert meta["title"] == "First"
        assert "Second" in body
