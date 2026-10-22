#!/usr/bin/env bash
# ArashiOS toolstack tests.
#
# The suite validates the catalog, the vendor manifests, the wordlist data, the
# license metadata, and the behaviour of the arsenal and lab commands in a
# sandbox. It never downloads a security tool and never touches the host
# package database.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/config/common/includes.chroot/usr/local/bin"
TMP="$(mktemp -d)"
FAILURES=0

cleanup() {
    rm -rf "$TMP"
}
trap cleanup EXIT

log() {
    printf '  %s\n' "$*"
}

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    FAILURES=$((FAILURES + 1))
}

ok() {
    printf 'OK:   %s\n' "$*"
}

expect_zero() {
    local label="$1"
    shift
    if "$@" >"$TMP/out" 2>&1; then
        ok "$label"
    else
        fail "$label"
        sed -n '1,20p' "$TMP/out" >&2
    fi
}

expect_fail() {
    local label="$1"
    shift
    if "$@" >"$TMP/out" 2>&1; then
        fail "$label, perintah seharusnya gagal"
        sed -n '1,20p' "$TMP/out" >&2
    else
        ok "$label"
    fi
}

printf 'ArashiOS toolstack tests\n\n'

printf 'Pemeriksaan statis:\n'
expect_zero "katalog dan manifest toolstack" python3 "$ROOT/scripts/check-toolstack.py"
expect_zero "katalog runtime toolstack sinkron" python3 "$ROOT/scripts/generate-toolstack.py" --check
expect_zero "wordlist dan manifestnya" python3 "$ROOT/scripts/check-wordlists.py"
expect_zero "metadata lisensi" python3 "$ROOT/scripts/check-licenses.py"
expect_zero "katalog toolchain runtime sinkron" python3 "$ROOT/scripts/generate-toolchain.py" --check
expect_zero "lock toolchain lengkap" python3 "$ROOT/scripts/refresh-toolchain-lock.py" --check

printf '\nArsenal:\n'
expect_zero "daftar tool" "$BIN/arashios-arsenal" list --tier T0
expect_zero "daftar tool JSON" "$BIN/arashios-arsenal" list --json
expect_zero "detail tool" "$BIN/arashios-arsenal" info nmap
expect_zero "coverage alur kerja" "$BIN/arashios-arsenal" workflows --json
expect_zero "verifikasi tool" "$BIN/arashios-arsenal" verify --tier T0
expect_zero "dry run pasang tool" "$BIN/arashios-arsenal" install nuclei --dry-run
expect_fail "hapus tool yang tidak dipasang" "$BIN/arashios-arsenal" remove nuclei
expect_fail "tool tidak dikenal ditolak" "$BIN/arashios-arsenal" info tool-hantu
expect_zero "diagnosis toolstack" "$BIN/arashios-arsenal" doctor --json

python3 - "$BIN" "$TMP" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

binary, tmp = sys.argv[1], Path(sys.argv[2])
result = subprocess.run(
    [f"{binary}/arashios-arsenal", "list", "--json"],
    capture_output=True,
    text=True,
    check=True,
)
data = json.loads(result.stdout)
tiers = {tool["tier"] for tool in data["tools"]}
assert {"T0", "T1", "T2", "T3"} <= tiers, f"tier tidak lengkap: {tiers}"
assert data["count"] >= 180, f"jumlah tool terlalu kecil: {data['count']}"

result = subprocess.run(
    [f"{binary}/arashios-arsenal", "workflows", "--json"],
    capture_output=True,
    text=True,
    check=True,
)
coverage = json.loads(result.stdout)["workflows"]
assert len(coverage) == 12, f"alur kerja tidak lengkap: {len(coverage)}"
for workflow, entry in coverage.items():
    assert entry["T0"], f"{workflow} tidak punya tool T0"
    assert entry["T1"], f"{workflow} tidak punya tool T1"

catalog = {
    "schema_version": 1,
    "catalog_version": "test",
    "workflows": {"WF-01": "Reconnaissance"},
    "tools": [
        {
            "name": "ls",
            "tier": "T0",
            "workflow": "WF-01",
            "workflows": ["WF-01"],
            "category": "utilitas",
            "distribution": "iso",
            "summary": "uji",
            "license": "debian",
            "arch": {"amd64": "supported", "arm64": "supported", "i386": "supported"},
            "install_path": "/bin/ls",
            "test": {"kind": "presence", "command": ["ls"], "version_args": ["--version"]},
        }
    ],
}
catalog_path = tmp / "catalog.json"
catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
result = subprocess.run(
    [f"{binary}/arashios-tool-smoke", "--catalog", str(catalog_path), "--json"],
    capture_output=True,
    text=True,
    check=True,
)
report = json.loads(result.stdout)
assert report["checked"] == 1, report
assert report["results"][0]["status"] == "ok", report
assert report["failures"] == 0, report
print("OK:   arsenal JSON dan smoke harness")
PY

if [ -f "$ROOT/vendor/artifacts.lock.json" ]; then
    printf '\nSiklus pasang tier 1:\n'
    artifact="$(python3 - "$ROOT/vendor/artifacts.lock.json" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
artifacts = data.get("artifacts", {})
for name, arches in sorted(artifacts.items()):
    for arch, record in sorted(arches.items()):
        if arch == "amd64":
            print(f"{name}|{record['path']}")
            raise SystemExit(0)
raise SystemExit(1)
PY
)" || artifact=""
    if [ -n "$artifact" ]; then
        tool_name="${artifact%%|*}"
        tool_path="${artifact#*|}"
        if [ -f "$ROOT/$tool_path" ]; then
            sandbox="$TMP/home"
            mkdir -p "$sandbox"
            if HOME="$sandbox" XDG_DATA_HOME="$sandbox/.local/share" \
                "$BIN/arashios-arsenal" install "$tool_name" --from "$ROOT/$tool_path" >"$TMP/out" 2>&1; then
                ok "artefak $tool_name dipasang setelah checksum cocok"
            else
                fail "pemasangan $tool_name gagal"
                sed -n '1,20p' "$TMP/out" >&2
            fi
            if HOME="$sandbox" XDG_DATA_HOME="$sandbox/.local/share" \
                "$BIN/arashios-arsenal" remove "$tool_name" >"$TMP/out" 2>&1; then
                ok "artefak $tool_name dilepas bersih"
            else
                fail "pelepasan $tool_name gagal"
                sed -n '1,20p' "$TMP/out" >&2
            fi
        else
            printf '  catatan: artefak %s tidak ada di host, pengujian dilewati\n' "$tool_name"
        fi
    fi
fi

printf '\nLab dan container:\n'
expect_zero "daftar lab" "$BIN/arashios-lab" list
expect_zero "rencana lab dengan digest" "$BIN/arashios-lab" plan dvwa
expect_fail "lab tanpa digest ditolak" "$BIN/arashios-lab" plan juice-shop
expect_zero "daftar template container" "$BIN/arashios-container" list
if "$BIN/arashios-container" doctor --json >"$TMP/doctor.json" 2>&1; then
    ok "diagnosis container"
else
    printf '  catatan: podman tidak tersedia di host, masalah dilaporkan\n'
    python3 -c "
import json, sys
data = json.load(open('$TMP/doctor.json'))
assert 'problems' in data and 'notes' in data
print('OK:   diagnosis container melaporkan JSON yang valid')
"
fi
expect_zero "rencana build container" "$BIN/arashios-container" build python --dry-run

printf '\n'
if [ "$FAILURES" -gt 0 ]; then
    printf 'Toolstack tests gagal: %s masalah.\n' "$FAILURES" >&2
    exit 1
fi
printf 'Toolstack tests lulus.\n'
