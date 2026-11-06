"""A small YAML subset reader for SKILL.md frontmatter.

The subset is what this pack writes: top-level scalars and one level of
nested string maps. It does not try to be a general YAML parser.
"""

from __future__ import annotations


class FrontmatterError(ValueError):
    """The SKILL.md frontmatter is missing or outside the supported subset."""


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise FrontmatterError("frontmatter must start with ---")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise FrontmatterError("frontmatter must end with ---")
    raw = text[4:end]
    body = text[end + 5 :]
    return _parse_mapping(raw), body


def parse_scalar(raw: str) -> str:
    if raw.startswith(("'", '"')):
        if len(raw) < 2 or raw[-1] != raw[0]:
            raise FrontmatterError(f"unclosed quote: {raw}")
        inner = raw[1:-1]
        if raw[0] in inner:
            raise FrontmatterError(f"quotes inside a scalar are not supported: {raw}")
        return inner
    if raw.startswith((">", "|", "[", "{", "&", "*", "!")):
        raise FrontmatterError(f"unsupported scalar syntax: {raw}")
    return raw


def _parse_mapping(raw: str) -> dict:
    result: dict = {}
    lines = raw.split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.strip() == "" or line.lstrip().startswith("#"):
            if line.startswith((" ", "\t")) and line.strip():
                raise FrontmatterError(f"unexpected indent: {line}")
            index += 1
            continue
        if line.startswith("\t") or line.startswith(" "):
            raise FrontmatterError(f"unexpected indent: {line}")
        key, value, index = _read_entry(lines, index)
        if key in result:
            raise FrontmatterError(f"duplicate key: {key}")
        result[key] = value
    return result


def _read_entry(lines: list[str], index: int) -> tuple[str, object, int]:
    line = lines[index]
    if ":" not in line:
        raise FrontmatterError(f"expected key: value, got {line}")
    key, rest = line.split(":", 1)
    key = key.strip()
    if not key or " " in key or "\t" in key:
        raise FrontmatterError(f"invalid key: {key!r}")
    rest = rest.strip()
    if rest != "":
        return key, parse_scalar(rest), index + 1
    nested: dict[str, str] = {}
    index += 1
    while index < len(lines):
        current = lines[index]
        if current.strip() == "":
            break
        if not current.startswith("  ") or current.startswith("   "):
            break
        if "\t" in current:
            raise FrontmatterError("tabs are not allowed in frontmatter")
        inner = current[2:]
        if ":" not in inner:
            raise FrontmatterError(f"expected nested key: value, got {current}")
        nested_key, nested_value = inner.split(":", 1)
        nested_key = nested_key.strip()
        if not nested_key or nested_key in nested:
            raise FrontmatterError(f"invalid nested key: {nested_key}")
        nested[nested_key] = parse_scalar(nested_value.strip())
        index += 1
    if not nested:
        raise FrontmatterError(f"empty nested map: {key}")
    return key, nested, index
