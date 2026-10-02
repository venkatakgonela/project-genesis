# PHASE-1-SUMMARY — Project Genesis Foundation

**Status:** COMPLETE — 2026-06-02
**Next phase:** Phase 2 — Templates

---

## Purpose

Genesis is a local CLI tool that generates and maintains an **AI Engineering Operating System (AI-EOS)** inside any software project. It stamps a structured, opinionated folder of living documents so that AI agents, human engineers, and hybrid teams share a single navigable source of truth.

Genesis does not call LLMs, run agents, or connect to external services. It is a pure filesystem bootstrapper.

---

## Architecture

```
[User] ──► genesis CLI (Typer)
                │
                ├── commands/         ← one module per command
                │     init, new, brief, task, migrate
                │
                ├── scaffold.py       ← stateless filesystem helpers
                ├── frontmatter.py    ← manual YAML front matter parser
                ├── template_engine.py ← Jinja2 PackageLoader wrapper
                └── models.py         ← dataclasses (no ORM, no DB)
```

**Data flow (planned, Phase 3+):**
```
Brief file ──► frontmatter.parse() ──► BriefData
ProjectConfig + BriefData ──► template_engine.render() ──► rendered string
rendered string ──► scaffold.write_file() ──► disk
```

**Template location:** `genesis/templates/` (inside the package). Loaded via `PackageLoader("genesis", "templates")` — works in both editable installs and built wheels.

---

## Repository Structure

```
project-genesis/
├── pyproject.toml              # uv, ruff, black, isort, mypy, pytest config
├── .python-version             # 3.12
├── .gitignore
├── README.md
│
├── genesis/
│   ├── __init__.py             # __version__ = "0.1.0"
│   ├── cli.py                  # Typer app, command registration
│   ├── frontmatter.py          # manual parser — zero deps
│   ├── models.py               # ProjectConfig, BriefData, AiEosManifest, RunConfig
│   ├── scaffold.py             # ensure_dir, write_file, file_exists
│   ├── template_engine.py      # render(template_name, context) → str
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── init.py             # stub — Phase 3
│   │   ├── new.py              # stub — Phase 3
│   │   ├── brief.py            # stub — Phase 4
│   │   ├── task.py             # stub — Phase 4
│   │   └── migrate.py          # stub — Phase 4
│   └── templates/
│       └── .gitkeep            # populated in Phase 2
│
├── tests/
│   ├── conftest.py             # project_root fixture (tmp_path)
│   ├── test_frontmatter.py     # 16 tests
│   └── test_scaffold.py        # 16 tests
│
└── ai/
    └── runs/
        └── RUN-001-phase1-foundation.md
```

---

## Implemented Components

### `genesis/frontmatter.py`

```python
parse(text: str) -> tuple[dict[str, str], str]
```

- Parses flat `key: value` YAML front matter delimited by `---`
- Returns `(metadata_dict, body_text)`
- Returns `({}, text)` when no front matter block is present
- Raises `ValueError` if an opening `---` has no closing `---`
- Values containing colons are correctly preserved (uses `str.partition(":")`)
- Zero external dependencies

### `genesis/scaffold.py`

```python
ensure_dir(path: Path) -> None
write_file(path: Path, content: str, *, force: bool = False) -> bool
file_exists(path: Path) -> bool
```

- `write_file` returns `True` if written, `False` if skipped (existing file + no force)
- Creates all parent directories automatically
- Stateless — no echo or logging; callers handle output
- `file_exists` uses `Path.is_file()` — returns `False` for directories

### `genesis/models.py`

| Dataclass | Purpose |
|---|---|
| `ProjectConfig` | name, type, owner, description for a project |
| `BriefData` | parsed brief metadata + body text |
| `ManifestEntry` | single `{path, template}` entry in the manifest |
| `AiEosManifest` | `.ai-eos.yaml` contents: version, created, project, archetype, manifest |
| `RunConfig` | schema for `ai/runs/run.yaml` (written as template, not parsed) |

### `genesis/template_engine.py`

```python
render(template_name: str, context: dict[str, object]) -> str
```

- Backed by `PackageLoader("genesis", "templates")`
- `autoescape` disabled (Markdown output)
- `keep_trailing_newline=True`
- Silent `Undefined` — missing vars render as empty string; use `| default('TBD')` in templates

### `genesis/cli.py`

```
genesis --version
genesis init       [--force]
genesis new        --name <name> --type <type>
genesis brief      <brief-file> [--force]
genesis task       <task-name>
genesis migrate    [--dry-run]
```

Reserved (hidden, exit code 1, not implemented):
- `genesis analyze`
- `genesis doctor`
- `genesis refresh`

---

## AI-EOS Output Structure

Written into a target project by `genesis init` or `genesis new` (Phase 3):

```
.ai-eos.yaml
AGENTS.md
ai/
  00-project-charter.md      
  01-architecture.md         specs/  SPEC-000-template.md
  02-domain-model.md         tasks/  TASK-000-template.md
  03-repo-map.md             skills/ (6 skill files)
  04-decisions.md            runs/   RUN-000-template.md + run.yaml
  05-coding-standards.md     roadmap/ ROADMAP.md
  06-agentic-sdlc.md         epics/   EPIC-000-template.md
  07-observability.md        features/ FEATURE-000-template.md
  08-risk-register.md        agents/  AGENT-000-template.md
                             context-packs/ context-pack-default.md
```

**Total: ~28 files across 12 folders.**

### `.ai-eos.yaml` Manifest

Written by `init`/`new`. Read by `migrate`. Schema:

```yaml
genesis_version: "0.1.0"
created: "2026-06-02T18:09:36"
project:
  name: ""
  type: "default"
  owner: ""
  description: ""
archetype: "default"
manifest:
  - path: AGENTS.md
    template: AGENTS.md.j2
  # ... one entry per generated file
```

---

## Constraints

These are fixed for v1 — do not introduce:

| Constraint | Reason |
|---|---|
| No LLM API calls | Genesis writes files; agents read them |
| No MCP integration | Out of scope for v1 |
| No database | Everything is plain Markdown and YAML |
| No web UI | CLI only |
| No multi-agent runtime | Out of scope for v1 |
| No external deps beyond Typer + Jinja2 | Minimal surface area |
| No parent directory inspection | Only operates within the target project |
| Only `default` archetype rendered | Archetype system is v2 |

---

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Front matter | Manual parser | Zero deps; only flat key/value needed |
| Template location | Inside package (`genesis/templates/`) | Works in editable + wheel installs |
| Template variables | Silent `Undefined` + `\| default('TBD')` | Safe degradation when brief is incomplete |
| Conflict strategy | Skip by default, `--force` to overwrite | Safe on re-runs |
| Scaffold helpers | Stateless, no echo | Composable; callers control output |
| `run.yaml` | Written as template, never parsed | Genesis is a writer, not a runner |
| Archetype | `default` only in v1 | Deferred to v2; `--type` stored in manifest |
| Reserved commands | Hidden, exit code 1 | Reserves namespace; clear user messaging |

---

## Quality Gates (must pass before any phase is declared complete)

```bash
uv run pytest -v          # all tests pass
uv run ruff check .       # zero lint errors
uv run black --check .    # zero format errors
uv run isort --check .    # zero import order errors
uv run mypy genesis/      # zero type errors
```

Phase 1 result: **32/32 tests, all linters clean, 12 source files typed.**

---

## Remaining Work

### Phase 2 — Templates
Write all ~28 Jinja2 `.j2` files into `genesis/templates/`. Each template must:
- Include a heading and purpose block
- Use `{{ variable | default('TBD') }}` for all injected values
- End with a trailing newline
- Cover: AGENTS.md, 9 ai/ docs, specs, tasks, 6 skills, runs (md + yaml), roadmap, epics, features, agents, context-packs

### Phase 3 — `init` and `new` commands
- Implement `commands/init.py` — render all templates into cwd, write `.ai-eos.yaml`
- Implement `commands/new.py` — create `<name>/` sub-folder, same scaffold
- Add `tests/test_init.py`, `tests/test_new.py`

### Phase 4 — `brief`, `task`, `migrate` commands
- Implement `commands/brief.py` — parse brief → render ai/ docs
- Implement `commands/task.py` — auto-number (count `TASK-*.md`), slugify, write
- Implement `commands/migrate.py` — diff manifest vs disk, add missing, `--dry-run`
- Add `tests/test_brief.py`, `tests/test_task.py`, `tests/test_migrate.py`

### Phase 5 — Polish
- Final lint + type pass across all phases
- `README.md` updated with full usage docs and examples
