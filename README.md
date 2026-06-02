# Project Genesis

> **AI-EOS Generator** — bootstrap and maintain an AI Engineering Operating System inside any software project.

Genesis is a local CLI tool that stamps a structured, opinionated operating context into software projects so AI agents, human engineers, and hybrid teams share a single navigable source of truth.

## What is AI-EOS?

An **AI Engineering Operating System (AI-EOS)** is a curated folder of living documents that:

- Define how this project works (architecture, domain model, standards)
- Describe how AI agents should behave (AGENTS.md, skills, context-packs)
- Track work at every level (specs, tasks, epics, features, roadmap)
- Record decisions and risk (decisions, risk register)
- Structure agentic runs (runs/, run.yaml)

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/your-org/project-genesis
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

## Design Principles

- **No LLM calls** — Genesis writes files; agents read them
- **No database** — everything is plain Markdown and YAML
- **No web UI** — CLI only
- **Safe by default** — existing files are never overwritten without `--force`
- **Minimal dependencies** — only Typer and Jinja2 at runtime

## Versioning

Genesis follows [Semantic Versioning](https://semver.org/). The `.ai-eos.yaml` manifest records which genesis version created the structure, enabling future `genesis migrate` upgrades.

## License

MIT
