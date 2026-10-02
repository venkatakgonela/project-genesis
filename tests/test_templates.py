"""Unit tests for Jinja2 templates in Genesis."""

from __future__ import annotations

import pytest
from jinja2 import Environment, PackageLoader

from genesis.manifest import TEMPLATES
from genesis.template_engine import render

# Full list of 26 templates expected to exist inside genesis/templates/
EXPECTED_TEMPLATES = list(TEMPLATES.keys())


class TestTemplatesExist:
    def test_all_expected_templates_are_discoverable(self) -> None:
        """Verify that all 26 templates exist and are discoverable via PackageLoader."""
        env = Environment(loader=PackageLoader("genesis", "templates"))
        loaded_templates = env.list_templates()

        # Ensure every expected template is present in the loaded list
        for tmpl in EXPECTED_TEMPLATES:
            assert (
                tmpl in loaded_templates
            ), f"Template {tmpl} was not found by Jinja2 package loader"


class TestTemplatesRender:
    @pytest.mark.parametrize("template_name", EXPECTED_TEMPLATES)
    def test_renders_with_empty_context(self, template_name: str) -> None:
        """Verify that templates render successfully without raising syntax/undefined errors."""
        rendered = render(template_name, {})
        assert isinstance(rendered, str)
        assert len(rendered) > 0
        assert rendered.endswith(
            "\n"
        ), f"Template {template_name} should end with a trailing newline"

    @pytest.mark.parametrize("template_name", EXPECTED_TEMPLATES)
    def test_no_unresolved_jinja_syntax(self, template_name: str) -> None:
        """Verify that no unresolved Jinja delimiters remain in the rendered content."""
        context: dict[str, object] = {
            "project_name": "TestProj",
            "project_type": "python-api",
            "project_owner": "test-owner",
            "project_description": "A test project",
            "genesis_version": "0.1.0",
            "created": "2026-06-02T18:09:36",
            "archetype": "default",
            "agent_model": "Gemini 3.5 Flash",
            "run_id": "RUN-001",
            "run_name": "Phase 2 Run",
            "run_goal": "Implement templates",
            "agent_role": "developer",
            "context_pack": "ai/context-packs/context-pack-default.md",
            "task_file": "ai/tasks/TASK-001-example.md",
        }
        rendered = render(template_name, context)
        assert (
            "{{" not in rendered
        ), f"Found unresolved '{{{{' in rendered {template_name}"
        assert (
            "}}" not in rendered
        ), f"Found unresolved '}}}}' in rendered {template_name}"
        assert (
            "{%" not in rendered
        ), f"Found unresolved '{{%' in rendered {template_name}"
        assert (
            "%}" not in rendered
        ), f"Found unresolved '%}}' in rendered {template_name}"


class TestSpecificTemplates:
    def test_ai_eos_yaml_renders_correctly(self) -> None:
        """Verify structural correctness of rendered .ai-eos.yaml."""
        context: dict[str, object] = {
            "project_name": "MyCoolProject",
            "project_type": "python-api",
            "project_owner": "Alice",
            "project_description": "Handles payment processing",
            "genesis_version": "0.1.0",
            "created": "2026-06-02T18:09:36",
            "archetype": "default",
        }
        rendered = render(".ai-eos.yaml.j2", context)

        # Check specific YAML structural outputs
        assert 'genesis_version: "0.1.0"' in rendered
        assert 'created: "2026-06-02T18:09:36"' in rendered
        assert 'name: "MyCoolProject"' in rendered
        assert 'type: "python-api"' in rendered
        assert 'owner: "Alice"' in rendered
        assert 'description: "Handles payment processing"' in rendered
        assert 'archetype: "default"' in rendered
        assert "manifest:" in rendered

        # Verify it lists key files
        assert "- path: AGENTS.md" in rendered
        assert "template: AGENTS.md.j2" in rendered
        assert "- path: ai/08-risk-register.md" in rendered
        assert "template: ai/08-risk-register.md.j2" in rendered

    def test_run_yaml_renders_correctly(self) -> None:
        """Verify structural correctness of rendered run.yaml."""
        context: dict[str, object] = {
            "run_id": "RUN-002",
            "run_name": "Phase 2 Run",
            "run_goal": "Verify templates",
            "agent_role": "tester",
            "context_pack": "ai/context-packs/context-pack-custom.md",
            "task_file": "ai/tasks/TASK-005-verify-code.md",
        }
        rendered = render("ai/runs/run.yaml.j2", context)

        assert 'id: "RUN-002"' in rendered
        assert 'name: "Phase 2 Run"' in rendered
        assert 'goal: "Verify templates"' in rendered
        assert 'agent_role: "tester"' in rendered
        assert 'context_pack: "ai/context-packs/context-pack-custom.md"' in rendered
        assert '- "ai/tasks/TASK-005-verify-code.md"' in rendered
