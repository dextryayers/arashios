#!/usr/bin/env python3
"""Static verification for the ArashiOS toolstack catalog and vendor manifests.

The checker validates catalog rules, workflow coverage, package list
consistency, manifest completeness, and license policy. It never downloads
anything and never executes a security tool.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - dependency is checked by check-env
    print("ERROR: PyYAML tidak tersedia. Pasang paket python3-yaml.", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "tools" / "catalog.yaml"
PINS = ROOT / "tools" / "source-pins.yaml"
MANIFEST_DIR = ROOT / "vendor" / "manifests"
RUNTIME_CATALOG = (
    ROOT
    / "config"
    / "common"
    / "includes.chroot"
    / "usr"
    / "share"
    / "arashios"
    / "toolstack"
    / "catalog.json"
)
SECURITY_LIST = ROOT / "config" / "common" / "package-lists" / "20-security.list.chroot"

SUPPORTED_ARCHES = ("amd64", "arm64", "i386")
WORKFLOWS = tuple(f"WF-{index:02d}" for index in range(1, 13))
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
PACKAGE_RE = re.compile(r"^[a-z0-9][a-z0-9+.-]*$")

MIN_T0 = 130
MIN_T1 = 40
T2_RANGE = (8, 12)
MIN_T3 = 3

ALLOWED_T1_LICENSES = {
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

errors: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def read_packages(path: Path) -> list[str]:
    packages: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        packages.extend(line.split())
    return packages


def all_listed_packages() -> set[str]:
    packages: set[str] = set()
    for path in sorted((ROOT / "config").rglob("*.list.chroot")):
        packages.update(read_packages(path))
    return packages


def main() -> int:
    catalog = load_yaml(CATALOG)
    pins = load_yaml(PINS).get("sources", {})

    workflows = catalog.get("workflows", {})
    check(set(workflows) == set(WORKFLOWS), f"katalog harus memuat 12 alur kerja {WORKFLOWS[0]} sampai {WORKFLOWS[-1]}")

    tools = catalog.get("tools", [])
    listed = all_listed_packages()
    security_packages = set(read_packages(SECURITY_LIST)) if SECURITY_LIST.exists() else set()

    names: set[str] = set()
    tier_counts = {"T0": 0, "T1": 0, "T2": 0, "T3": 0}
    coverage = {wf: {"T0": 0, "T1": 0} for wf in WORKFLOWS}
    catalog_packages: set[str] = set()

    for tool in tools:
        name = tool.get("name", "")
        tier = tool.get("tier", "")
        distribution = tool.get("distribution", catalog.get("tiers", {}).get(tier, {}).get("distribution", "iso"))
        check(bool(NAME_RE.match(name)), f"nama tool tidak valid: {name!r}")
        check(name not in names, f"nama tool duplikat: {name}")
        names.add(name)

        tier = tool.get("tier", "")
        check(tier in tier_counts, f"{name}: tier tidak dikenal {tier!r}")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

        raw_workflows = tool.get("workflow", "")
        tool_workflows = [raw_workflows] if isinstance(raw_workflows, str) else list(raw_workflows)
        check(bool(tool_workflows), f"{name}: alur kerja kosong")
        for workflow in tool_workflows:
            check(workflow in workflows, f"{name}: alur kerja tidak dikenal {workflow!r}")
            if workflow in coverage and tier in ("T0", "T1"):
                coverage[workflow][tier] += 1

        check(bool(str(tool.get("summary", "")).strip()), f"{name}: ringkasan kosong")
        check(bool(str(tool.get("license", "")).strip()), f"{name}: lisensi kosong")
        check(bool(str(tool.get("category", "")).strip()), f"{name}: kategori kosong")

        arch = tool.get("arch", list(SUPPORTED_ARCHES))
        check(set(arch) <= set(SUPPORTED_ARCHES), f"{name}: arsitektur tidak dikenal {arch}")
        check(bool(arch), f"{name}: daftar arsitektur kosong")

        if tier == "T0":
            package = tool.get("package", "")
            check(bool(PACKAGE_RE.match(package)), f"{name}: nama paket tidak valid {package!r}")
            check(package in listed, f"{name}: paket {package} tidak ada di package list")
            check(package in security_packages or package in listed, f"{name}: paket {package} tidak terlacak")
            catalog_packages.add(package)
            check(distribution == "iso", f"{name}: tool T0 harus distribusi iso")
            check(tool.get("license") == "debian", f"{name}: tool T0 harus memakai lisensi debian")
        elif tier == "T1":
            source_key = tool.get("source", "")
            check(source_key in pins, f"{name}: pin sumber {source_key!r} tidak ada di source-pins.yaml")
            pin = pins.get(source_key, {})
            commit = str(pin.get("commit", ""))
            check(bool(COMMIT_RE.match(commit)), f"{name}: commit sumber bukan sha1 40 karakter")
            check(bool(pin.get("url", "").startswith("https://")), f"{name}: URL sumber harus https")
            check(bool(pin.get("ref", "")), f"{name}: ref sumber kosong")
            check(tool.get("license") in ALLOWED_T1_LICENSES, f"{name}: lisensi T1 {tool.get('license')!r} di luar daftar")
            check(distribution == "vendor", f"{name}: tool T1 harus distribusi vendor")
            check(str(tool.get("install_path", "")).startswith("/"), f"{name}: install path T1 harus absolut")
        elif tier == "T2":
            check(distribution == "installer", f"{name}: tool T2 harus distribusi installer")
            check(distribution != "iso", f"{name}: tool T2 tidak boleh masuk image")
        elif tier == "T3":
            check(distribution == "container", f"{name}: tool T3 harus distribusi container")
            image = str(tool.get("image", ""))
            check(image.startswith("docker.io/"), f"{name}: image T3 harus memakai registry docker.io")
            check("latest" not in image, f"{name}: image T3 tidak boleh memakai tag latest")

    check(tier_counts["T0"] >= MIN_T0, f"jumlah tool T0 {tier_counts['T0']} di bawah target {MIN_T0}")
    check(tier_counts["T1"] >= MIN_T1, f"jumlah tool T1 {tier_counts['T1']} di bawah target {MIN_T1}")
    check(
        T2_RANGE[0] <= tier_counts["T2"] <= T2_RANGE[1],
        f"jumlah tool T2 {tier_counts['T2']} di luar rentang {T2_RANGE}",
    )
    check(tier_counts["T3"] >= MIN_T3, f"jumlah tool T3 {tier_counts['T3']} di bawah target {MIN_T3}")

    for workflow in WORKFLOWS:
        check(coverage[workflow]["T0"] >= 1, f"alur kerja {workflow} tidak punya tool T0")
        check(coverage[workflow]["T1"] >= 1, f"alur kerja {workflow} tidak punya tool T1")

    check(
        security_packages <= catalog_packages,
        "paket pada 20-security.list.chroot di luar katalog: "
        + ", ".join(sorted(security_packages - catalog_packages)),
    )

    manifest_files = sorted(MANIFEST_DIR.glob("*.yaml"))
    check(len(manifest_files) >= len(names), "jumlah manifest lebih kecil dari jumlah tool")
    for path in manifest_files:
        if path.name == "index.yaml":
            continue
        manifest = load_yaml(path)
        name = manifest.get("name", "")
        check(name == path.stem, f"{path.name}: nama manifest {name!r} tidak sesuai berkas")
        for field in ("name", "version", "category", "workflow", "tier", "source", "license", "arch", "build", "artifact", "install", "test"):
            check(field in manifest, f"{path.name}: field manifest {field} hilang")
        arch = manifest.get("arch", {})
        check(set(arch) == set(SUPPORTED_ARCHES), f"{path.name}: peta arsitektur tidak lengkap")
        test = manifest.get("test", {})
        check(bool(test.get("kind")), f"{path.name}: smoke test tidak punya jenis")
        if test.get("kind") == "version":
            check(bool(test.get("command")), f"{path.name}: smoke test version tanpa perintah")
        if manifest.get("tier") == "T1":
            check(bool(COMMIT_RE.match(str(manifest.get("source_commit", "")))), f"{path.name}: commit sumber tidak valid")
            artifact = manifest.get("artifact", {})
            check(
                bool(str(artifact.get("sha256", ""))) or artifact.get("status") == "source-locked",
                f"{path.name}: artifact tanpa hash dan tanpa status source-locked",
            )
            if artifact.get("sha256"):
                check(bool(SHA256_RE.match(str(artifact["sha256"]))), f"{path.name}: sha256 artifact tidak valid")

    if RUNTIME_CATALOG.exists():
        runtime = json.loads(RUNTIME_CATALOG.read_text(encoding="utf-8"))
        check(len(runtime.get("tools", [])) == len(names), "katalog runtime tidak sinkron dengan katalog sumber")
        check(set(runtime.get("workflows", {})) == set(WORKFLOWS), "katalog runtime kehilangan alur kerja")
    else:
        check(False, "katalog runtime tidak ditemukan")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate-toolstack.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    check(result.returncode == 0, f"hasil generate toolstack kedaluwarsa: {result.stdout.strip()} {result.stderr.strip()}")

    for path in sorted((ROOT / "config").rglob("*.list*")):
        text = path.read_text(encoding="utf-8").lower()
        check("kali" not in text, f"{path.relative_to(ROOT)}:Mention repository Kali")
        check("blackarch" not in text, f"{path.relative_to(ROOT)}: mention repository BlackArch")

    if errors:
        print(f"Toolstack checks failed: {len(errors)} of {checks}")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"Toolstack checks passed: {checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
