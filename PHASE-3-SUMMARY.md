# PHASE-3-SUMMARY — Project Genesis Init & New Commands

**Status:** COMPLETE — 2026-06-02  
**Next phase:** Phase 4 — `brief`, `task`, and `migrate` commands  

---

## Purpose

Phase 3 implements the project scaffolding and bootstrapping functionality via the `genesis init` and `genesis new` CLI commands. These commands deploy the 26 standard templates forming the AI Engineering Operating System (AI-EOS) into target folders, safely skipping or forcing file writes as instructed.

---

## Implemented Components & Architecture

### Single Source of Truth for Mappings
- **`genesis/manifest.py`**: Added this module to hold `TEMPLATES: dict[str, str]` as the central source of truth for mapping every `.j2` template to its destination relative path.

### Scaffolding Logic
- **`genesis/scaffold.py`**: Added `scaffold_project(target_dir: Path, context: dict[str, object], *, force: bool = False) -> tuple[int, int]`. A stateless function that iterates over templates, resolves destination paths, renders content, writes to the filesystem, and returns the count of files written and skipped.

### CLI Commands
- **`genesis/commands/init.py`**:
  - Automatically targets the current working directory.
  - Automatically structures context with defaults and current UTC timestamp.
  - Deploys full AI-EOS structure.
  - Exposes `--force` / `-f` option to override skips.
- **`genesis/commands/new.py`**:
  - Targets `<CWD>/<name>` subfolder.
  - Injects CLI `--name` and `--type` into templates context.
  - Safely handles existing directories.

---

## Quality Gates & Verification

Comprehensive CLI and integration unit tests were introduced:
- **`tests/test_init.py`**:
  - Verifies bootstrap creation of `.ai-eos.yaml`, `AGENTS.md`, and all `ai/` docs.
  - Verifies creation of all nested directories (`specs`, `tasks`, etc.).
  - Verifies default metadata injection and that no unresolved Jinja syntax leaks.
  - Verifies skipping existing files by default and overwriting with `--force`.
- **`tests/test_new.py`**:
  - Verifies subfolder creation and CLI argument injection (`name`, `type`).
  - Verifies no modification is done outside the target directory.
  - Verifies safe handling of pre-existing subfolders.

Results:
- **`pytest`**: 94 passed / 94 total
- **`ruff`**: Clean lint check (including fix for `datetime.UTC`)
- **`black`**: Clean formatting
- **`isort`**: Clean import sorting
- **`mypy`**: Strict type checking passed for both package source (`genesis/`) and test suites (`tests/`).

---

## Next Steps

### Phase 4 — `brief`, `task`, `migrate` commands
- Implement brief parsing (`genesis brief`) to customize operating system configurations.
- Implement TASK auto-numbering and file generation (`genesis task`).
- Implement structure migrations and structural diffs check (`genesis migrate`).
