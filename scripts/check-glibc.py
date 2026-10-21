#!/usr/bin/env python3
"""Check the glibc requirement of ArashiOS vendor binaries.

Debian 12 bookworm ships glibc 2.36. A binary that needs a newer symbol
version cannot run on the target system and must be moved to tier 3 or rebuilt
against an older glibc. Static binaries, including Go binaries, pass without
symbol inspection.

Usage:
  scripts/check-glibc.py <binary> [<binary> ...] [--max-glibc 2.36]
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

GLIBC_RE = re.compile(r"GLIBC_(\d+)\.(\d+)")


def version_tuple(value: str) -> tuple[int, int]:
    major, _, minor = value.partition(".")
    return int(major or 0), int(minor or 0)


def elf_info(path: Path) -> dict:
    info = {"is_elf": False, "static": False, "max_glibc": (0, 0), "symbols": []}
    data = path.read_bytes()[:64]
    if data[:4] != b"\x7fELF":
        return info
    info["is_elf"] = True
    if shutil.which("file"):
        result = subprocess.run(
            ["file", "-b", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        description = result.stdout.strip().lower()
        info["static"] = "statically linked" in description
        if "go build" in description or "go1." in description:
            info["go"] = True
    if info["static"]:
        return info
    if shutil.which("objdump"):
        result = subprocess.run(
            ["objdump", "-T", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        for match in GLIBC_RE.finditer(result.stdout):
            version = (int(match.group(1)), int(match.group(2)))
            info["symbols"].append(version)
            if version > info["max_glibc"]:
                info["max_glibc"] = version
    return info


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binaries", nargs="+")
    parser.add_argument("--max-glibc", default="2.36")
    args = parser.parse_args()

    limit = version_tuple(args.max_glibc)
    failures = 0
    for name in args.binaries:
        path = Path(name)
        if not path.is_file():
            print(f"FAIL  {name}: berkas tidak ditemukan")
            failures += 1
            continue
        info = elf_info(path)
        if not info["is_elf"]:
            print(f"SKIP  {name}: bukan berkas ELF")
            continue
        if info["static"]:
            print(f"OK    {name}: binary statik, tanpa simbol glibc")
            continue
        if info["max_glibc"] == (0, 0):
            print(f"OK    {name}: tidak memakai simbol glibc")
            continue
        found = f"{info['max_glibc'][0]}.{info['max_glibc'][1]}"
        if info["max_glibc"] > limit:
            print(
                f"FAIL  {name}: membutuhkan GLIBC_{found}, batas {args.max_glibc}. "
                "Pindahkan ke tier 3 atau bangun ulang."
            )
            failures += 1
        else:
            print(f"OK    {name}: simbol glibc tertinggi GLIBC_{found}, batas {args.max_glibc}")
    if failures:
        print(f"Audit glibc gagal: {failures} berkas.")
        return 1
    print("Audit glibc lulus.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
