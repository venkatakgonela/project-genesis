"""genesis doctor - diagnose AI-EOS health in the current project."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import typer

from genesis.manifest import TEMPLATES


@dataclass(frozen=True)
class Finding:
    """A single AI-EOS health finding."""

    severity: str
    code: str
    path: str
    message: str


PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD)\b", re.IGNORECASE)
LAST_REVIEWED_RE = re.compile(
    r"\*\*Last reviewed:\*\*\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE
)
JINJA_TOKENS = ("{{", "}}", "{%", "%}")
IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
    "test-results",
}


def run(
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Exit non-zero when warnings are present.",
    ),
    max_age_days: int = typer.Option(
        90,
        "--max-age-days",
        min=1,
        help="Warn when Last reviewed dates are older than this many days.",
    ),
) -> None:
    """Check the current project for AI-EOS structure, context, and drift issues."""
    root = Path.cwd()
    findings = diagnose(root, max_age_days=max_age_days)

    errors = [finding for finding in findings if finding.severity == "ERROR"]
    warnings = [finding for finding in findings if finding.severity == "WARN"]

    typer.echo("AI-EOS doctor")
    typer.echo(f"  Target directory: {root}")
    typer.echo(f"  Errors:   {len(errors)}")
    typer.echo(f"  Warnings: {len(warnings)}")

    if findings:
        typer.echo("")
        for finding in findings:
            typer.echo(
                f"[{finding.severity}] {finding.code} {finding.path}: {finding.message}"
            )
    else:
        typer.echo("")
        typer.echo("No AI-EOS health issues found.")

    if errors or (strict and warnings):
        raise typer.Exit(code=1)


def diagnose(root: Path, *, max_age_days: int = 90) -> list[Finding]:
    """Return AI-EOS health findings for *root* without printing output."""
    findings: list[Finding] = []

    findings.extend(check_manifest_files(root))
    findings.extend(check_declared_manifest_paths(root))
    findings.extend(check_text_files(root, max_age_days=max_age_days))
    findings.extend(check_context_policy(root))
    findings.extend(check_quality_gate_policy(root))

    return sorted(findings, key=lambda item: (item.severity, item.path, item.code))


def check_manifest_files(root: Path) -> list[Finding]:
    """Check whether canonical AI-EOS files exist."""
    findings: list[Finding] = []
    for rel_path in TEMPLATES.values():
        path = root / rel_path
        if not path.is_file():
            findings.append(
                Finding(
                    severity="ERROR",
                    code="MISSING_CANONICAL_FILE",
                    path=rel_path,
                    message="Canonical AI-EOS file is missing. Run `genesis migrate`.",
                )
            )
    return findings


def check_declared_manifest_paths(root: Path) -> list[Finding]:
    """Check path entries declared in .ai-eos.yaml."""
    manifest_path = root / ".ai-eos.yaml"
    if not manifest_path.is_file():
        return [
            Finding(
                severity="ERROR",
                code="MISSING_MANIFEST",
                path=".ai-eos.yaml",
                message="AI-EOS manifest is missing. Run `genesis migrate`.",
            )
        ]

    findings: list[Finding] = []
    try:
        content = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [
            Finding(
                severity="ERROR",
                code="UNREADABLE_MANIFEST",
                path=".ai-eos.yaml",
                message=f"Could not read manifest: {exc}",
            )
        ]

    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("- path:"):
            continue
        rel_path = stripped.removeprefix("- path:").strip().strip("\"'")
        if rel_path and not (root / rel_path).is_file():
            findings.append(
                Finding(
                    severity="ERROR",
                    code="MISSING_DECLARED_FILE",
                    path=f".ai-eos.yaml:{line_number}",
                    message=f"Manifest declares missing file `{rel_path}`.",
                )
            )
    return findings


def check_text_files(root: Path, *, max_age_days: int) -> list[Finding]:
    """Check AI-EOS text files for unresolved syntax, placeholders, and stale dates."""
    findings: list[Finding] = []
    today = datetime.now(UTC).date()

    for path in iter_ai_eos_text_files(root):
        rel_path = path.relative_to(root).as_posix()
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for token in JINJA_TOKENS:
            if token in content:
                findings.append(
                    Finding(
                        severity="ERROR",
                        code="UNRESOLVED_TEMPLATE_TOKEN",
                        path=rel_path,
                        message=f"Found unresolved Jinja token `{token}`.",
                    )
                )
                break

        if should_check_placeholders(path):
            placeholder_count = len(PLACEHOLDER_RE.findall(content))
            if placeholder_count:
                findings.append(
                    Finding(
                        severity="WARN",
                        code="PLACEHOLDER_TEXT",
                        path=rel_path,
                        message=(
                            f"Found {placeholder_count} TODO/TBD placeholder(s). "
                            "Replace placeholders before relying on this context."
                        ),
                    )
                )

        reviewed_match = LAST_REVIEWED_RE.search(content)
        if reviewed_match:
            reviewed = parse_iso_date(reviewed_match.group(1))
            if reviewed is not None:
                age_days = (today - reviewed).days
                if age_days > max_age_days:
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="STALE_REVIEW_DATE",
                            path=rel_path,
                            message=(
                                f"Last reviewed date is {age_days} days old. "
                                "Refresh this context or confirm it is still valid."
                            ),
                        )
                    )
    return findings


def check_context_policy(root: Path) -> list[Finding]:
    """Check context packs for broad loading instructions."""
    context_dir = root / "ai/context-packs"
    if not context_dir.is_dir():
        return []

    findings: list[Finding] = []
    broad_patterns = (
        "before executing any commands",
        "read the following files",
        "load into the agent's context block",
    )

    for path in sorted(context_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8").lower()
        rel_path = path.relative_to(root).as_posix()
        if any(pattern in content for pattern in broad_patterns) and "context budget" not in content:
            findings.append(
                Finding(
                    severity="WARN",
                    code="BROAD_CONTEXT_PACK",
                    path=rel_path,
                    message=(
                        "Context pack encourages broad loading without a budget. "
                        "Prefer task-scoped required/optional references."
                    ),
                )
            )
    return findings


def check_quality_gate_policy(root: Path) -> list[Finding]:
    """Check whether project-specific quality gates have been documented."""
    candidate_paths = [
        root / "AGENTS.md",
        root / "ai/05-coding-standards.md",
        root / "ai/specs/SPEC-003-testing-strategy.md",
    ]
    existing = [path for path in candidate_paths if path.is_file()]
    if not existing:
        return []

    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in existing)
    has_command = any(
        marker in combined
        for marker in (
            "pytest",
            "ruff",
            "npm run",
            "cargo test",
            "go test",
            "mvn test",
        )
    )
    if has_command:
        return []

    return [
        Finding(
            severity="WARN",
            code="MISSING_QUALITY_GATES",
            path="AGENTS.md",
            message="Document concrete test/lint/type/build commands for agents.",
        )
    ]


def iter_ai_eos_text_files(root: Path) -> list[Path]:
    """Return Markdown/YAML AI-EOS files, skipping generated dependency folders."""
    candidates: list[Path] = []
    for base in (root / "AGENTS.md", root / ".ai-eos.yaml"):
        if base.is_file():
            candidates.append(base)

    ai_dir = root / "ai"
    if ai_dir.is_dir():
        for path in ai_dir.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in {".md", ".yaml", ".yml"}
                and not any(part in IGNORED_PARTS for part in path.parts)
            ):
                candidates.append(path)
    return sorted(candidates)


def should_check_placeholders(path: Path) -> bool:
    """Return whether TODO/TBD placeholders should count against this file."""
    name = path.name.lower()
    return not (
        name.endswith("-template.md")
        or name.endswith("-template.yaml")
        or name.endswith("-template.yml")
    )


def parse_iso_date(value: str) -> date | None:
    """Parse YYYY-MM-DD dates, returning None for invalid input."""
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
