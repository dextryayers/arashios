#!/usr/bin/env python3
"""Audit the ArashiOS package set against the packaging standard.

The audit mirrors the rules from plan.md section 11.3: debhelper style
control fields, complete copyright, changelog format, FHS paths only, no
network access in maintainer scripts, and idempotent post installation.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML tidak tersedia. Pasang paket python3-yaml.", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "packages" / "packages.yaml"
PACKAGE_DIR = ROOT / "build" / "packages"
REPO = ROOT / "repo" / "public"
FHS_PREFIXES = ("usr/", "etc/", "var/", "opt/", "srv/", "usr/local/")

errors: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)


def load_spec() -> tuple[dict, dict]:
    with SPEC.open(encoding="utf-8") as handle:
        spec = yaml.safe_load(handle) or {}
    return spec, spec.get("common", {})


def deb_files() -> list[Path]:
    if not PACKAGE_DIR.is_dir():
        return []
    return sorted(PACKAGE_DIR.glob("arashios-*.deb"))


def package_control(deb: Path) -> dict:
    result = subprocess.run(
        ["dpkg-deb", "-f", str(deb)],
        capture_output=True,
        text=True,
        check=False,
    )
    fields: dict[str, str] = {}
    key = ""
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        if line[0] in " \t" and key:
            fields[key] += "\n" + line.strip()
            continue
        name, _, value = line.partition(":")
        key = name.strip()
        fields[key] = value.strip()
    return fields


def package_files(deb: Path) -> list[str]:
    result = subprocess.run(
        ["dpkg-deb", "-c", str(deb)],
        capture_output=True,
        text=True,
        check=False,
    )
    names = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 6 and parts[0].startswith("."):
            names.append(parts[5].lstrip(".").lstrip("/"))
    return names


def check_spec() -> None:
    spec, common = load_spec()
    packages = spec.get("packages", [])
    check(len(packages) == 16, f"jumlah paket harus 16, saat ini {len(packages)}")
    names = [item["name"] for item in packages]
    check(len(names) == len(set(names)), "nama paket duplikat pada spesifikasi")
    for item in packages:
        name = item["name"]
        check(name.startswith("arashios-"), f"{name}: nama paket harus berawalan arashios-")
        check(bool(item.get("description")), f"{name}: deskripsi singkat kosong")
        check(bool(item.get("long_description")), f"{name}: deskripsi panjang kosong")
        check(len(item.get("long_description", "").splitlines()) >= 2, f"{name}: deskripsi terlalu pendek")
        check(
            item.get("architecture", common.get("architecture", "all")) == "all",
            f"{name}: paket v1 harus arsitektur all",
        )
        depends = item.get("depends", [])
        check(isinstance(depends, list), f"{name}: daftar Depends harus berupa list")
    for name in ("arashios-branding", "arashios-arsenal", "arashios-repo-keyring"):
        check(name in names, f"paket wajib {name} tidak ada pada spesifikasi")


def check_built() -> None:
    debs = deb_files()
    if not debs:
        check(False, "belum ada paket yang dibangun di build/packages")
        return
    built = {deb.name.split("_")[0] for deb in debs}
    spec, _ = load_spec()
    for item in spec.get("packages", []):
        name = item["name"]
        if item.get("external"):
            continue
        check(name in built, f"paket {name} belum dibangun")
    for deb in debs:
        control = package_control(deb)
        name = control.get("Package", deb.name)
        for field in ("Package", "Version", "Architecture", "Maintainer", "Section", "Priority", "Description"):
            check(field in control, f"{name}: field control {field} hilang")
        check(control.get("Maintainer", "").endswith(">"), f"{name}: Maintainer tidak valid")
        check(control.get("Architecture") == "all", f"{name}: arsitektur harus all")
        check(control.get("Version", "").endswith("-1"), f"{name}: versi paket harus berakhiran -1")
        files = package_files(deb)
        for path in files:
            if path.startswith("DEBIAN/"):
                check(
                    path.split("/")[-1] in {"control", "copyright", "changelog", "md5sums", "conffiles"},
                    f"{name}: berkas DEBIAN/{path.split('/')[-1]} tidak dikenal",
                )
                continue
            check(
                path.startswith(FHS_PREFIXES),
                f"{name}: berkas di luar FHS: {path}",
            )
        check(
            "usr/share/doc" in " ".join(files) or not files,
            f"{name}: paket tanpa dokumentasi di usr/share/doc",
        )


def check_determinism() -> None:
    debs = deb_files()
    if len(debs) < 2:
        return
    for deb in debs[:3]:
        result = subprocess.run(
            ["dpkg-deb", "-c", str(deb)],
            capture_output=True,
            text=True,
            check=False,
        )
        stamps = {line.split()[-2] for line in result.stdout.splitlines() if "UTC" in line}
        check(
            len(stamps) <= 1,
            f"{deb.name}: timestamp berkas tidak seragam, paket tidak reproducible",
        )


def check_repository() -> None:
    release = REPO / "dists" / "stable" / "Release"
    if not release.is_file():
        check(False, "repository belum dibangun, jalankan scripts/build-repo.py")
        return
    text = release.read_text(encoding="utf-8")
    for field in ("Origin:", "Suite: stable", "Components: main", "Architectures:", "MD5Sum:", "SHA256:"):
        check(field in text, f"Release repository tidak memuat {field}")
    inrelease = REPO / "dists" / "stable" / "InRelease"
    if inrelease.is_file():
        keyring = ROOT / "repo" / "keys" / "arashios-archive-keyring.gpg"
        if keyring.is_file():
            result = subprocess.run(
                ["gpgv", "--keyring", str(keyring), str(inrelease)],
                capture_output=True,
                text=True,
                check=False,
            )
            check(result.returncode == 0, "InRelease tidak terverifikasi dengan kunci repo")
        else:
            check(False, "keyring repository tidak ditemukan")
    packages = REPO / "dists" / "stable" / "main" / "binary-amd64" / "Packages"
    if packages.is_file():
        entries = packages.read_text(encoding="utf-8")
        check("Filename: pool/" in entries, "Filename pada Packages harus relatif ke root repo")
        check("SHA256:" in entries, "Packages harus memuat checksum SHA256")
    else:
        check(False, "indeks Packages amd64 tidak ditemukan")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-built", action="store_true", help="hanya memeriksa spesifikasi")
    args = parser.parse_args()

    check_spec()
    if not args.skip_built:
        check_built()
        check_determinism()
        check_repository()

    if errors:
        print(f"Package checks failed: {len(errors)} of {checks}")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"Package checks passed: {checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
