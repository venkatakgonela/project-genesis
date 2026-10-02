"""Single source of truth for AI-EOS template-to-output mappings."""

from __future__ import annotations

TEMPLATES: dict[str, str] = {
    ".ai-eos.yaml.j2": ".ai-eos.yaml",
    "AGENTS.md.j2": "AGENTS.md",
    "ai/00-project-charter.md.j2": "ai/00-project-charter.md",
    "ai/01-architecture.md.j2": "ai/01-architecture.md",
    "ai/02-domain-model.md.j2": "ai/02-domain-model.md",
    "ai/03-repo-map.md.j2": "ai/03-repo-map.md",
    "ai/04-decisions.md.j2": "ai/04-decisions.md",
    "ai/05-coding-standards.md.j2": "ai/05-coding-standards.md",
    "ai/06-agentic-sdlc.md.j2": "ai/06-agentic-sdlc.md",
    "ai/07-observability.md.j2": "ai/07-observability.md",
    "ai/08-risk-register.md.j2": "ai/08-risk-register.md",
    "ai/roadmap/ROADMAP.md.j2": "ai/roadmap/ROADMAP.md",
    "ai/specs/SPEC-000-template.md.j2": "ai/specs/SPEC-000-template.md",
    "ai/tasks/TASK-000-template.md.j2": "ai/tasks/TASK-000-template.md",
    "ai/epics/EPIC-000-template.md.j2": "ai/epics/EPIC-000-template.md",
    "ai/features/FEATURE-000-template.md.j2": "ai/features/FEATURE-000-template.md",
    "ai/agents/AGENT-000-template.md.j2": "ai/agents/AGENT-000-template.md",
    "ai/context-packs/context-pack-default.md.j2": "ai/context-packs/context-pack-default.md",
    "ai/skills/feature-development.md.j2": "ai/skills/feature-development.md",
    "ai/skills/regression-testing.md.j2": "ai/skills/regression-testing.md",
    "ai/skills/refactoring.md.j2": "ai/skills/refactoring.md",
    "ai/skills/database-migration.md.j2": "ai/skills/database-migration.md",
    "ai/skills/ui-change.md.j2": "ai/skills/ui-change.md",
    "ai/skills/documentation-update.md.j2": "ai/skills/documentation-update.md",
    "ai/runs/RUN-000-template.md.j2": "ai/runs/RUN-000-template.md",
    "ai/runs/run.yaml.j2": "ai/runs/run.yaml",
}
