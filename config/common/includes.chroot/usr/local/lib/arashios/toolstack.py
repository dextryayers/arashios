"""Shared runtime helpers for the ArashiOS toolstack.

The module is installed at /usr/local/lib/arashios/toolstack.py and is used by
arashios-arsenal and arashios-tool-smoke. It only uses the Python standard
library so it runs on a stock Debian 12 system without extra packages.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

CATALOG_ENV = "ARASHIOS_TOOLSTACK_CATALOG"
DEFAULT_CATALOG = Path("/usr/share/arashios/toolstack/catalog.json")
def _repo_catalog() -> Path | None:
    """Locate the in-tree catalog when running from the repository."""
    relative = Path("config/common/includes.chroot/usr/share/arashios/toolstack/catalog.json")
    for parent in Path(__file__).resolve().parents:
        candidate = parent / relative
        if candidate.is_file():
            return candidate
    return None


REPO_CATALOG = _repo_catalog()
TIERS = ("T0", "T1", "T2", "T3")


def data_home() -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    if base:
        return Path(base)
    return Path.home() / ".local" / "share"


def state_dir() -> Path:
    return data_home() / "arashios"


def state_file() -> Path:
    return state_dir() / "arsenal-state.json"


def vendor_cache() -> Path:
    override = os.environ.get("ARASHIOS_VENDOR_CACHE")
    if override:
        return Path(override)
    return Path.home() / ".cache" / "arashios" / "vendor"


def catalog_candidates() -> list[Path]:
    candidates: list[Path] = []
    override = os.environ.get(CATALOG_ENV)
    if override:
        candidates.append(Path(override))
    candidates.append(DEFAULT_CATALOG)
    if REPO_CATALOG is not None:
        candidates.append(REPO_CATALOG)
    return candidates


def load_catalog(path: str | None = None) -> dict:
    paths = [Path(path)] if path else catalog_candidates()
    for candidate in paths:
        if candidate.is_file():
            with candidate.open(encoding="utf-8") as handle:
                return json.load(handle)
    raise SystemExit(
        "ERROR: katalog toolstack tidak ditemukan. "
        "Set ARASHIOS_TOOLSTACK_CATALOG atau pasang image ArashiOS."
    )


def tools_of(catalog: dict) -> list[dict]:
    return list(catalog.get("tools", []))


def find_tool(catalog: dict, name: str) -> dict | None:
    for tool in tools_of(catalog):
        if tool["name"] == name:
            return tool
    return None


def workflows_of(catalog: dict) -> dict:
    return dict(catalog.get("workflows", {}))


def tool_workflows(tool: dict) -> list[str]:
    if "workflows" in tool:
        return list(tool["workflows"])
    return [tool["workflow"]]


def coverage(catalog: dict) -> dict:
    result: dict[str, dict] = {}
    for workflow in workflows_of(catalog):
        entry = {"T0": [], "T1": [], "T2": [], "T3": []}
        for tool in tools_of(catalog):
            if workflow in tool_workflows(tool):
                entry.setdefault(tool["tier"], []).append(tool["name"])
        result[workflow] = entry
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_state() -> dict:
    path = state_file()
    if not path.is_file():
        return {"installed": {}}
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {"installed": {}}
    data.setdefault("installed", {})
    return data


def save_state(state: dict) -> None:
    path = state_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")


def record_install(name: str, kind: str, target: str, extra: dict | None = None) -> None:
    state = load_state()
    entry = {"kind": kind, "target": target, "installed_at": int(time.time())}
    if extra:
        entry.update(extra)
    state["installed"][name] = entry
    save_state(state)


def forget_install(name: str) -> dict | None:
    state = load_state()
    entry = state.get("installed", {}).pop(name, None)
    save_state(state)
    return entry


def installed_entries() -> dict:
    return load_state().get("installed", {})


def binary_path(tool: dict) -> str:
    binary = tool.get("test", {}).get("command", [""])[0]
    if not binary or binary == "none":
        return ""
    return shutil.which(binary) or ""


def artifact_candidates(tool: dict) -> list[Path]:
    name = tool["name"]
    version = str(tool.get("version", ""))
    cache = vendor_cache()
    found: list[Path] = []
    for pattern in (
        f"{name}-{version}-*.tar.gz",
        f"{name}-{version}-*.zip",
        f"{name}-{version}.tar.gz",
        f"{name}-{version}.zip",
        f"{name}.tar.gz",
        f"{name}.zip",
    ):
        found.extend(sorted(cache.glob(pattern)))
    return found


def verify_tool(tool: dict) -> dict:
    """Return a verification record for one tool."""
    tier = tool["tier"]
    result = {
        "name": tool["name"],
        "tier": tier,
        "workflow": tool.get("workflow", ""),
        "status": "skipped",
        "detail": "",
    }
    if tier == "T0":
        path = binary_path(tool)
        if path:
            result["status"] = "ok"
            result["detail"] = path
        else:
            result["status"] = "missing"
            binary = tool.get("test", {}).get("command", ["?"])[0]
            result["detail"] = f"binary {binary} tidak ditemukan"
        return result
    if tier == "T1":
        expected = str(tool.get("artifact_sha256", "") or "")
        candidates = artifact_candidates(tool)
        if not expected:
            result["status"] = "pending"
            result["detail"] = "artefak belum dibangun, sumber terkunci di " + str(tool.get("source_ref", ""))
            return result
        if not candidates:
            result["status"] = "missing"
            result["detail"] = "artefak tidak ada di cache " + str(vendor_cache())
            return result
        for candidate in candidates:
            digest = sha256_file(candidate)
            if digest == expected:
                result["status"] = "ok"
                result["detail"] = str(candidate)
                return result
        result["status"] = "corrupt"
        result["detail"] = "checksum artefak tidak cocok"
        return result
    result["status"] = "not-applicable"
    result["detail"] = f"tool {tier} tidak didistribusikan dalam image"
    return result


def run_tool_test(tool: dict, timeout: int = 30) -> dict:
    """Execute the smoke test of one tool without touching the network."""
    test = tool.get("test", {})
    kind = test.get("kind", "none")
    command = list(test.get("command", []))
    record = {
        "name": tool["name"],
        "tier": tool["tier"],
        "workflow": tool.get("workflow", ""),
        "kind": kind,
        "status": "skipped",
        "detail": "",
        "version": "",
    }
    if kind == "none":
        record["status"] = "skipped"
        record["detail"] = "tool tidak memiliki biner yang diuji"
        return record
    if not command or not command[0]:
        record["status"] = "skipped"
        record["detail"] = "perintah smoke test kosong"
        return record

    binary = command[0]
    if shutil.which(binary) is None:
        record["status"] = "missing"
        record["detail"] = f"binary {binary} tidak ditemukan"
        return record

    if kind == "presence":
        record["status"] = "ok"
        record["detail"] = shutil.which(binary) or binary
        version_args = test.get("version_args")
        if version_args:
            probe = subprocess.run(
                [binary, *version_args],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            output = (probe.stdout + probe.stderr).strip().splitlines()
            if output:
                record["version"] = output[0][:200]
        return record

    if kind == "version":
        try:
            probe = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            record["status"] = "timeout"
            record["detail"] = "perintah smoke test melewati batas waktu"
            return record
        output = (probe.stdout + probe.stderr).strip()
        record["version"] = output.splitlines()[0][:200] if output else ""
        expect = test.get("expect", "")
        if probe.returncode != 0:
            record["status"] = "failed"
            record["detail"] = f"keluar dengan status {probe.returncode}"
            return record
        if expect and expect.lower() not in output.lower():
            record["status"] = "failed"
            record["detail"] = f"output tidak memuat {expect!r}"
            return record
        record["status"] = "ok"
        record["detail"] = record["version"] or "selesai"
        return record

    record["status"] = "skipped"
    record["detail"] = f"jenis smoke test {kind!r} tidak dikenal"
    return record
