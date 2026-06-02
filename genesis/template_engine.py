"""Jinja2 template engine wrapper.

Templates are bundled inside the ``genesis`` package under the
``templates/`` sub-directory and loaded via ``PackageLoader``.
This ensures they are correctly resolved whether Genesis is installed
as a wheel or run from an editable source checkout.

Usage::

    from genesis.template_engine import render

    content = render("AGENTS.md.j2", {"project_name": "payments-service"})

Undefined variables in templates render as empty strings by default.
Use the ``| default('TBD')`` filter for explicit fallbacks.
"""

from __future__ import annotations

from jinja2 import Environment, PackageLoader, Undefined, select_autoescape


def _make_env() -> Environment:
    """Construct a Jinja2 Environment backed by the bundled templates."""
    return Environment(
        loader=PackageLoader("genesis", "templates"),
        autoescape=select_autoescape([]),  # Markdown — no HTML escaping
        keep_trailing_newline=True,
        undefined=Undefined,  # silent undefined; use | default('TBD') in templates
    )


def render(template_name: str, context: dict[str, object]) -> str:
    """Render a template by name with the given context variables.

    Args:
        template_name: Relative path to the template inside ``genesis/templates/``,
                       e.g. ``"AGENTS.md.j2"`` or ``"ai/00-project-charter.md.j2"``.
        context:       Template variables to inject.

    Returns:
        Rendered string content.

    Raises:
        jinja2.TemplateNotFound: If *template_name* does not exist.
    """
    env = _make_env()
    tmpl = env.get_template(template_name)
    return tmpl.render(**context)
