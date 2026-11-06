"""Fill each skill template from an example object.

Rendering is substitution only. Wording that is not in the template or the
example is limited to table headers, list markers, and the empty-risk token.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from empack.contract import (
    EMPTY_ACCEPTED_RISK,
    NOT_PROVIDED,
    ROOT,
    SKILL_NAMES,
    SCHEMAS,
)

_PLACEHOLDER = re.compile(r"\{\{([a-z0-9_]+)\}\}")


def skill_dir(name: str) -> Path:
    if name not in SKILL_NAMES:
        raise KeyError(name)
    return ROOT / "skills" / name


def load_example(name: str) -> dict:
    path = skill_dir(name) / "assets" / "example-input.json"
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{name}: example-input.json must be an object")
    return data


def load_template(name: str) -> str:
    path = skill_dir(name) / "assets" / "template.md"
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        raise ValueError(f"{name}: template.md must end with a newline")
    return text


def as_bullets(items: list[str]) -> str:
    if not items:
        return NOT_PROVIDED
    return "\n".join(f"- {item}" for item in items)


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    def cell(value: str) -> str:
        cleaned = value.replace("\r", " ").replace("\n", " ").replace("|", "\\|")
        if not cleaned.strip():
            raise ValueError("table cell is empty")
        return cleaned

    if not rows:
        return NOT_PROVIDED
    head = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = [
        "| " + " | ".join(cell(column) for column in row) + " |"
        for row in rows
    ]
    return "\n".join([head, separator, *body])


def fill(template: str, fields: dict[str, str]) -> str:
    found = _PLACEHOLDER.findall(template)
    if len(found) != len(set(found)):
        raise ValueError("template has a repeated placeholder")
    if set(found) != set(fields):
        missing = sorted(set(found) - set(fields))
        unused = sorted(set(fields) - set(found))
        raise ValueError(f"placeholder mismatch missing={missing} unused={unused}")
    rendered = _PLACEHOLDER.sub(lambda match: fields[match.group(1)], template)
    if "{{" in rendered or "}}" in rendered:
        raise ValueError("unresolved placeholder braces")
    return rendered


def render_skill(name: str, data: dict) -> str:
    builders = {
        "weekly-update": _weekly_fields,
        "incident-postmortem": _incident_fields,
        "one-on-one": _one_on_one_fields,
        "release-checklist": _release_fields,
    }
    try:
        fields = builders[name](data)
    except KeyError as exc:
        raise ValueError(f"{name}: missing field {exc}") from exc
    return fill(load_template(name), fields)


def _weekly_fields(data: dict) -> dict[str, str]:
    schema = SCHEMAS["weekly-update"]
    fields = {key: data[key] for key in schema.strings}
    fields.update({key: as_bullets(data[key]) for key in schema.lists})
    return fields


def _incident_fields(data: dict) -> dict[str, str]:
    schema = SCHEMAS["incident-postmortem"]
    fields = {key: data[key] for key in schema.strings}
    fields.update({key: as_bullets(data[key]) for key in schema.lists})
    fields["timeline"] = markdown_table(
        ["Time", "Event"],
        [[row["time"], row["event"]] for row in data["timeline"]],
    )
    fields["contributing_factors"] = markdown_table(
        ["Confidence", "Statement"],
        [[row["confidence"], row["statement"]] for row in data["contributing_factors"]],
    )
    fields["action_items"] = markdown_table(
        ["Action", "Owner", "Due", "Status"],
        [
            [row["action"], row["owner"], row["due"], row["status"]]
            for row in data["action_items"]
        ],
    )
    return fields


def _one_on_one_fields(data: dict) -> dict[str, str]:
    schema = SCHEMAS["one-on-one"]
    fields = {key: data[key] for key in schema.strings}
    fields.update({key: as_bullets(data[key]) for key in schema.lists})
    blocks = []
    for item in data["feedback"]:
        blocks.append(
            "\n".join(
                [
                    f"- Direction: {item['direction']}",
                    f"  - Situation: {item['situation']}",
                    f"  - Behavior: {item['behavior']}",
                    f"  - Impact: {item['impact']}",
                ]
            )
        )
    fields["feedback"] = "\n".join(blocks) if blocks else NOT_PROVIDED
    fields["shared_commitments"] = (
        "\n".join(
            f"- {item['owner']}: {item['action']} When: {item['when']}."
            for item in data["shared_commitments"]
        )
        or NOT_PROVIDED
    )
    return fields


def _release_fields(data: dict) -> dict[str, str]:
    schema = SCHEMAS["release-checklist"]
    fields = {key: data[key] for key in schema.strings}
    fields.update({key: as_bullets(data[key]) for key in schema.lists})
    risk = data["accepted_risk"].strip() or EMPTY_ACCEPTED_RISK
    fields["accepted_risk"] = risk
    fields["checks"] = markdown_table(
        ["Check", "Status", "Evidence", "Owner"],
        [
            [row["name"], row["status"], row["evidence"], row["owner"]]
            for row in data["checks"]
        ],
    )
    return fields
