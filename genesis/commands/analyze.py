"""genesis analyze - inspect a project for AI-EOS and stack signals."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import typer

from genesis.manifest import TEMPLATES


@dataclass(frozen=True)
class StackSignal:
    """A detected project stack signal."""

    name: str
    path: str


@dataclass(frozen=True)
class ProjectAnalysis:
    """Read-only project analysis summary."""

    root: Path
    canonical_files_present: int
    canonical_files_total: int
    stack_signals: list[StackSignal] = field(default_factory=list)
    quality_gates: list[str] = field(default_factory=list)
    ai_counts: dict[str, int] = field(default_factory=dict)


def run() -> None:
    """Inspect project structure and print stack/context guidance."""
    root = Path.cwd()
    analysis = analyze_project(root)

    typer.echo("Project analysis")
    typer.echo(f"  Target directory: {analysis.root}")
    typer.echo(
        "  AI-EOS files: "
        f"{analysis.canonical_files_present}/{analysis.canonical_files_total}"
    )

    typer.echo("")
    typer.echo("Stack signals:")
    if analysis.stack_signals:
        for signal in analysis.stack_signals:
            typer.echo(f"  - {signal.name}: {signal.path}")
    else:
        typer.echo("  - None detected")

    typer.echo("")
    typer.echo("AI-EOS inventory:")
    if analysis.ai_counts:
        for label, count in analysis.ai_counts.items():
            typer.echo(f"  - {label}: {count}")
    else:
        typer.echo("  - No ai/ inventory detected")

    typer.echo("")
    typer.echo("Likely quality gates:")
    if analysis.quality_gates:
        for command in analysis.quality_gates:
            typer.echo(f"  - {command}")
    else:
        typer.echo("  - None inferred; document exact commands in AGENTS.md")

    typer.echo("")
    typer.echo("Next step: run `genesis doctor` for health and drift checks.")


def analyze_project(root: Path) -> ProjectAnalysis:
    """Return a read-only stack and AI-EOS inventory for *root*."""
    canonical_present = sum(1 for rel_path in TEMPLATES.values() if (root / rel_path).is_file())
    stack_signals = detect_stack_signals(root)
    quality_gates = infer_quality_gates(root, stack_signals)
    ai_counts = count_ai_inventory(root)

    return ProjectAnalysis(
        root=root,
        canonical_files_present=canonical_present,
        canonical_files_total=len(TEMPLATES),
        stack_signals=stack_signals,
        quality_gates=quality_gates,
        ai_counts=ai_counts,
    )


def detect_stack_signals(root: Path) -> list[StackSignal]:
    """Detect common project technologies from stable file markers."""
    signals: list[StackSignal] = []
    markers = [
        ("Python project", "pyproject.toml"),
        ("Node package", "package.json"),
        ("Frontend package", "frontend/package.json"),
        ("FastAPI app", "app/main.py"),
        ("Alembic migrations", "alembic.ini"),
        ("Docker Compose runtime", "docker-compose.yml"),
        ("Backend tests", "tests"),
        ("Frontend E2E tests", "frontend/playwright.config.ts"),
        ("Frontend unit tests", "frontend/vitest.config.ts"),
    ]

    for name, rel_path in markers:
        if (root / rel_path).exists():
            signals.append(StackSignal(name=name, path=rel_path))
    return signals


def infer_quality_gates(root: Path, signals: list[StackSignal]) -> list[str]:
    """Infer likely quality gate commands without executing anything."""
    gates: list[str] = []
    signal_names = {signal.name for signal in signals}

    if "Python project" in signal_names:
        gates.extend(["uv run ruff check .", "uv run pytest"])

    gates.extend(package_json_gates(root / "package.json", prefix=""))
    gates.extend(package_json_gates(root / "frontend/package.json", prefix="cd frontend && "))

    if "Alembic migrations" in signal_names:
        gates.append("uv run alembic upgrade head")

    return dedupe_preserve_order(gates)


def package_json_gates(path: Path, *, prefix: str) -> list[str]:
    """Infer npm gates from package.json scripts."""
    if not path.is_file():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return []

    preferred = ["lint", "test", "build", "test:e2e"]
    return [f"{prefix}npm run {name}" for name in preferred if name in scripts]


def count_ai_inventory(root: Path) -> dict[str, int]:
    """Count AI-EOS planning artifacts by common folder."""
    ai_dir = root / "ai"
    if not ai_dir.is_dir():
        return {}

    inventory_paths = {
        "specs": ai_dir / "specs",
        "tasks": ai_dir / "tasks",
        "runs": ai_dir / "runs",
        "context packs": ai_dir / "context-packs",
        "skills": ai_dir / "skills",
        "ADRs/decisions": ai_dir / "04-decisions.md",
        "risk register": ai_dir / "08-risk-register.md",
    }

    counts: dict[str, int] = {}
    for label, path in inventory_paths.items():
        if path.is_dir():
            counts[label] = len(sorted(path.glob("*.md")))
        elif path.is_file():
            counts[label] = 1
    return counts


def dedupe_preserve_order(values: list[str]) -> list[str]:
    """Return unique strings while preserving first-seen order."""
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
