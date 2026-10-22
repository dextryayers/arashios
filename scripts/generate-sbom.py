#!/usr/bin/env python3
"""Generate a CycloneDX SBOM for an ArashiOS release.

The SBOM lists every Debian package selected by the release configuration and
every ArashiOS package built from this tree. Package versions come from the
Debian bookworm index when it is available locally, otherwise the component
is recorded without a version and marked as such.

Usage:
  scripts/generate-sbom.py --output out/ArashiOS-amd64-V1.10.21.sbom.json
  scripts/generate-sbom.py --index-dir /path/to/indexes --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = ROOT / "build" / "packages"
COMPONENTS = ("main", "contrib", "non-free", "non-free-firmware")
ARCHES = ("amd64", "arm64", "i386")
NAMESPACE = "pkg:deb/debian"


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def list_packages(path: Path) -> list[str]:
    packages: list[str] = []
    for line in read(path).splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        packages.extend(line.split())
    return packages


def index_versions(index_dir: Path, arch: str) -> dict[str, str]:
    versions: dict[str, str] = {}
    for component in COMPONENTS:
        path = index_dir / arch / f"bookworm-{component}.xz"
        if not path.is_file():
            continue
        with lzma.open(path, "rt", encoding="utf-8", errors="replace") as handle:
            name = ""
            version = ""
            for line in handle:
                if line.startswith("Package: "):
                    if name and version:
                        versions.setdefault(name, version)
                    name = line[9:].strip()
                    version = ""
                elif line.startswith("Version: "):
                    version = line[9:].strip()
                elif not line.strip():
                    if name and version:
                        versions.setdefault(name, version)
                    name = ""
                    version = ""
            if name and version:
                versions.setdefault(name, version)
    return versions


def purl(name: str, version: str, arch: str) -> str:
    return f"{NAMESPACE}/{name}@{version}?arch={arch}" if version else f"{NAMESPACE}/{name}?arch={arch}"


def build_sbom(arch: str, index_dir: Path | None) -> dict:
    versions = index_versions(index_dir, arch) if index_dir else {}
    components: list[dict] = []
    seen: set[str] = set()

    for path in sorted((ROOT / "config").rglob("*.list.chroot")):
        if "archives" in path.parts:
            continue
        for name in list_packages(path):
            if name in seen:
                continue
            seen.add(name)
            version = versions.get(name, "")
            entry = {
                "type": "library",
                "bom-ref": f"deb:{name}@{version or 'unknown'}",
                "name": name,
                "purl": purl(name, version, arch),
                "scope": "required",
                "properties": [
                    {"name": "arashios:source", "value": "debian-bookworm"},
                    {"name": "arashios:list", "value": str(path.relative_to(ROOT))},
                ],
            }
            if version:
                entry["version"] = version
            else:
                entry["properties"].append(
                    {"name": "arashios:version", "value": "unresolved"}
                )
            components.append(entry)

    for deb in sorted(PACKAGE_DIR.glob("arashios-*.deb")):
        name = deb.name.split("_")[0]
        version = deb.name.split("_")[1] if "_" in deb.name else ""
        digest = hashlib.sha256(deb.read_bytes()).hexdigest()
        components.append(
            {
                "type": "application",
                "bom-ref": f"deb:{name}@{version}",
                "name": name,
                "version": version,
                "purl": f"pkg:deb/arashios/{name}@{version}?arch=all",
                "scope": "required",
                "hashes": [{"alg": "SHA-256", "content": digest}],
                "licenses": [{"license": {"id": "GPL-3.0-or-later"}}],
                "properties": [
                    {"name": "arashios:source", "value": "arashios-repository"},
                ],
            }
        )

    components.sort(key=lambda item: (item["type"], item["name"]))
    document = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {
            "timestamp": "1970-01-01T00:00:00Z",
            "tools": [{"vendor": "ArashiOS Project", "name": "generate-sbom.py"}],
            "component": {
                "type": "operating-system",
                "name": "ArashiOS",
                "version": read(ROOT / "versions.env").split('ARASHIOS_VERSION="')[1].split('"')[0],
                "purl": "pkg:generic/arashios",
            },
        },
        "components": components,
    }
    serial_source = json.dumps(components, sort_keys=True).encode("utf-8")
    document["serialNumber"] = f"urn:uuid:{uuid.UUID(bytes=hashlib.sha256(serial_source).digest()[:16])}"
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="tulis SBOM ke berkas")
    parser.add_argument("--index-dir", help="direktori indeks Packages.xz Debian")
    parser.add_argument("--arch", default="amd64")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    index_dir = Path(args.index_dir) if args.index_dir else None
    document = build_sbom(args.arch, index_dir)
    content = json.dumps(document, indent=2, sort_keys=True) + "\n"

    if args.check:
        if not args.output:
            print("ERROR: --check memerlukan --output.", file=sys.stderr)
            return 2
        path = Path(args.output)
        if not path.is_file():
            print(f"ERROR: SBOM belum ada: {path}", file=sys.stderr)
            return 1
        if path.read_text(encoding="utf-8") != content:
            print("ERROR: SBOM kedaluwarsa.", file=sys.stderr)
            return 1
        print("OK: SBOM sinkron.")
        return 0

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"SBOM ditulis ke {path} dengan {len(document['components'])} komponen")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
