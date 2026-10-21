#!/usr/bin/env python3
"""Generate ArashiOS tool manifests and the runtime toolstack catalog.

Sources of truth:
  tools/catalog.yaml      metadata, tiers, workflows, packages
  tools/source-pins.yaml  pinned upstream refs and commits for tier 1

Outputs:
  vendor/manifests/<tool>.yaml            one manifest per tool
  vendor/manifests/index.yaml             summary index
  config/common/includes.chroot/usr/share/arashios/toolstack/catalog.json

Usage:
  scripts/generate-toolstack.py           write generated files
  scripts/generate-toolstack.py --check   fail when generated files differ
"""

from __future__ import annotations

import argparse
import json
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

SUPPORTED_ARCHES = ("amd64", "arm64", "i386")
TIERS = ("T0", "T1", "T2", "T3")
BUILD_KINDS = {
    "T0": "debian",
    "T1": {"go", "python", "ruby", "java", "source", "data", "binary"},
    "T2": {"installer"},
    "T3": {"container"},
}
GO_VERSION = "1.23"

TEST_DEFAULTS = {
    "nmap": ["--version"],
    "sqlmap": ["--version"],
    "hydra": ["-h"],
    "john": ["--list=build-info"],
    "hashcat": ["--help"],
    "nikto": ["-Version"],
    "gobuster": ["-h"],
    "ffuf": ["-h"],
    "wpscan": ["--version"],
    "wireshark": ["-v"],
    "tshark": ["--version"],
    "tcpdump": ["--version"],
    "bettercap": ["-h"],
    "medusa": ["-h"],
    "aircrack-ng": ["--help"],
    "responder": ["-h"],
    "vol": ["--help"],
    "impacket-GetNPUsers": ["-h"],
}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: {path} bukan mapping YAML.")
    return data


def dump_yaml(data: dict) -> str:
    return yaml.safe_dump(
        data,
        sort_keys=True,
        default_flow_style=False,
        allow_unicode=True,
        width=100,
    )


def arch_map(arches: list[str]) -> dict:
    return {name: ("supported" if name in arches else "unsupported") for name in SUPPORTED_ARCHES}


def build_command(kind: str, name: str, source: dict) -> str:
    if kind == "go":
        return (
            "CGO_ENABLED=0 GOOS=linux GOARCH=$TARGETARCH "
            "go build -trimpath -ldflags '-s -w' -o $OUT ./cmd/" + name
        )
    if kind == "python":
        return f"python3 -m pip install --no-deps --prefix=$PREFIX {name}"
    if kind == "ruby":
        return f"gem install --install-dir=$PREFIX {name}"
    if kind == "java":
        return f"java -jar {name}.jar"
    if kind == "source":
        return f"make -C {source.get('ref', 'source')} install PREFIX=$PREFIX"
    if kind == "data":
        return f"install -d $PREFIX && cp -a {source.get('ref', 'source')}/. $PREFIX/"
    if kind == "binary":
        return f"install -m 0755 {name} $PREFIX/bin/{name}"
    return ""


def normalize_tool(raw: dict, catalog: dict, pins: dict) -> dict:
    name = raw["name"]
    tier = raw["tier"]
    defaults = catalog.get("defaults", {})
    arch_list = raw.get("arch", defaults.get("arch", list(SUPPORTED_ARCHES)))
    role = raw.get("role", defaults.get("role", "security"))
    distribution = raw.get("distribution", catalog["tiers"][tier]["distribution"])
    raw_workflows = raw["workflow"]
    if isinstance(raw_workflows, str):
        raw_workflows = [raw_workflows]
    workflows = list(raw_workflows)
    workflow = workflows[0]
    binary = raw.get("binary", "none")
    license_id = raw["license"]

    tool: dict = {
        "name": name,
        "tier": tier,
        "role": role,
        "workflow": workflow,
        "workflows": workflows,
        "category": raw.get("category", "general"),
        "distribution": distribution,
        "summary": raw.get("summary", "").strip(),
        "license": license_id,
        "arch": arch_map(arch_list),
    }

    if tier == "T0":
        package = raw["package"]
        tool["version"] = f"debian-{catalog.get('debian_codename', 'bookworm')}"
        tool["source"] = f"https://packages.debian.org/{catalog.get('debian_codename', 'bookworm')}/{package}"
        tool["package"] = package
        tool["install"] = {"path": raw.get("install_path", f"/usr/bin/{binary}")}
        tool["build"] = {"kind": "debian", "package": package}
        tool["artifact"] = {
            "status": "debian-archive",
            "sha256": "",
            "note": "Checksum diambil dari indeks Debian saat build image.",
        }
        test_kind = "presence"
        command = [binary]
        expect = ""
    elif tier == "T1":
        source_key = raw["source"]
        pin = pins.get(source_key)
        if pin is None:
            raise SystemExit(f"ERROR: pin sumber untuk {name} tidak ditemukan di source-pins.yaml")
        kind = raw["build"]
        if kind not in BUILD_KINDS["T1"]:
            raise SystemExit(f"ERROR: build kind tidak dikenal untuk {name}: {kind}")
        tool["version"] = str(pin.get("version", pin.get("ref", "unknown")))
        tool["source"] = pin["url"]
        tool["source_ref"] = pin.get("ref", "")
        tool["source_commit"] = pin.get("commit", "")
        tool["license_file"] = pin.get("license_file", "")
        tool["install"] = {"path": raw.get("install_path", f"/usr/local/bin/{binary}")}
        build = {
            "kind": kind,
            "source_ref": pin.get("ref", ""),
            "source_commit": pin.get("commit", ""),
            "command": build_command(kind, name, pin),
        }
        if kind == "go":
            build["go_version"] = GO_VERSION
        tool["build"] = build
        tool["artifact"] = {
            "status": "source-locked",
            "sha256": "",
            "note": "Hash binary diisi oleh scripts/build-vendor-tools.sh saat artifact dibangun.",
        }
        test_kind = "version"
        command = [binary]
        expect = raw.get("expect", "")
    elif tier == "T2":
        tool["version"] = raw.get("version", "user-managed")
        tool["source"] = raw.get("source_url", "upstream")
        tool["install"] = {"path": raw.get("install_path", "")}
        tool["build"] = {"kind": "installer"}
        tool["artifact"] = {
            "status": "user-download",
            "sha256": "",
            "note": "Tool T2 tidak didistribusikan. Pengguna unduh sendiri dari upstream.",
        }
        test_kind = "presence"
        command = [binary]
        expect = ""
    else:
        tool["version"] = raw.get("version", "digest-pinned")
        tool["source"] = raw.get("image", "")
        tool["install"] = {"image": raw.get("image", "")}
        tool["build"] = {"kind": "container"}
        tool["artifact"] = {
            "status": "digest-required",
            "sha256": "",
            "note": "Container memakai digest. Arsenal menolak tag yang belum dikunci.",
        }
        test_kind = "presence"
        command = [binary]
        expect = ""

    if binary == "none":
        test_kind = "none"

    test = {"kind": test_kind, "command": command}
    if expect:
        test["expect"] = expect
    version_args = raw.get("version_args") or TEST_DEFAULTS.get(name)
    if version_args and test_kind in {"presence", "version"}:
        test["version_args"] = version_args
    tool["test"] = test
    if raw.get("notes"):
        tool["notes"] = raw["notes"]
    return tool


def render_manifest(tool: dict) -> dict:
    manifest = {
        "name": tool["name"],
        "version": tool["version"],
        "category": tool["category"],
        "workflow": tool["workflow"],
        "workflows": tool["workflows"],
        "tier": tool["tier"],
        "source": tool["source"],
        "license": tool["license"],
        "arch": tool["arch"],
        "build": tool["build"],
        "artifact": tool["artifact"],
        "install": tool["install"],
        "test": tool["test"],
    }
    for key in ("role", "distribution", "summary", "package", "source_ref", "source_commit", "license_file", "notes"):
        if key in tool:
            manifest[key] = tool[key]
    return manifest


def render_index(tools: list[dict], catalog: dict) -> dict:
    by_tier: dict[str, list[str]] = {tier: [] for tier in TIERS}
    by_workflow: dict[str, list[str]] = {wf: [] for wf in catalog["workflows"]}
    for tool in tools:
        by_tier[tool["tier"]].append(tool["name"])
        for workflow in tool["workflows"]:
            by_workflow[workflow].append(tool["name"])
    return {
        "schema_version": 1,
        "catalog_version": catalog["catalog_version"],
        "updated": catalog["updated"],
        "counts": {tier: len(names) for tier, names in by_tier.items()},
        "workflows": {
            wf: {
                "name": catalog["workflows"][wf],
                "tier0": sorted(n for n in by_workflow[wf] if n in by_tier["T0"]),
                "tier1": sorted(n for n in by_workflow[wf] if n in by_tier["T1"]),
            }
            for wf in sorted(catalog["workflows"])
        },
        "tools": sorted(tool["name"] for tool in tools),
    }


def runtime_entry(tool: dict) -> dict:
    entry = {
        "name": tool["name"],
        "tier": tool["tier"],
        "role": tool.get("role", "security"),
        "workflow": tool["workflow"],
        "workflows": tool["workflows"],
        "category": tool["category"],
        "distribution": tool["distribution"],
        "summary": tool["summary"],
        "license": tool["license"],
        "arch": tool["arch"],
        "install_path": tool["install"].get("path", ""),
        "test": tool["test"],
    }
    if "package" in tool:
        entry["package"] = tool["package"]
    if "source" in tool:
        entry["source"] = tool["source"]
    if "version" in tool:
        entry["version"] = tool["version"]
    if "source_ref" in tool:
        entry["source_ref"] = tool["source_ref"]
    if "source_commit" in tool:
        entry["source_commit"] = tool["source_commit"]
    if "artifact" in tool:
        entry["artifact_status"] = tool["artifact"]["status"]
        entry["artifact_sha256"] = tool["artifact"]["sha256"]
    if "notes" in tool:
        entry["notes"] = tool["notes"]
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="periksa hasil generate tanpa menulis")
    args = parser.parse_args()

    catalog = load_yaml(CATALOG)
    pins = load_yaml(PINS).get("sources", {})

    tools = []
    seen = set()
    for raw in catalog["tools"]:
        name = raw["name"]
        if name in seen:
            raise SystemExit(f"ERROR: nama tool duplikat di katalog: {name}")
        seen.add(name)
        tools.append(normalize_tool(raw, catalog, pins))
    tools.sort(key=lambda item: item["name"])

    outputs: dict[Path, str] = {}
    for tool in tools:
        manifest = render_manifest(tool)
        outputs[MANIFEST_DIR / f"{tool['name']}.yaml"] = dump_yaml(manifest)
    outputs[MANIFEST_DIR / "index.yaml"] = dump_yaml(render_index(tools, catalog))

    runtime = {
        "schema_version": 1,
        "catalog_version": catalog["catalog_version"],
        "updated": catalog["updated"],
        "debian_codename": catalog.get("debian_codename", "bookworm"),
        "workflows": catalog["workflows"],
        "tools": [runtime_entry(tool) for tool in tools],
    }
    outputs[RUNTIME_CATALOG] = json.dumps(runtime, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    stale = []
    for path, content in sorted(outputs.items()):
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        if args.check:
            stale.append(path.relative_to(ROOT))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    if args.check and stale:
        print("ERROR: hasil generate toolstack kedaluwarsa:", file=sys.stderr)
        for path in stale:
            print(f"  {path}", file=sys.stderr)
        return 1

    if not args.check:
        for path in MANIFEST_DIR.glob("*.yaml"):
            if path.name == "index.yaml":
                continue
            if path not in outputs:
                path.unlink()

    print(
        f"OK: {len(tools)} tool, "
        f"{sum(1 for t in tools if t['tier'] == 'T0')} T0, "
        f"{sum(1 for t in tools if t['tier'] == 'T1')} T1, "
        f"{sum(1 for t in tools if t['tier'] == 'T2')} T2, "
        f"{sum(1 for t in tools if t['tier'] == 'T3')} T3."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
