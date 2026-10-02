# RUN-003 — Phase 3 Init & New Commands

| Field            | Value                                      |
|------------------|--------------------------------------------|
| **Run ID**       | RUN-003                                    |
| **Phase**        | Phase 3 — Init & New Commands              |
| **Date**         | 2026-06-02                                 |
| **Status**       | COMPLETE                                   |
| **Decision**     | Approved                                   |

---

## Goal

Implement the `genesis init [--force]` and `genesis new --name <name> --type <type>` commands. Ensure that they correctly deploy all 26 templates, write `.ai-eos.yaml`, handle pre-existing directories gracefully, and prevent Jinja variable leakages.

---

## Files Added / Modified

### Package Sources & Commands

- `genesis/manifest.py` (new mapping source of truth)
- `genesis/scaffold.py` (modified to add `scaffold_project` function)
- `genesis/commands/init.py` (implemented `init` CLI command)
- `genesis/commands/new.py` (implemented `new` CLI command)

### Tests

- `tests/test_templates.py` (modified to use central `TEMPLATES` from `genesis/manifest.py`)
- `tests/test_init.py` (new tests checking `init` CLI results, defaults, --force, skips, directories)
- `tests/test_new.py` (new tests checking `new` CLI results, subfolder isolates, safety checks)

### Documentation & Summaries

- `PHASE-3-SUMMARY.md` (project summary)
- `ai/runs/RUN-003-phase3-init-new.md` (this file)

---

## Commands Executed

```bash
# Sorted and auto-fixed imports
uv run ruff check . --fix

# Re-formatted code
uv run black .

# Checked quality gate compliance
uv run pytest -v
uv run ruff check .
uv run black --check .
uv run isort --check .
uv run mypy genesis/
uv run mypy tests/
```

---

## Results

| Check         | Outcome                                   |
|---------------|-------------------------------------------|
| `pytest`      | ✅ 94 / 94 passed (0.20s)                 |
| `ruff`        | ✅ All checks passed                      |
| `black`       | ✅ 20 files unchanged                     |
| `isort`       | ✅ Passed (3 files skipped)               |
| `mypy`        | ✅ No issues found in source + test files |

---

## Review Notes & Assumptions

- Mappings are centrally defined in `genesis/manifest.py` and reused by commands and tests.
- File names are derived from template names by stripping `.j2`.
- Target directories are created cleanly, using standard `pathlib.Path` structures.
- All files written contain defaults (such as `TBD` or standard project descriptions) without leaking unresolved Jinja delimiters.
- Skipped/Force strategies are fully verified: `--force` on `init` overrides existing files, while `new` skips safely and is not expanded with `--force` as the stub didn't originally expose it.
