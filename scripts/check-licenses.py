#!/usr/bin/env python3
"""Audit the license metadata of the ArashiOS toolstack.

The audit checks that every tier 1 tool declares a redistributable license, that
no tier 2 or tier 3 tool is marked as distributed inside the image, and that
docs/LICENSES.md lists every vendored tool.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML tidak tersedia. Pasang paket python3-yaml.", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "tools" / "catalog.yaml"
LICENSES_DOC = ROOT / "docs" / "LICENSES.md"
NOTICE = ROOT / "NOTICE"
WORDLIST_LICENSE = (
    ROOT
    / "config"
    / "common"
    / "includes.chroot"
    / "usr"
    / "share"
    / "wordlists"
    / "arashios"
    / "LICENSE"
)

REDISTRIBUTABLE = {
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "GPL-2.0-only",
    "GPL-3.0-only",
    "LGPL-3.0-only",
    "MIT",
    "VSL",
    "wxWindows-Licence",
}
NON_REDISTRIBUTABLE = {"proprietary"}

errors: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true", help="tulis ulang docs/LICENSES.md")
    args = parser.parse_args()

    with CATALOG.open(encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle) or {}
    pins_path = ROOT / "tools" / "source-pins.yaml"
    pins = {}
    if pins_path.is_file():
        with pins_path.open(encoding="utf-8") as handle:
            pins = (yaml.safe_load(handle) or {}).get("sources", {})
    tools = catalog.get("tools", [])
    defaults = catalog.get("defaults", {})

    rows: list[tuple[str, str, str, str, str]] = []
    for tool in tools:
        name = tool.get("name", "")
        tier = tool.get("tier", "")
        license_id = tool.get("license", "")
        distribution = tool.get("distribution", catalog.get("tiers", {}).get(tier, {}).get("distribution", "iso"))
        source = tool.get("source", "")
        if tier == "T1":
            check(license_id in REDISTRIBUTABLE, f"{name}: lisensi {license_id!r} tidak boleh didistribusikan ulang")
            check(bool(source), f"{name}: sumber lisensi kosong")
            pin = pins.get(str(source), {})
            rows.append((name, tier, license_id, distribution, str(pin.get("url", source))))
        elif tier in {"T2", "T3"}:
            check(distribution != "iso", f"{name}: tool {tier} tidak boleh masuk image")
            if license_id in NON_REDISTRIBUTABLE:
                check(distribution in {"installer", "container"}, f"{name}: tool proprietary harus opt-in")

    check(LICENSES_DOC.is_file(), "docs/LICENSES.md hilang")
    if LICENSES_DOC.is_file():
        text = LICENSES_DOC.read_text(encoding="utf-8")
        for name, _, _, _, _ in rows:
            check(f"| `{name}`" in text, f"docs/LICENSES.md belum memuat {name}")

    check(NOTICE.is_file(), "NOTICE hilang")
    if NOTICE.is_file():
        notice = NOTICE.read_text(encoding="utf-8")
        check("Kanagawa" in notice, "NOTICE belum mencantumkan Kanagawa")
        check("Wordlist ArashiOS" in notice, "NOTICE belum mencantumkan wordlist ArashiOS")

    check(WORDLIST_LICENSE.is_file(), "lisensi wordlist ArashiOS hilang")
    if WORDLIST_LICENSE.is_file():
        check(
            "CC-BY-SA-4.0" in WORDLIST_LICENSE.read_text(encoding="utf-8"),
            "lisensi wordlist ArashiOS tidak menyebut CC-BY-SA-4.0",
        )

    if args.update:
        lines = [
            "# Matriks Lisensi Tool ArashiOS",
            "",
            "Dokumen ini dihasilkan dari `tools/catalog.yaml` dengan",
            "`scripts/check-licenses.py --update`. Setiap tool tier 1 yang",
            "dibundel harus mencantumkan lisensi upstream dan sumbernya.",
            "",
            "| Tool | Tier | Lisensi | Distribusi | Sumber |",
            "|---|---|---|---|---|",
        ]
        for name, tier, license_id, distribution, source in sorted(rows):
            lines.append(f"| `{name}` | {tier} | {license_id} | {distribution} | {source} |")
        lines.extend(
            [
                "",
                "## Aturan",
                "",
                "1. Tool proprietary tidak pernah masuk image dan hanya tersedia",
                "   lewat tier 2 atau tier 3.",
                "2. Tool GPL menyertakan source code atau tawaran source sesuai",
                "   kewajiban lisensi.",
                "3. Perubahan lisensi upstream dipantau pada setiap rilis dan",
                "   tercatat di CHANGELOG.",
                "4. Wordlist ArashiOS memakai CC-BY-SA-4.0 dan dicatat di NOTICE.",
                "",
            ]
        )
        LICENSES_DOC.write_text("\n".join(lines), encoding="utf-8")
        print(f"OK: docs/LICENSES.md ditulis dengan {len(rows)} tool tier 1.")
        return 0

    if errors:
        print(f"License checks failed: {len(errors)} of {checks}")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"License checks passed: {checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
