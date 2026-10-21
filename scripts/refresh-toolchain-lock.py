#!/usr/bin/env python3
"""Refresh the ArashiOS toolchain lock file with upstream checksums.

For every component and architecture the script resolves the checksum of the
release artifact. Upstream checksum files are preferred. When upstream does not
publish a checksum the artifact is downloaded once and hashed locally, and the
lock records that the value was computed instead of published.

Usage:
  scripts/refresh-toolchain-lock.py --cache ~/.cache/arashios/vendor
  scripts/refresh-toolchain-lock.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML tidak tersedia. Pasang paket python3-yaml.", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "toolchains" / "catalog.yaml"
LOCK = ROOT / "toolchains" / "lock.yaml"
SHA256_RE = re.compile(r"\b([0-9a-f]{64})\b")
USER_AGENT = "ArashiOS-toolchain-lock/1.0"


def fetch(url: str, timeout: int = 120, attempts: int = 6) -> bytes:
    """Download with retries because release CDNs reset connections often."""
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, OSError, TimeoutError) as error:
            last = error
            time.sleep(3 * (attempt + 1))
    raise last if last else RuntimeError(f"gagal mengunduh {url}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checksum_from_sidecar(url: str) -> str | None:
    try:
        text = fetch(url, timeout=60).decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError, TimeoutError):
        return None
    match = SHA256_RE.search(text)
    return match.group(1) if match else None


def checksum_from_go_index(url: str, filename: str) -> str | None:
    try:
        payload = json.loads(fetch(url, timeout=120).decode("utf-8"))
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError):
        return None
    for release in payload:
        for entry in release.get("files", []):
            if entry.get("filename") == filename:
                return entry.get("sha256")
    return None


def checksum_from_download(url: str, cache: Path) -> tuple[str | None, int]:
    cache.mkdir(parents=True, exist_ok=True)
    name = url.rsplit("/", 1)[-1]
    target = cache / name
    if not target.is_file():
        try:
            data = fetch(url, timeout=900)
        except (urllib.error.URLError, OSError, TimeoutError):
            return None, 0
        target.write_bytes(data)
    else:
        data = target.read_bytes()
    return sha256_bytes(data), len(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", help="direktori cache untuk artefak yang dihitung manual")
    parser.add_argument("--check", action="store_true", help="hanya laporkan status lock")
    args = parser.parse_args()

    with CATALOG.open(encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle)

    cache = Path(args.cache) if args.cache else Path.home() / ".cache" / "arashios" / "vendor"
    previous: dict = {}
    if LOCK.is_file():
        previous = yaml.safe_load(LOCK.read_text(encoding="utf-8")) or {}
    lock = {
        "schema_version": 1,
        "updated": catalog.get("updated", ""),
        "components": {},
    }

    for component in catalog.get("components", []):
        name = component["name"]
        entry = {
            "version": str(component.get("version", "")),
            "role": component.get("role", ""),
            "kind": component.get("kind", "archive"),
            "license": component.get("license", ""),
            "targets": {},
        }
        for arch, target in (component.get("targets") or {}).items():
            url = target["url"]
            digest = None
            origin = "upstream"
            size = 0
            style = target.get("checksum_style", "")
            if style == "go-index":
                filename = url.rsplit("/", 1)[-1]
                digest = checksum_from_go_index(target["checksum_url"], filename)
            elif target.get("checksum_url"):
                digest = checksum_from_sidecar(target["checksum_url"])
            if digest is None and not args.check:
                digest, size = checksum_from_download(url, cache)
                origin = "computed"
            if digest is None:
                kept = (
                    previous.get("components", {})
                    .get(name, {})
                    .get("targets", {})
                    .get(arch, {})
                    .get("sha256")
                )
                if kept:
                    digest = kept
                    origin = "previous-lock"
            record = {"url": url, "sha256": digest or "", "origin": origin}
            if size:
                record["bytes"] = size
            entry["targets"][arch] = record
            state = digest or "TIDAK ADA"
            print(f"{name:<12} {arch:<7} {state}")
        lock["components"][name] = entry

    if args.check:
        if not LOCK.is_file():
            print("ERROR: lock toolchain belum ada.", file=sys.stderr)
            return 1
        stored = yaml.safe_load(LOCK.read_text(encoding="utf-8"))
        missing = []
        for name, entry in stored.get("components", {}).items():
            for arch, target in entry.get("targets", {}).items():
                if not target.get("sha256"):
                    missing.append(f"{name}:{arch}")
        if missing:
            print("ERROR: target tanpa checksum: " + ", ".join(missing), file=sys.stderr)
            return 1
        print("OK: lock toolchain lengkap.")
        return 0

    LOCK.write_text(
        yaml.safe_dump(lock, sort_keys=True, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"OK: lock toolchain ditulis ke {LOCK.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
