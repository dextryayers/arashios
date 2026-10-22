#!/usr/bin/env python3
"""Refresh the pinned upstream refs for ArashiOS tier 1 tools.

The script resolves the current release tag of every pinned repository with
git ls-remote, compares it with the recorded pin, and writes the updated pin
file. The result must be reviewed and validated before it is committed.

Usage:
  scripts/refresh-source-pins.py --check
  scripts/refresh-source-pins.py --update [--tool NAME]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML tidak tersedia. Pasang paket python3-yaml.", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
PINS = ROOT / "tools" / "source-pins.yaml"
VERSION_RE = re.compile(r"^[A-Za-z]*v?\d")


def version_key(tag: str) -> list:
    parts = re.split(r"[._-]", tag.lstrip("vV"))
    key = []
    for part in parts:
        key.append((0, int(part)) if part.isdigit() else (1, part))
    return key


def list_tags(url: str, attempts: int = 4) -> list[tuple[str, str]]:
    for attempt in range(attempts):
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--tags", "--refs", url],
                capture_output=True,
                text=True,
                check=False,
                timeout=90,
            )
        except (OSError, subprocess.TimeoutExpired):
            time.sleep(3)
            continue
        if result.returncode != 0:
            time.sleep(3)
            continue
        tags = []
        for line in result.stdout.splitlines():
            sha, _, ref = line.partition("\t")
            tag = ref.removeprefix("refs/tags/")
            if not VERSION_RE.match(tag):
                continue
            tags.append((tag, sha))
        return tags
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="hanya laporkan selisih pin")
    parser.add_argument("--update", action="store_true", help="tulis pin baru ke source-pins.yaml")
    parser.add_argument("--tool", help="hanya periksa satu tool")
    args = parser.parse_args()

    with PINS.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    sources = data.get("sources", {})
    if not sources:
        print("ERROR: source-pins.yaml tidak memuat sources.", file=sys.stderr)
        return 1

    changed = 0
    checked = 0
    unreachable = 0
    for name, pin in sorted(sources.items()):
        if args.tool and name != args.tool:
            continue
        url = pin.get("url", "")
        if not url:
            continue
        tags = list_tags(url)
        if not tags:
            unreachable += 1
            print(f"WARN  {name}: upstream tidak dapat dihubungi, pin dipertahankan")
            continue
        tags.sort(key=lambda item: version_key(item[0]))
        tag, commit = tags[-1]
        checked += 1
        if tag == pin.get("ref") and commit == pin.get("commit"):
            print(f"OK    {name}: {tag} tetap terkunci")
            continue
        changed += 1
        print(f"UPD   {name}: {pin.get('ref')} -> {tag}")
        if args.update:
            pin["ref"] = tag
            pin["commit"] = commit

    if args.update and changed:
        data["updated"] = time.strftime("%Y-%m-%d")
        PINS.write_text(
            yaml.safe_dump(data, sort_keys=True, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
        print(f"OK: {changed} pin diperbarui di {PINS.relative_to(ROOT)}")
    else:
        print(f"{checked} pin diperiksa, {changed} berubah, {unreachable} tidak dapat dihubungi.")
    if args.check and changed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
