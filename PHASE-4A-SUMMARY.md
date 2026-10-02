# PHASE-4A-SUMMARY — Project Genesis Brief & Task Commands

**Status:** COMPLETE — 2026-06-02  
**Next phase:** Phase 4B — `migrate` command (future phase)

---

## Purpose

Phase 4A implements project setup customization from markdown briefs (`genesis brief`) and auto-numbered developer task card generation (`genesis task`). These features leverage the template engine and local project metadata to bootstrap custom structured AI-EOS directory states and individual task lists.

---

## Implemented Components & Architecture

### Custom Templates Configuration
- **`genesis/templates/ai/tasks/TASK-000-template.md.j2`**: Refactored to support direct Jinja2 context variables (`task_id`, `task_name`, `task_slug`, `created_date`, `status`).
- **`genesis/templates/ai/00-project-charter.md.j2`**: Integrated parsed brief sections (`purpose`, `users`, `requirements`, `scope`, `non_goals`) to populate project mission and goals.
- **`genesis/templates/ai/01-architecture.md.j2`**: Integrated parsed `constraints` to populate tech stack constraints.

### Custom Brief Scaffolding
- **`genesis/commands/brief.py`**:
  - Leverages existing front matter parser to extract core metadata (mapping `title` -> `project_name`, `type` -> `project_type`, `owner` -> `project_owner`, `description` -> `project_description`).
  - Implements a rule-based deterministic markdown header parser for six core sections: **Purpose**, **Users**, **Requirements**, **Constraints**, **Scope**, and **Non Goals** (supporting aliases like `Non-Goals`).
  - Supports `--force` / `-f` CLI option to overwrite existing scaffolding.
  - Returns a detailed summary of files written, skipped, and sections discovered.

### Task Generation
- **`genesis/commands/task.py`**:
  - Automatically calculates next sequential ID (`TASK-XXX`) by scanning `ai/tasks/TASK-*.md` in CWD (handling gaps gracefully).
  - Slugifies the task name for the filename.
  - Safely reads the project owner from `.ai-eos.yaml` in CWD if available.
  - **Preferred Behavior**: Renders the packaged template directly with complete Jinja2 context.
  - **Fallback Behavior**: In the presence of a local custom `ai/tasks/TASK-000-template.md` template override, carefully substitutes placeholders to preserve user formatting.
  - Enforces write-safety (never overwrites existing tasks) and prints the relative created file path.

---

## Quality Gates & Verification

Comprehensive CLI and integration unit tests were introduced:
- **`tests/test_brief.py`**:
  - Verifies setup from a valid brief file.
  - Verifies fallback handling when sections are missing.
  - Verifies behavior without front matter.
  - Verifies skipped/force write strategies.
  - Verifies metadata and parsed sections propagate cleanly to files (e.g. `ai/00-project-charter.md` and `ai/01-architecture.md`).
  - Verifies zero Jinja2 variable leakage in all output files.
- **`tests/test_task.py`**:
  - Verifies first task auto-generation starts at `TASK-001`.
  - Verifies sequential increment numbering across multiple task creations.
  - Verifies highest index sequence calculation even when gaps exist (e.g. `TASK-005` exists, creates `TASK-006`).
  - Verifies metadata extraction from local `.ai-eos.yaml`.
  - Verifies local custom template override replacement fallback.
  - Verifies safety constraints preventing file overwrites.

Results:
- **`pytest`**: ✅ 105 passed
- **`ruff` check**: ✅ All checks passed
- **`black` check**: ✅ Formatting clean
- **`isort` check**: ✅ Import ordering clean
- **`mypy` checks**: ✅ Strict type checks passed (`genesis/` and `tests/`)
