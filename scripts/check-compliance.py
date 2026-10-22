#!/usr/bin/env python3
"""Audit the ArashiOS compliance requirements before a release.

The audit covers the legal and privacy rules from plan.md sections 35 and 36:
licenses, attribution, dual use notice, export notice, privacy policy,
trademark statement, and the absence of network calls in maintainer scripts.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML tidak tersedia. Pasang paket python3-yaml.", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "tools" / "catalog.yaml"
LICENSE_DOC = ROOT / "docs" / "LICENSES.md"
NOTICE = ROOT / "NOTICE"
LEGAL = ROOT / "docs" / "LEGAL.md"
PRIVACY = ROOT / "docs" / "PRIVACY.md"
TRADEMARK = ROOT / "docs" / "TRADEMARK.md"
SECURITY = ROOT / "SECURITY.md"
CODE_OF_CONDUCT = ROOT / "CODE_OF_CONDUCT.md"

errors: list[str] = []
checks = 0
results: list[dict] = []


def check(identifier: str, condition: bool, message: str) -> None:
    global checks
    checks += 1
    results.append({"id": identifier, "status": "ok" if condition else "fail", "detail": message})
    if not condition:
        errors.append(f"{identifier}: {message}")


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def check_documents() -> None:
    for path, needle, identifier in (
        (LEGAL, "GPL-3.0-or-later", "C-01"),
        (LEGAL, "CC-BY-SA-4.0", "C-02"),
        (LEGAL, "Ekspor", "C-03"),
        (LEGAL, "manifes", "C-04"),
        (NOTICE, "Kanagawa", "C-05"),
        (NOTICE, "Wordlist ArashiOS", "C-06"),
        (PRIVACY, "telemetry", "C-07"),
        (PRIVACY, "akun", "C-08"),
        (TRADEMARK, "merek", "C-09"),
        (SECURITY, "72", "C-10"),
        (SECURITY, "safe harbor", "C-11"),
        (CODE_OF_CONDUCT, "Contributor Covenant", "C-12"),
    ):
        text = read(path)
        check(identifier, path.is_file() and needle.lower() in text.lower(),
              f"{path.name} tidak memuat {needle!r}")


def check_dual_use() -> None:
    text = read(LEGAL)
    check("C-13", "dual-use" in text.lower() or "dual use" in text.lower(),
          "legal tidak memuat disclaimer dual use")
    check("C-13", "izin" in text.lower(), "legal tidak memuat kewajiban izin")


def check_attribution() -> None:
    text = read(LEGAL)
    check("C-14", "Debian" in text, "legal tidak memuat atribusi Debian")
    check("C-15", "tidak diklaim sebagai proyek resmi" in text.lower(),
          "legal tidak menyatakan ArashiOS bukan proyek resmi Debian")


def check_licenses() -> None:
    with CATALOG.open(encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle) or {}
    tools = catalog.get("tools", [])
    doc = read(LICENSE_DOC)
    for tool in tools:
        tier = tool.get("tier", "")
        name = tool.get("name", "")
        license_id = tool.get("license", "")
        if tier == "T1":
            check("C-16", f"| `{name}`" in doc, f"{name} tidak ada di docs/LICENSES.md")
            check("C-16", bool(license_id) and license_id != "proprietary",
                  f"{name} memakai lisensi {license_id!r}")
        if tier in {"T2", "T3"}:
            check("C-17", tool.get("distribution") in {"installer", "container"},
                  f"{name} tier {tier} tidak opt-in")
    proprietary = [t for t in tools if t.get("license") == "proprietary"]
    check("C-17", all(t.get("distribution") != "iso" for t in proprietary),
          "tool proprietary ditemukan pada distribusi iso")


def check_no_network_maintainer() -> None:
    offenders = []
    for path in (ROOT / "config").rglob("*.chroot"):
        text = read(path)
        if re.search(r"\b(wget|curl)\b", text) and "postinst" in path.name:
            offenders.append(str(path.relative_to(ROOT)))
    check("C-18", not offenders, "skrip pemelihara mengakses jaringan: " + ", ".join(offenders))

    packages = ROOT / "packages" / "packages.yaml"
    with packages.open(encoding="utf-8") as handle:
        spec = yaml.safe_load(handle) or {}
    for item in spec.get("packages", []):
        depends = item.get("depends", [])
        check("C-19", "curl" not in depends and "wget" not in depends,
              f"{item['name']} bergantung pada pengunduh jaringan")


def check_third_party_assets() -> None:
    banner = read(ROOT / "branding" / "logo" / "arashios-mark.svg")
    check("C-20", "<svg" in banner, "mark ArashiOS bukan SVG yang valid")
    theme_manifest = ROOT / "build" / "theme" / "manifest.json"
    if theme_manifest.is_file():
        data = json.loads(read(theme_manifest))
        check("C-21", bool(data.get("files") or data.get("entries")),
              "manifest tema tidak memuat daftar berkas")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="tulis laporan JSON")
    args = parser.parse_args()

    check_documents()
    check_dual_use()
    check_attribution()
    check_licenses()
    check_no_network_maintainer()
    check_third_party_assets()

    report = {
        "schema_version": 1,
        "results": results,
        "failures": len(errors),
        "checks": checks,
    }
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if errors:
        print(f"Compliance checks failed: {len(errors)} of {checks}")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"Compliance checks passed: {checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
