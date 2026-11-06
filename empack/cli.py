"""Command line for check, demo, and install."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from empack.contract import ROOT, SKILL_NAMES
from empack.preview import write_preview
from empack.render import load_example, render_skill
from empack.validate import format_report, validate_pack


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="empack")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("check", help="validate skills, examples, readmes, and license")

    demo = subcommands.add_parser("demo", help="validate and write the fictional preview")
    demo.add_argument(
        "--out",
        default=str(ROOT / "dist" / "demo"),
        help="directory for the preview (default: dist/demo)",
    )

    install = subcommands.add_parser("install", help="copy the four skills into a skills directory")
    install.add_argument("--dest", required=True, help="destination skills directory")
    install.add_argument(
        "--dry-run",
        action="store_true",
        help="print the copies without writing",
    )

    args = parser.parse_args(argv)
    if args.command == "check":
        return _command_check()
    if args.command == "demo":
        return _command_demo(Path(args.out))
    if args.command == "install":
        return _command_install(Path(args.dest), dry_run=args.dry_run)
    parser.error(f"unknown command {args.command}")
    return 2


def _command_check() -> int:
    errors = validate_pack()
    sys.stdout.write(format_report(errors))
    return 1 if errors else 0


def _command_demo(out_dir: Path) -> int:
    errors = validate_pack()
    report = format_report(errors)
    sys.stdout.write(report)
    if errors:
        return 1
    documents = [
        (name, render_skill(name, load_example(name)))
        for name in SKILL_NAMES
    ]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    index = write_preview(out_dir, report, documents, generated_at)
    sys.stdout.write(f"wrote {index}\n")
    for name, _markdown in documents:
        sys.stdout.write(f"wrote {out_dir / (name + '.md')}\n")
    return 0


def _command_install(dest: Path, dry_run: bool) -> int:
    try:
        destination = _guard_dest(dest)
    except ValueError as exc:
        sys.stdout.write(f"empack install failed\n- {exc}\n")
        return 1
    verb = "dry-run install" if dry_run else "installed"
    if not dry_run:
        destination.mkdir(parents=True, exist_ok=True)
    for name in SKILL_NAMES:
        source = ROOT / "skills" / name
        target = destination / name
        if not dry_run:
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
        sys.stdout.write(f"{verb} {name} -> {target}\n")
    return 0


def _guard_dest(dest: Path) -> Path:
    resolved = dest.expanduser().resolve()
    blocked = [ROOT / "skills", ROOT / "empack", ROOT / "tests"]
    for path in blocked:
        if resolved == path or path in resolved.parents:
            raise ValueError(f"destination must be outside {path}")
    if resolved.exists() and not resolved.is_dir():
        raise ValueError("destination must be a directory")
    return resolved
