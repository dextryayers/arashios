#!/usr/bin/env python3
"""Validate an ArashiOS CycloneDX SBOM.

The validator checks the document format, the component list, the serial
number, and the presence of the ArashiOS packages so a truncated or empty
SBOM cannot pass a release gate.

Usage:
  scripts/check-sbom.py out/ArashiOS-amd64-V1.10.21.sbom.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MIN_COMPONENTS = 100
REQUIRED_PROPERTIES = ("arashios:source",)


def main() -> int:
    if len(sys.argv) != 2:
        print("ERROR:pemakaian: check-sbom.py <berkas>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: SBOM tidak ditemukan: {path}", file=sys.stderr)
        return 1
    try:
        with path.open(encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: SBOM tidak dapat dibaca: {error}", file=sys.stderr)
        return 1

    errors: list[str] = []
    if document.get("bomFormat") != "CycloneDX":
        errors.append("bomFormat harus CycloneDX")
    if not str(document.get("specVersion", "")).startswith("1."):
        errors.append("specVersion harus 1.x")
    components = document.get("components", [])
    if len(components) < MIN_COMPONENTS:
        errors.append(f"komponen terlalu sedikit: {len(components)}")
    if not str(document.get("serialNumber", "")).startswith("urn:uuid:"):
        errors.append("serialNumber harus berformat urn:uuid")
    if "metadata" not in document:
        errors.append("metadata tidak ada")

    names = {component.get("name", "") for component in components}
    if not any(name.startswith("arashios-") for name in names):
        errors.append("SBOM tidak memuat paket ArashiOS")
    for component in components:
        properties = {item.get("name") for item in component.get("properties", [])}
        if not properties & set(REQUIRED_PROPERTIES):
            errors.append(f"komponen {component.get('name')} tanpa properti sumber")
            break

    if errors:
        for error in errors:
            print(f"FAIL  {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(components)} komponen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
