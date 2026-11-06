"""Shared names and rules for the skill pack.

The strings here are the contract that skills, fixtures, and the preview
renderer all follow. They are not sample company data.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKILL_NAMES = (
    "weekly-update",
    "incident-postmortem",
    "one-on-one",
    "release-checklist",
)

DISCLAIMER = (
    "FICTIONAL EXAMPLE. Not a real company, team, incident, metric, or person. "
    "Organization: Fictional Harbor Labs."
)

ORG_NAME = "Fictional Harbor Labs"

README_FILES = (
    "README.md",
    "README.zh-Hans.md",
    "README.zh-Hant.md",
    "README.ja.md",
)

LANGUAGE_SWITCH = (
    "[English](README.md) · [简体中文](README.zh-Hans.md) · "
    "[繁體中文](README.zh-Hant.md) · [日本語](README.ja.md)"
)

CLONE_URL = "https://github.com/xuqijx/eng-manager-skills-pack.git"
REPO_URL = "https://github.com/xuqijx/eng-manager-skills-pack"
ALLOWED_URLS = frozenset({CLONE_URL, REPO_URL})

MAX_SKILL_LINES = 500
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500

REQUIRED_SKILL_SECTIONS = (
    "## When to use",
    "## Collect before writing",
    "## Rules",
    "## Output",
    "## Fictional example",
)

INCIDENT_STATUS = frozenset({"Draft", "Active", "Final"})
CONFIDENCE = frozenset({"Confirmed", "Hypothesis", "Unknown"})
ACTION_STATUS = frozenset({"Open", "Done", "Unassigned"})
CHECK_STATUS = frozenset({"Ready", "Not ready", "Not provided"})
DECISION = frozenset({"Go", "No-go", "Not provided"})
FEEDBACK_DIRECTION = frozenset({"manager to report", "report to manager"})

EMPTY_ACCEPTED_RISK = "None stated."
NOT_PROVIDED = "Not provided"

TEMPLATE_HEADINGS = {
    "weekly-update": (
        "# Weekly engineering update",
        "## Headline",
        "## Shipped",
        "## In progress",
        "## Risks and asks",
        "## Metrics",
        "## Next week",
        "## Manager notes (do not forward)",
    ),
    "incident-postmortem": (
        "# Incident postmortem",
        "## Summary",
        "## Impact",
        "## Detection",
        "## Timeline",
        "## Contributing factors",
        "## What worked",
        "## Where we were slow",
        "## Action items",
        "## Drafting notes (do not file)",
    ),
    "one-on-one": (
        "# 1:1 notes",
        "## Their topics",
        "## Manager topics",
        "## Feedback",
        "## Career",
        "## Shared commitments",
        "## Shared note excludes",
        "## Private notes (do not share)",
    ),
    "release-checklist": (
        "# Release checklist",
        "## Scope",
        "## Out of scope",
        "## Checks",
        "## Decision",
        "## Watch window",
        "### Signals",
        "## Drafting notes (do not send)",
    ),
}


@dataclass(frozen=True)
class Schema:
    """JSON shape of one skill's fictional example."""

    strings: tuple[str, ...]
    lists: tuple[str, ...]
    tables: dict[str, tuple[str, ...]]
    optional_strings: tuple[str, ...] = ()


SCHEMAS = {
    "weekly-update": Schema(
        strings=(
            "disclaimer",
            "team",
            "organization",
            "period",
            "timezone",
            "audience",
            "author",
            "headline",
        ),
        lists=(
            "shipped",
            "in_progress",
            "risks_and_asks",
            "metrics",
            "next_week",
            "manager_notes",
        ),
        tables={},
    ),
    "incident-postmortem": Schema(
        strings=(
            "disclaimer",
            "title",
            "service",
            "severity",
            "status",
            "window",
            "timezone",
            "customer_identifiers",
            "summary",
            "detection",
            "drafting_notes",
        ),
        lists=("impact", "what_worked", "what_was_slow"),
        tables={
            "timeline": ("time", "event"),
            "contributing_factors": ("confidence", "statement"),
            "action_items": ("action", "owner", "due", "status"),
        },
    ),
    "one-on-one": Schema(
        strings=(
            "disclaimer",
            "report",
            "manager",
            "relationship",
            "date",
            "duration",
            "career_note",
        ),
        lists=(
            "their_topics",
            "manager_topics",
            "shared_note_excludes",
            "private_notes",
        ),
        tables={
            "feedback": ("direction", "situation", "behavior", "impact"),
            "shared_commitments": ("owner", "action", "when"),
        },
    ),
    "release-checklist": Schema(
        strings=(
            "disclaimer",
            "release",
            "environment",
            "owner",
            "window",
            "decision",
            "decision_note",
            "watch_duration",
            "watch_owner",
            "drafting_notes",
        ),
        lists=("scope", "out_of_scope", "watch_signals"),
        tables={
            "checks": ("name", "status", "evidence", "owner"),
        },
        optional_strings=("accepted_risk",),
    ),
}
