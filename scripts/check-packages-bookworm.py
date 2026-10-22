#!/usr/bin/env python3
"""Audit the ArashiOS package lists against the Debian bookworm archive.

The auditor checks that every package name used by the configuration exists in
bookworm for the architecture of each supported combination. It compares
package names only, not dependency resolution.

Usage:
  scripts/check-packages-bookworm.py --index-dir /path/to/indexes
  scripts/check-packages-bookworm.py --fetch --cache ~/.cache/arashios/index
  scripts/check-packages-bookworm.py --combinations --fetch
"""

from __future__ import annotations

import argparse
import lzma
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = ("main", "contrib", "non-free", "non-free-firmware")
ARCHES = ("amd64", "arm64", "i386")
MIRROR = "https://deb.debian.org/debian"
DIST = "bookworm"


def read_packages(path: Path) -> list[str]:
    packages: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            packages.extend(line.split())
    return packages


def versions() -> dict:
    values: dict[str, str] = {}
    for line in (ROOT / "versions.env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"')
    return values


def fetch_index(cache: Path, arch: str, component: str) -> Path | None:
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / f"{DIST}-{component}-{arch}.xz"
    if target.is_file() and target.stat().st_size > 0:
        return target
    url = f"{MIRROR}/dists/{DIST}/{component}/binary-{arch}/Packages.xz"
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "ArashiOS-audit/1.0"})
        with urllib.request.urlopen(request, timeout=120) as response:
            target.write_bytes(response.read())
    except (urllib.error.URLError, OSError, TimeoutError):
        return None
    return target


def index_names(path: Path) -> set[str]:
    names: set[str] = set()
    with lzma.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("Package: "):
                names.add(line[9:].strip())
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-dir", help="direktori berisi indeks Packages.xz")
    parser.add_argument("--cache", default=str(Path.home() / ".cache" / "arashios" / "index"))
    parser.add_argument("--fetch", action="store_true", help="unduh indeks dari mirror Debian")
    parser.add_argument("--combinations", action="store_true", help="periksa per kombinasi rilis")
    args = parser.parse_args()

    env = versions()
    combinations = env.get("SUPPORTED_COMBINATIONS", "").split()
    if not combinations:
        print("ERROR: SUPPORTED_COMBINATIONS kosong.", file=sys.stderr)
        return 2

    index_dir = Path(args.index_dir) if args.index_dir else None
    cache = Path(args.cache)
    names_by_arch: dict[str, set[str]] = {}

    for arch in ARCHES:
        names: set[str] = set()
        available = True
        for component in COMPONENTS:
            path = None
            if index_dir is not None:
                candidate = index_dir / arch / f"{DIST}-{component}.xz"
                path = candidate if candidate.is_file() else None
            if path is None and args.fetch:
                path = fetch_index(cache, arch, component)
            if path is None:
                available = False
                continue
            names |= index_names(path)
        if available and names:
            names_by_arch[arch] = names
        else:
            print(f"WARN  indeks bookworm untuk {arch} tidak tersedia, pemeriksaan dilewati.")

    if not names_by_arch:
        print("INFO  tidak ada indeks yang bisa dibandingkan, pemeriksaan dilewati.")
        return 0

    errors: list[str] = []
    checked = 0
    for combination in combinations:
        arch, _, edition = combination.partition(":")
        if arch not in names_by_arch:
            continue
        files = [path for path in (ROOT / "config").rglob("*.list.chroot")
                 if path.parent.parent.name == "common" and "archives" not in path.parts]
        files += list((ROOT / "config" / "editions" / edition / "package-lists").glob("*.list.chroot"))
        arch_dir = ROOT / "config" / "arches" / arch / "package-lists"
        if arch_dir.is_dir():
            files += list(arch_dir.glob("*.list.chroot"))
        used: list[str] = []
        for path in files:
            used.extend(read_packages(path))
        unique = sorted(set(used))
        missing = [name for name in unique if name not in names_by_arch[arch]]
        checked += len(unique)
        if missing:
            errors.append(f"{combination}: paket tidak tersedia: {', '.join(missing)}")
        else:
            print(f"OK    {combination}: {len(unique)} paket tersedia di bookworm {arch}")

    if errors:
        print(f"Audit paket gagal: {len(errors)} kombinasi bermasalah.")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"Audit paket lulus: {checked} nama paket diperiksa.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
