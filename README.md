# Project Genesis

A command-line tool, in early development, for stamping an **engineering operating context** into a software project so human engineers and AI coding agents share one navigable source of truth: project charter, architecture notes, agent rules (`AGENTS.md`), specs, tasks, decisions and run records.

> **Status: Phase 1 (foundation). The user-facing commands are not implemented yet.** `genesis init`, `new`, `brief`, `task` and `migrate` are registered as placeholders and print "not yet implemented". What exists today is the tested groundwork the commands will build on.

## What works today

- Typer CLI skeleton and command registration (`genesis --help`)
- Safe filesystem helpers: existing files are never overwritten without an explicit force flag
- A small dependency-free front-matter parser for Markdown briefs
- Typed data models for project config, briefs, manifests and run records
- A Jinja2 template-rendering wrapper (the template set itself is not written yet)
- 32 unit tests, with `ruff` and `mypy` clean

## Planned

| Command | Intent | Status |
| --- | --- | --- |
| `genesis init` | Create the operating-context structure in the current project | planned |
| `genesis new` | Create a new project folder with that structure | planned |
| `genesis brief <file>` | Generate documents from a project brief | planned |
| `genesis task <name>` | Create a numbered task file | planned |
| `genesis migrate` | Add missing files to an existing project | planned |

## Design principles

- No LLM calls: Genesis writes files, agents read them
- No database, no web UI: plain Markdown and YAML
- Safe by default: no silent overwrites
- Minimal runtime dependencies (Typer, Jinja2)

## Development

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/venkatakgonela/project-genesis
cd project-genesis
uv sync
uv pip install -e .
```

Verify:

```bash
genesis --help
```

## Commands

| Command | Description |
|---|---|
| `genesis init` | Initialise AI-EOS in the current directory |
| `genesis new --name X --type Y` | Create a new project folder with AI-EOS scaffolding |
| `genesis brief <file>` | Generate AI-EOS documents from a project brief |
| `genesis task <name>` | Create a numbered task file in `ai/tasks/` |
| `genesis migrate` | Add missing AI-EOS files to an existing project |
| `genesis analyze` | Inspect project stack signals, AI-EOS inventory, and likely quality gates |
| `genesis doctor` | Diagnose AI-EOS structure, placeholders, stale docs, and context hygiene |

## Quick Start

```bash
mkdir my-project && cd my-project
genesis init
```

This writes the full AI-EOS structure:

```
.ai-eos.yaml
AGENTS.md
ai/
  00-project-charter.md
  01-architecture.md
  ...
  roadmap/
  epics/
  features/
  agents/
  context-packs/
  runs/
    run.yaml
```

## Development

```bash
uv sync
uv run pytest -v
uv run ruff check .
uv run mypy genesis/
```

Use `genesis doctor` inside a project that has been initialised with AI-EOS to check structure,
placeholder drift, stale review dates, and context-pack hygiene.

## Design Principles

- **No LLM calls** — Genesis writes files; agents read them
- **No database** — everything is plain Markdown and YAML
- **No web UI** — CLI only
- **Safe by default** — existing files are never overwritten without `--force`
- **Minimal dependencies** — only Typer and Jinja2 at runtime

## Versioning

Genesis follows [Semantic Versioning](https://semver.org/). The `.ai-eos.yaml` manifest records which genesis version created the structure, enabling future `genesis migrate` upgrades.

## License

MIT, see [LICENSE](LICENSE).
