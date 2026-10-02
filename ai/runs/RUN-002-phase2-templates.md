# RUN-002 — Phase 2 Templates

| Field            | Value                                      |
|------------------|--------------------------------------------|
| **Run ID**       | RUN-002                                    |
| **Phase**        | Phase 2 — Templates                        |
| **Date**         | 2026-06-02                                 |
| **Status**       | COMPLETE                                   |
| **Decision**     | Approved                                   |

---

## Goal

Create all Jinja2 templates required by the AI-EOS output structure. Implement corrections on risk-register naming, reserve future manifest fields, document stubs backlog, and add template unit tests.

---

## Files Added / Modified

### Package Templates — `genesis/templates/`

- `genesis/templates/.ai-eos.yaml.j2`
- `genesis/templates/AGENTS.md.j2`
- `genesis/templates/ai/00-project-charter.md.j2`
- `genesis/templates/ai/01-architecture.md.j2`
- `genesis/templates/ai/02-domain-model.md.j2`
- `genesis/templates/ai/03-repo-map.md.j2`
- `genesis/templates/ai/04-decisions.md.j2`
- `genesis/templates/ai/05-coding-standards.md.j2`
- `genesis/templates/ai/06-agentic-sdlc.md.j2`
- `genesis/templates/ai/07-observability.md.j2`
- `genesis/templates/ai/08-risk-register.md.j2`
- `genesis/templates/ai/roadmap/ROADMAP.md.j2`
- `genesis/templates/ai/specs/SPEC-000-template.md.j2`
- `genesis/templates/ai/tasks/TASK-000-template.md.j2`
- `genesis/templates/ai/epics/EPIC-000-template.md.j2`
- `genesis/templates/ai/features/FEATURE-000-template.md.j2`
- `genesis/templates/ai/agents/AGENT-000-template.md.j2`
- `genesis/templates/ai/context-packs/context-pack-default.md.j2`
- `genesis/templates/ai/skills/feature-development.md.j2`
- `genesis/templates/ai/skills/regression-testing.md.j2`
- `genesis/templates/ai/skills/refactoring.md.j2`
- `genesis/templates/ai/skills/database-migration.md.j2`
- `genesis/templates/ai/skills/ui-change.md.j2`
- `genesis/templates/ai/skills/documentation-update.md.j2`
- `genesis/templates/ai/runs/RUN-000-template.md.j2`
- `genesis/templates/ai/runs/run.yaml.j2`

### Package Sources & CLI

- `genesis/cli.py` (modified to include backlog notes for `analyze`, `doctor`, and `refresh`)
- `genesis/models.py` (modified to document reserved `ai_eos_version` field)

### Tests

- `tests/test_templates.py` (new tests checking existence, parsing, rendering correctness, and output validation)

---

## Commands Executed

```bash
# Formatted tests file
uv run black .

# Fixed import sort issues in tests
uv run ruff check . --fix

# Tests verification
uv run pytest -v

# Linters verification
uv run ruff check .
uv run black --check .
uv run isort --check .

# Type checking verification
uv run mypy genesis/
uv run mypy tests/
```

---

## Results

| Check         | Outcome                                   |
|---------------|-------------------------------------------|
| `pytest`      | ✅ 87 / 87 passed                          |
| `ruff`        | ✅ All checks passed                      |
| `black`       | ✅ 17 files unchanged                     |
| `isort`       | ✅ Passed (3 files skipped)               |
| `mypy`        | ✅ No issues found in source + test files |

---

## Review Notes & Assumptions

- All templates contain a metadata block describing purpose, usage, generator, and regeneration strategy.
- Every variable is configured with default fallbacks `| default('TBD')` to allow graceful rendering on incomplete context.
- Numbering consistency is resolved: `08-risk-register.md` is utilized uniformly across the manifest, readme, and templates.
- Future field `ai_eos_version` is documented in comments and docstrings.
