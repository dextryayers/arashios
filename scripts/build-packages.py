#!/usr/bin/env python3
"""Build the ArashiOS Debian package set deterministically.

The builder reads packages/packages.yaml, stages every payload, writes the
Debian control, copyright, and changelog files, and produces one .deb per
package. Timestamps come from SOURCE_DATE_EPOCH so repeated builds produce
identical files.

Usage:
  scripts/build-packages.py --list
  scripts/build-packages.py --package arashios-theme-gtk
  scripts/build-packages.py --all
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
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
SPEC = ROOT / "packages" / "packages.yaml"
STAGE_ROOT = ROOT / "build" / "package-staging"
OUTPUT_DIR = ROOT / "build" / "packages"
VERSION_FILE = ROOT / "versions.env"


def read_versions() -> dict:
    values: dict[str, str] = {}
    for line in VERSION_FILE.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"')
    return values


def package_version(versions: dict) -> str:
    number = versions.get("ARASHIOS_VERSION", "V1.0.0").lstrip("V")
    override = os.environ.get("ARASHIOS_PACKAGE_VERSION")
    return override or f"{number}-1"


def epoch() -> int:
    raw = os.environ.get("SOURCE_DATE_EPOCH", "")
    if raw.isdigit():
        return int(raw)
    return int(time.time())


def log(message: str) -> None:
    print(f"[packages] {message}", file=sys.stderr)


def copy_payload(root: Path, entry: dict, stage: Path, warn_missing: bool) -> list[str]:
    source = root / entry["from"]
    destination = stage / entry["to"]
    strip = int(entry.get("strip", 0))
    written: list[str] = []
    if not source.exists():
        if entry.get("optional"):
            return written
        raise SystemExit(f"ERROR: sumber payload tidak ditemukan: {entry['from']}")
    if source.is_dir():
        paths = [path for path in sorted(source.rglob("*")) if path.is_file()]
    else:
        paths = [source]
    for path in paths:
        if path.is_dir():
            continue
        if source.is_dir():
            relative = path.relative_to(source)
            parts = relative.parts[strip:] if strip else relative.parts
            if not parts:
                continue
            target = destination.joinpath(*parts)
        else:
            target = destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        written.append(str(target.relative_to(stage)))
    return written


def list_dependencies(root: Path, spec: dict) -> list[str]:
    """Read package names from the audited package lists."""
    names: list[str] = []
    for relative in spec.get("depends_from_lists", []):
        path = root / relative
        if not path.is_file():
            raise SystemExit(f"ERROR: daftar paket tidak ditemukan: {relative}")
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            for name in line.split():
                if name not in names:
                    names.append(name)
    return names


def render_control(spec: dict, common: dict, version: str, installed_size: int) -> str:
    name = spec["name"]
    lines = [
        f"Package: {name}",
        f"Version: {version}",
        f"Section: {spec.get('section', common.get('section', 'misc'))}",
        f"Priority: {spec.get('priority', common.get('priority', 'optional'))}",
        f"Architecture: {spec.get('architecture', common.get('architecture', 'all'))}",
        f"Maintainer: {common.get('maintainer', 'ArashiOS Project <maintainers@arashios.example>')}",
        f"Installed-Size: {installed_size}",
    ]
    homepage = spec.get("homepage", common.get("homepage", ""))
    if homepage:
        lines.append(f"Homepage: {homepage}")
    bugs = spec.get("bugs", common.get("bugs", ""))
    if bugs:
        lines.append(f"Bugs: {bugs}")
    depends = list(spec.get("depends", common.get("depends", [])))
    for name in list_dependencies(ROOT, spec):
        if name not in depends:
            depends.append(name)
    if depends:
        lines.append(f"Depends: {', '.join(depends)}")
    recommends = spec.get("recommends", common.get("recommends", []))
    if recommends:
        lines.append(f"Recommends: {', '.join(recommends)}")
    conflicts = spec.get("conflicts", common.get("conflicts", []))
    if conflicts:
        lines.append(f"Conflicts: {', '.join(conflicts)}")
    breaks = spec.get("breaks", common.get("breaks", []))
    if breaks:
        lines.append(f"Breaks: {', '.join(breaks)}")
    provides = spec.get("provides", common.get("provides", []))
    if provides:
        lines.append(f"Provides: {', '.join(provides)}")
    lines.append(f"Description: {spec['description']}")
    for line in spec.get("long_description", "").rstrip().splitlines():
        lines.append(f" {line}" if line.strip() else " .")
    return "\n".join(lines) + "\n"


def render_copyright(spec: dict, common: dict) -> str:
    license_id = spec.get("license", common.get("license", "GPL-3.0-or-later"))
    return f"""Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: arashios-{spec['name'].removeprefix('arashios-')}
Source: https://arashios.example

Files: *
Copyright: 2026 ArashiOS contributors
License: {license_id}

License: {license_id}
 This program is free software: you can redistribute it and modify it under
 the terms of the GNU General Public License as published by the Free
 Software Foundation, either version 3 of the License, or (at your option)
 any later version.
 .
 On Debian systems the full text of the GNU General Public License version 3
 can be found in the file /usr/share/common-licenses/GPL-3.
"""


def render_changelog(spec: dict, version: str) -> str:
    upstream = f"arashios-{spec['name'].removeprefix('arashios-')}"
    return f"""{upstream} ({version}) arashios; urgency=medium

  * Release {version} of the ArashiOS package set.

 -- ArashiOS Project <maintainers@arashios.example>  Thu, 22 Oct 2026 00:00:00 +0000
"""


def md5sums(stage: Path) -> str:
    lines = []
    for path in sorted(stage.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(stage)
        if relative.parts and relative.parts[0] == "DEBIAN":
            continue
        digest = hashlib.md5(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    return "\n".join(lines) + "\n"


def build_package(spec: dict, common: dict, version: str, stamp: int) -> Path:
    name = spec["name"]
    stage = STAGE_ROOT / name
    if stage.exists():
        shutil.rmtree(stage)
    (stage / "DEBIAN").mkdir(parents=True)

    written: list[str] = []
    for entry in spec.get("payload", []):
        written.extend(copy_payload(ROOT, entry, stage, True))

    installed_size = 0
    for path in stage.rglob("*"):
        if path.is_file() and "DEBIAN" not in path.parts:
            installed_size += path.stat().st_size // 1024 + 1

    (stage / "DEBIAN" / "control").write_text(
        render_control(spec, common, version, max(1, installed_size)), encoding="utf-8"
    )
    (stage / "DEBIAN" / "copyright").write_text(render_copyright(spec, common), encoding="utf-8")
    (stage / "DEBIAN" / "changelog").write_text(render_changelog(spec, version), encoding="utf-8")
    (stage / "DEBIAN" / "md5sums").write_text(md5sums(stage), encoding="utf-8")

    for path in sorted(stage.rglob("*")):
        if path.is_dir():
            path.chmod(0o755)
        elif "DEBIAN" in path.parts:
            path.chmod(0o644)
        else:
            path.chmod(0o644)
    (stage / "DEBIAN").chmod(0o755)

    for path in sorted(stage.rglob("*")):
        os.utime(path, (stamp, stamp))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUTPUT_DIR / f"{name}_{version}_{spec.get('architecture', 'all')}.deb"
    if target.exists():
        target.unlink()
    result = subprocess.run(
        ["dpkg-deb", "--root-owner-group", "--build", str(stage), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"ERROR: pembangunan paket {name} gagal")
    log(f"{name}: {len(written)} berkas, {target.stat().st_size} byte")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--package", action="append", help="bangun satu paket, boleh diulang")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--print-depends", help="tampilkan daftar Depends satu paket")
    args = parser.parse_args()

    with SPEC.open(encoding="utf-8") as handle:
        spec = yaml.safe_load(handle) or {}
    common = spec.get("common", {})
    packages = spec.get("packages", [])

    if args.list:
        for item in packages:
            print(f"{item['name']}\t{item.get('description', '')}")
        return 0

    if args.print_depends:
        for item in packages:
            if item["name"] == args.print_depends:
                for dependency in item.get("depends", []):
                    print(dependency)
                return 0
        print(f"ERROR: paket tidak dikenal: {args.print_depends}", file=sys.stderr)
        return 2

    versions = read_versions()
    version = package_version(versions)
    stamp = epoch()

    selected = [item for item in packages if not item.get("external")]
    if args.package:
        wanted = set(args.package)
        selected = [
            item for item in packages if item["name"] in wanted and not item.get("external")
        ]
        missing = wanted - {item["name"] for item in packages}
        if missing:
            print(f"ERROR: paket tidak dikenal: {', '.join(sorted(missing))}", file=sys.stderr)
            return 2
    elif not args.all:
        parser.error("pilih --all, --package, atau --list")

    for item in selected:
        build_package(item, common, version, stamp)
    log(f"{len(selected)} paket dibangun dengan versi {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
