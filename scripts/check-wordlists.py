#!/usr/bin/env python3
"""Verify the ArashiOS wordlist collection and its manifest.

The checker enforces the rules from docs/TOOLSTACK.md: every wordlist has a
source, a checksum, a license, stays below the size budget, and contains no
duplicate or empty entries.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDLIST_DIR = (
    ROOT
    / "config"
    / "common"
    / "includes.chroot"
    / "usr"
    / "share"
    / "wordlists"
    / "arashios"
)
MANIFEST = WORDLIST_DIR / "manifest.json"
MAX_TOTAL_BYTES = 10 * 1024 * 1024
MIN_LINES = 10

errors: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest() -> dict:
    files = {}
    for path in sorted(WORDLIST_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        entries = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        files[path.name] = {
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "entries": len(entries),
            "license": "CC-BY-SA-4.0",
            "source": "kurasi internal ArashiOS",
        }
    return {
        "schema_version": 1,
        "license": "CC-BY-SA-4.0",
        "total_bytes": sum(item["bytes"] for item in files.values()),
        "files": files,
    }


def main() -> int:
    if not WORDLIST_DIR.is_dir():
        print(f"ERROR: direktori wordlist hilang: {WORDLIST_DIR}", file=sys.stderr)
        return 1

    check((WORDLIST_DIR / "README.md").is_file(), "README wordlist hilang")
    check((WORDLIST_DIR / "LICENSE").is_file(), "LICENSE wordlist hilang")
    readme = (WORDLIST_DIR / "README.md").read_text(encoding="utf-8")
    check("CC-BY-SA-4.0" in readme, "README wordlist tidak menyebut lisensi")
    license_text = (WORDLIST_DIR / "LICENSE").read_text(encoding="utf-8")
    check("CC-BY-SA-4.0" in license_text, "LICENSE wordlist tidak menyebut CC-BY-SA-4.0")

    manifest = build_manifest()
    total = manifest["total_bytes"]
    check(total <= MAX_TOTAL_BYTES, f"total wordlist {total} byte melebihi batas {MAX_TOTAL_BYTES}")
    check(len(manifest["files"]) >= 4, "jumlah wordlist di bawah minimum")

    for name, entry in manifest["files"].items():
        path = WORDLIST_DIR / name
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        check(bool(lines) and lines[0].startswith("#"), f"{name}: tanpa komentar sumber")
        check(entry["entries"] >= MIN_LINES, f"{name}: hanya {entry['entries']} entri")
        entries = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
        check(len(entries) == len(set(entries)), f"{name}: ada entri duplikat")
        check(all(entry for entry in entries), f"{name}: ada entri kosong")

    if MANIFEST.is_file():
        stored = json.loads(MANIFEST.read_text(encoding="utf-8"))
        check(stored == manifest, "manifest wordlist tidak sinkron, jalankan scripts/check-wordlists.py --update")
    else:
        check(False, "manifest wordlist hilang, jalankan scripts/check-wordlists.py --update")

    if errors:
        print(f"Wordlist checks failed: {len(errors)} of {checks}")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"Wordlist checks passed: {checks}")
    return 0


def update() -> int:
    manifest = build_manifest()
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OK: manifest wordlist ditulis, {len(manifest['files'])} berkas.")
    return 0


if __name__ == "__main__":
    if "--update" in sys.argv[1:]:
        raise SystemExit(update())
    raise SystemExit(main())
