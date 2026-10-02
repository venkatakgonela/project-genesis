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
uv run pytest
uv run ruff check .
uv run mypy genesis/
```

## License

MIT, see [LICENSE](LICENSE).
