"""Validate the skill pack against the Agent Skills subset this repo uses."""

from __future__ import annotations

import re
from pathlib import Path

from empack.contract import (
    ACTION_STATUS,
    ALLOWED_URLS,
    CHECK_STATUS,
    CLONE_URL,
    CONFIDENCE,
    DECISION,
    DISCLAIMER,
    FEEDBACK_DIRECTION,
    INCIDENT_STATUS,
    LANGUAGE_SWITCH,
    MAX_COMPATIBILITY,
    MAX_DESCRIPTION,
    MAX_SKILL_LINES,
    NOT_PROVIDED,
    ORG_NAME,
    README_FILES,
    REQUIRED_SKILL_SECTIONS,
    ROOT,
    SCHEMAS,
    SKILL_NAMES,
    TEMPLATE_HEADINGS,
)
from empack.frontmatter import FrontmatterError, parse_frontmatter
from empack.render import load_example, load_template, render_skill

_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_URL = re.compile(r"""https?://[^\s)`>"']+""")
_SECRET = re.compile(
    r"(AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+)",
)
_DENY = re.compile(
    r"\b(Google|Microsoft|Amazon|Meta|Facebook|Apple|Netflix|Uber|Stripe|OpenAI"
    r"|Anthropic|ByteDance|Tencent|Alibaba|Huawei|Slack|GitHub|GitLab|Atlassian"
    r"|Jira|Notion|Gumroad|Acme|Contoso)\b",
    re.IGNORECASE,
)
_HEADING = re.compile(r"^#{1,3} .+")
_STEP = re.compile(r"^([0-9]+)\. ")


def validate_name(name: str) -> str | None:
    if not isinstance(name, str) or not (1 <= len(name) <= 64):
        return "name must be 1-64 characters"
    if not _NAME.fullmatch(name):
        return "name must be lowercase letters, numbers, and single hyphens"
    if "anthropic" in name or "claude" in name:
        return "name must not contain reserved words anthropic or claude"
    return None


def validate_pack(root: Path | None = None) -> list[str]:
    root = root or ROOT
    errors: list[str] = []
    skills_root = root / "skills"
    found = sorted(path.name for path in skills_root.iterdir() if path.is_dir()) if skills_root.is_dir() else []
    if found != sorted(SKILL_NAMES):
        errors.append(f"skills directories must be {list(SKILL_NAMES)}, found {found}")
    for name in SKILL_NAMES:
        errors.extend(_validate_skill_dir(root, name))
    errors.extend(_validate_readmes(root))
    errors.extend(_validate_license(root))
    errors.extend(_validate_urls(root))
    return errors


def validate_example(name: str, data: dict) -> list[str]:
    errors: list[str] = []
    label = name
    if not isinstance(data, dict):
        return [f"{label}: example must be an object"]
    schema = SCHEMAS[name]
    expected = {"meta", *schema.strings, *schema.lists, *schema.tables, *schema.optional_strings}
    if set(data) != expected:
        return [
            f"{label}: example keys must be {sorted(expected)}, found {sorted(data)}"
        ]
    meta = data["meta"]
    if meta != {
        "fictional": True,
        "source": "hand-written example for this repository",
    }:
        errors.append(f"{label}: meta must mark the example as hand-written and fictional")
    if data.get("disclaimer") != DISCLAIMER:
        errors.append(f"{label}: disclaimer must be the shared fictional banner")
    for key in (*schema.strings, *schema.optional_strings):
        value = data[key]
        if not isinstance(value, str):
            errors.append(f"{label}: {key} must be a string")
            continue
        if key != "accepted_risk" and not value.strip():
            errors.append(f"{label}: {key} is empty")
        errors.extend(_scan_fixture_text(f"{label}.{key}", value))
    for key in schema.lists:
        errors.extend(_validate_string_list(label, key, data[key]))
    for key, columns in schema.tables.items():
        errors.extend(_validate_table(label, key, columns, data[key]))
    if "organization" in data and data["organization"] != ORG_NAME:
        errors.append(f"{label}: organization must be {ORG_NAME}")
    if errors:
        return errors
    errors.extend(_validate_domain_rules(name, data))
    return errors


def release_decision_errors(data: dict) -> list[str]:
    gaps = [row["name"] for row in data["checks"] if row["status"] != "Ready"]
    decision = data["decision"]
    if decision not in DECISION:
        return [f"decision must be one of {sorted(DECISION)}"]
    if decision != "Go" or not gaps:
        return []
    if data.get("accepted_risk", "").strip():
        return []
    names = ", ".join(gaps)
    return [f"Go with checks that are not Ready requires accepted risk: {names}"]


def format_report(errors: list[str]) -> str:
    if errors:
        lines = ["empack check failed", *(f"- {error}" for error in errors)]
    else:
        lines = ["empack check passed", *(f"pass {name}" for name in SKILL_NAMES)]
    return "\n".join(lines) + "\n"


def _validate_skill_dir(root: Path, name: str) -> list[str]:
    errors: list[str] = []
    directory = root / "skills" / name
    skill_path = directory / "SKILL.md"
    if not skill_path.is_file():
        return [f"{name}: missing SKILL.md"]
    text = skill_path.read_text(encoding="utf-8")
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    if line_count > MAX_SKILL_LINES:
        errors.append(f"{name}: SKILL.md has {line_count} lines, limit is {MAX_SKILL_LINES}")
    try:
        frontmatter, body = parse_frontmatter(text)
    except FrontmatterError as exc:
        return [f"{name}: {exc}"]
    errors.extend(_validate_frontmatter(name, frontmatter))
    for section in REQUIRED_SKILL_SECTIONS:
        if section not in body:
            errors.append(f"{name}: missing section {section}")
    for asset in ("assets/template.md", "assets/example-input.json"):
        if asset not in text:
            errors.append(f"{name}: SKILL.md must reference {asset}")
        if not (directory / asset).is_file():
            errors.append(f"{name}: missing {asset}")
    template = load_template(name) if (directory / "assets" / "template.md").is_file() else ""
    if template:
        headings = tuple(line for line in template.splitlines() if line.startswith("#"))
        expected = TEMPLATE_HEADINGS[name]
        if headings != expected:
            errors.append(f"{name}: template headings {headings} != {expected}")
        if "Harbor" in template or "Riley" in template or "Alex" in template:
            errors.append(f"{name}: template must stay generic; example facts belong in JSON")
    try:
        example = load_example(name)
    except (OSError, ValueError) as exc:
        return [*errors, f"{name}: {exc}"]
    errors.extend(validate_example(name, example))
    if errors:
        return errors
    try:
        rendered = render_skill(name, example)
    except (OSError, ValueError) as exc:
        return [*errors, f"{name}: render failed: {exc}"]
    errors.extend(_validate_rendered(name, example, rendered))
    return errors


def _validate_frontmatter(name: str, frontmatter: dict) -> list[str]:
    errors: list[str] = []
    required = {"name", "description", "license", "compatibility", "metadata"}
    missing = required - set(frontmatter)
    if missing:
        errors.append(f"{name}: frontmatter missing {sorted(missing)}")
    skill_name = frontmatter.get("name")
    name_error = validate_name(skill_name) if isinstance(skill_name, str) else "name must be a string"
    if name_error:
        errors.append(f"{name}: {name_error}")
    elif skill_name != name:
        errors.append(f"{name}: frontmatter name {skill_name} must match the directory")
    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{name}: description must be a non-empty string")
    elif len(description) > MAX_DESCRIPTION:
        errors.append(f"{name}: description is {len(description)} characters, limit is {MAX_DESCRIPTION}")
    elif "<" in description or ">" in description:
        errors.append(f"{name}: description must not contain XML angle brackets")
    elif "Use when" not in description:
        errors.append(f"{name}: description must say when to use the skill")
    if frontmatter.get("license") != "MIT":
        errors.append(f"{name}: license must be MIT")
    compatibility = frontmatter.get("compatibility")
    if not isinstance(compatibility, str) or not (1 <= len(compatibility) <= MAX_COMPATIBILITY):
        errors.append(f"{name}: compatibility must be 1-{MAX_COMPATIBILITY} characters")
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict) or set(metadata) != {"author", "version"}:
        errors.append(f"{name}: metadata must contain author and version")
    elif any(not isinstance(value, str) or not value.strip() for value in metadata.values()):
        errors.append(f"{name}: metadata values must be non-empty strings")
    elif metadata.get("author") != "eng-manager-skills-pack":
        errors.append(f"{name}: metadata.author must be eng-manager-skills-pack")
    return errors


def _validate_string_list(label: str, key: str, value: object) -> list[str]:
    if not isinstance(value, list) or not value:
        return [f"{label}: {key} must be a non-empty list"]
    errors: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label}: {key}[{index}] must be a non-empty string")
            continue
            errors.extend(_scan_fixture_text(f"{label}.{key}[{index}]", item))
        if "Owner:" in item and "fictional" not in item.lower():
            errors.append(f"{label}: {key}[{index}] names an owner who is not marked fictional")
    return errors


def _validate_table(label: str, key: str, columns: tuple[str, ...], value: object) -> list[str]:
    if not isinstance(value, list) or not value:
        return [f"{label}: {key} must be a non-empty list"]
    errors: list[str] = []
    for index, row in enumerate(value):
        if not isinstance(row, dict) or set(row) != set(columns):
            errors.append(f"{label}: {key}[{index}] keys must be {list(columns)}")
            continue
        for column in columns:
            cell = row[column]
            if not isinstance(cell, str) or not cell.strip():
                errors.append(f"{label}: {key}[{index}].{column} must be a non-empty string")
                continue
            errors.extend(_scan_fixture_text(f"{label}.{key}[{index}].{column}", cell))
            if column in {"owner", "report", "manager", "author"} and "fictional" not in cell.lower():
                errors.append(f"{label}: {key}[{index}].{column} must mark the person as fictional")
    return errors


def _validate_domain_rules(name: str, data: dict) -> list[str]:
    errors: list[str] = []
    if name == "incident-postmortem":
        if data["status"] not in INCIDENT_STATUS:
            errors.append(f"{name}: status must be one of {sorted(INCIDENT_STATUS)}")
        for index, row in enumerate(data["contributing_factors"]):
            if row["confidence"] not in CONFIDENCE:
                errors.append(f"{name}: contributing_factors[{index}].confidence is invalid")
        for index, row in enumerate(data["action_items"]):
            if row["status"] not in ACTION_STATUS:
                errors.append(f"{name}: action_items[{index}].status is invalid")
            if "fictional" not in row["owner"].lower():
                errors.append(f"{name}: action owner must be marked fictional")
    elif name == "one-on-one":
        for field in ("report", "manager"):
            if "fictional" not in data[field].lower():
                errors.append(f"{name}: {field} must be marked fictional")
        for index, row in enumerate(data["feedback"]):
            if row["direction"] not in FEEDBACK_DIRECTION:
                errors.append(f"{name}: feedback[{index}].direction is invalid")
        for index, row in enumerate(data["shared_commitments"]):
            if "fictional" not in row["owner"].lower():
                errors.append(f"{name}: commitment owner must be marked fictional")
    elif name == "release-checklist":
        if "fictional" not in data["owner"].lower() or "fictional" not in data["watch_owner"].lower():
            errors.append(f"{name}: release owner and watch owner must be marked fictional")
        for index, row in enumerate(data["checks"]):
            if row["status"] not in CHECK_STATUS:
                errors.append(f"{name}: checks[{index}].status is invalid")
            if row["status"] == "Ready" and row["evidence"].strip() in {"", NOT_PROVIDED}:
                errors.append(f"{name}: checks[{index}] is Ready without evidence")
        errors.extend(f"{name}: {item}" for item in release_decision_errors(data))
    elif name == "weekly-update":
        if "fictional" not in data["author"].lower():
            errors.append(f"{name}: author must be marked fictional")
    return errors


def _validate_rendered(name: str, example: dict, rendered: str) -> list[str]:
    errors: list[str] = []
    first = rendered.splitlines()[0] if rendered else ""
    if first != f"> {DISCLAIMER}":
        errors.append(f"{name}: rendered document must open with the fictional banner")
    if NOT_PROVIDED in rendered:
        errors.append(f"{name}: bundled example still contains {NOT_PROVIDED}")
    if "{{" in rendered:
        errors.append(f"{name}: rendered document still has a placeholder")
    headings = tuple(line for line in rendered.splitlines() if _HEADING.match(line))
    if headings != TEMPLATE_HEADINGS[name]:
        errors.append(f"{name}: rendered headings do not match the template contract")
    for text in _content_strings(example):
        if text not in rendered:
            errors.append(f"{name}: rendered document dropped a fixture fact: {text}")
    errors.extend(_scan_public_text(f"{name} rendered", rendered))
    return errors


def _content_strings(value: object, skip_meta: bool = True) -> list[str]:
    found: list[str] = []

    def walk(node: object, key: str | None = None) -> None:
        if skip_meta and key == "meta":
            return
        if isinstance(node, str):
            if node.strip():
                found.append(node.strip() if key == "accepted_risk" else node)
        elif isinstance(node, dict):
            for child_key, child in node.items():
                walk(child, child_key)
        elif isinstance(node, list):
            for child in node:
                walk(child, key)

    walk(value)
    return found


def _scan_fixture_text(label: str, text: str) -> list[str]:
    errors = _scan_public_text(label, text)
    if "\n" in text or "\r" in text:
        errors.append(f"{label}: newlines belong in the template, not in a fixture string")
    if "{{" in text or "}}" in text:
        errors.append(f"{label}: fixture text must not contain placeholders")
    if "|" in text:
        errors.append(f"{label}: fixture text must not contain a table pipe")
    if "@" in text:
        errors.append(f"{label}: fixture text must not contain an email address")
    return errors


def _scan_public_text(label: str, text: str) -> list[str]:
    errors: list[str] = []
    if _URL.search(text):
        errors.append(f"{label}: text must not contain a URL")
    if _SECRET.search(text):
        errors.append(f"{label}: text matches a secret pattern")
    denied = _DENY.search(text)
    if denied:
        errors.append(f"{label}: text names a real or stock example company ({denied.group(0)})")
    for token in ("TODO", "FIXME", "TBD", "lorem"):
        if token.lower() in text.lower():
            errors.append(f"{label}: contains {token}")
    return errors


def _validate_readmes(root: Path) -> list[str]:
    errors: list[str] = []
    for filename in README_FILES:
        path = root / filename
        if not path.is_file():
            errors.append(f"missing {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        if text.splitlines()[0] != LANGUAGE_SWITCH:
            errors.append(f"{filename}: language switch must be the first line")
        if "<!-- quickstart:start -->" not in text or "<!-- quickstart:end -->" not in text:
            errors.append(f"{filename}: missing quickstart markers")
        else:
            errors.extend(_validate_quickstart(filename, text))
        for token in (
            "python3 -m empack demo",
            "python3 -m empack install --dest",
            "python3 -m empack check",
            f"python3 -m unittest discover -s tests -t . -v",
            "FICTIONAL EXAMPLE",
            "MIT",
            "Cursor",
            "Claude",
            *SKILL_NAMES,
            f"git clone {CLONE_URL}",
        ):
            if token not in text:
                errors.append(f"{filename}: missing {token}")
    localized = (
        ("README.md", "**Audience.**"),
        ("README.md", "**Pain.**"),
        ("README.zh-Hans.md", "受众"),
        ("README.zh-Hans.md", "痛点"),
        ("README.zh-Hant.md", "受眾"),
        ("README.zh-Hant.md", "痛點"),
        ("README.ja.md", "想定する人"),
        ("README.ja.md", "困っていること"),
    )
    for filename, token in localized:
        path = root / filename
        if path.is_file() and token not in path.read_text(encoding="utf-8"):
            errors.append(f"{filename}: missing {token}")
    return errors


def _validate_quickstart(filename: str, text: str) -> list[str]:
    start = text.index("<!-- quickstart:start -->")
    end = text.index("<!-- quickstart:end -->")
    block = text[start:end]
    numbered = [line for line in block.splitlines() if _STEP.match(line)]
    numbers = [int(_STEP.match(line).group(1)) for line in numbered]
    if numbers != [1, 2, 3]:
        return [f"{filename}: quickstart must be exactly three steps, found {numbers}"]
    return []


def _validate_license(root: Path) -> list[str]:
    path = root / "LICENSE"
    if not path.is_file():
        return ["missing LICENSE"]
    text = path.read_text(encoding="utf-8")
    if not text.startswith("MIT License\n"):
        return ["LICENSE must start with MIT License"]
    if "Permission is hereby granted, free of charge" not in text:
        return ["LICENSE is missing the MIT permission grant"]
    return []


def _validate_urls(root: Path) -> list[str]:
    errors: list[str] = []
    files = [root / "LICENSE", *list((root / "skills").rglob("*")), *list((root / "empack").rglob("*.py"))]
    files.extend(root / name for name in README_FILES)
    for path in files:
        if not path.is_file() or path.suffix not in {".md", ".py", ".json", ""}:
            continue
        if path.name == "LICENSE":
            text = path.read_text(encoding="utf-8")
        elif path.suffix in {".md", ".py", ".json"}:
            text = path.read_text(encoding="utf-8")
        else:
            continue
        for url in _URL.findall(text):
            if url not in ALLOWED_URLS:
                errors.append(f"{path.relative_to(root)}: unexpected URL {url}")
    return errors
