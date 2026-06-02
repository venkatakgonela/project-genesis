"""Data models for Genesis."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProjectConfig:
    """Configuration for a single AI-EOS project."""

    name: str
    type: str = "default"
    owner: str = ""
    description: str = ""


@dataclass
class BriefData:
    """Parsed data extracted from a project brief Markdown file."""

    title: str = ""
    type: str = "default"
    description: str = ""
    owner: str = ""
    body: str = ""


@dataclass
class ManifestEntry:
    """A single generated file recorded in the AI-EOS manifest."""

    path: str
    template: str


@dataclass
class AiEosManifest:
    """Contents of the .ai-eos.yaml file written into a project root.

    Records which genesis version created the structure, the project
    metadata, and a full list of generated files. Used by ``genesis migrate``
    to compute structural diffs.
    """

    genesis_version: str
    created: str  # ISO 8601 string — no datetime dep needed
    project: ProjectConfig
    archetype: str = "default"
    manifest: list[ManifestEntry] = field(default_factory=list)


@dataclass
class RunConfig:
    """Schema for ai/runs/run.yaml — consumed by agent runners, not Genesis."""

    id: str = "RUN-001"
    name: str = ""
    goal: str = ""
    agent_role: str = ""
    context_pack: str = "ai/context-packs/context-pack-default.md"
    tasks: list[str] = field(default_factory=list)
