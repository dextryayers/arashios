#!/usr/bin/env python3
"""Write the ArashiOS release snapshot manifest.

The manifest records the version, the package set with checksums, the
repository key fingerprint, and the hash of the tracked configuration. It is
the anchor for the upgrade path and for reproducible rebuilds.

Usage:
  scripts/snapshot-manifest.py --output repo/manifest.json
  scripts/snapshot-manifest.py --check --output repo/manifest.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = ROOT / "build" / "packages"
KEY_DIR = ROOT / "repo" / "keys"
TRACKED = ("config", "branding", "packages", "tools", "toolchains", "scripts", "docs")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def config_hash() -> str:
    digest = hashlib.sha256()
    for name in TRACKED:
        base = ROOT / name
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.name == "__pycache__":
                continue
            digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def versions() -> dict:
    values: dict[str, str] = {}
    for line in (ROOT / "versions.env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"')
    return values


def build_manifest() -> dict:
    env = versions()
    packages = []
    for deb in sorted(PACKAGE_DIR.glob("*.deb")):
        packages.append(
            {
                "name": deb.name.split("_")[0],
                "file": deb.name,
                "bytes": deb.stat().st_size,
                "sha256": sha256_file(deb),
            }
        )
    fingerprint_file = KEY_DIR / "arashios-archive.fingerprint"
    fingerprint = fingerprint_file.read_text(encoding="utf-8").strip() if fingerprint_file.is_file() else ""
    return {
        "schema_version": 1,
        "version": env.get("ARASHIOS_VERSION", ""),
        "codename": env.get("ARASHIOS_CODENAME", ""),
        "repo_suite": env.get("REPO_SUITE", "stable"),
        "repo_uri": env.get("REPO_URI", ""),
        "repo_key_fingerprint": fingerprint,
        "config_hash": config_hash(),
        "package_count": len(packages),
        "packages": packages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="repo/manifest.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    output = ROOT / args.output
    manifest = build_manifest()
    content = json.dumps(manifest, indent=2, sort_keys=True) + "\n"

    if args.check:
        if not output.is_file():
            print(f"ERROR: manifest belum ada: {output}", file=sys.stderr)
            return 1
        current = output.read_text(encoding="utf-8")
        if current != content:
            print("ERROR: manifest snapshot kedaluwarsa.", file=sys.stderr)
            return 1
        print("OK: manifest snapshot sinkron.")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(
        f"OK: {manifest['package_count']} paket, config {manifest['config_hash'][:12]}, "
        f"ditulis ke {output.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
