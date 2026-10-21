#!/usr/bin/env python3
"""Generate the runtime toolchain catalog for ArashiOS.

Sources of truth:
  toolchains/catalog.yaml  component metadata and download URLs
  toolchains/lock.yaml     pinned checksums per architecture

Output:
  config/common/includes.chroot/usr/share/arashios/toolchain/catalog.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML tidak tersedia. Pasang paket python3-yaml.", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "toolchains" / "catalog.yaml"
LOCK = ROOT / "toolchains" / "lock.yaml"
OUTPUT = (
    ROOT
    / "config"
    / "common"
    / "includes.chroot"
    / "usr"
    / "share"
    / "arashios"
    / "toolchain"
    / "catalog.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="periksa hasil generate tanpa menulis")
    args = parser.parse_args()

    with CATALOG.open(encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle) or {}
    lock: dict = {}
    if LOCK.is_file():
        with LOCK.open(encoding="utf-8") as handle:
            lock = yaml.safe_load(handle) or {}

    components = []
    for component in catalog.get("components", []):
        name = component["name"]
        entry = {
            "name": name,
            "version": str(component.get("version", "")),
            "role": component.get("role", ""),
            "kind": component.get("kind", "archive"),
            "format": component.get("format", ""),
            "license": component.get("license", ""),
            "homepage": component.get("homepage", ""),
            "summary": component.get("summary", ""),
            "binaries": list(component.get("binaries", [])),
            "manager": component.get("manager", ""),
            "targets": {},
        }
        locked = lock.get("components", {}).get(name, {}).get("targets", {})
        for arch, target in (component.get("targets") or {}).items():
            pin = locked.get(arch, {})
            entry["targets"][arch] = {
                "url": target["url"],
                "sha256": pin.get("sha256", ""),
                "origin": pin.get("origin", ""),
            }
        components.append(entry)

    payload = {
        "schema_version": 1,
        "updated": catalog.get("updated", ""),
        "components": components,
    }
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != content:
            print("ERROR: katalog toolchain runtime kedaluwarsa.", file=sys.stderr)
            return 1
        print("OK: katalog toolchain runtime sinkron.")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"OK: {len(components)} komponen toolchain ditulis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
