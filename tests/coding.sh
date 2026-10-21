#!/usr/bin/env bash
# ArashiOS coding environment tests.
#
# The suite validates the toolchain catalog and lock, renders every project
# template, runs the language smoke test, and measures shell startup time with
# the shipped Zsh configuration.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/config/common/includes.chroot/usr/local/bin"
SKEL="$ROOT/config/common/includes.chroot/etc/skel"
TMP="$(mktemp -d)"
FAILURES=0
SHELL_BUDGET_MS=1200

cleanup() {
    rm -rf "$TMP"
}
trap cleanup EXIT

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

printf 'ArashiOS coding environment tests\n\n'

printf 'Katalog toolchain:\n'
expect_zero "katalog toolchain runtime sinkron" python3 "$ROOT/scripts/generate-toolchain.py" --check
expect_zero "lock toolchain lengkap" python3 "$ROOT/scripts/refresh-toolchain-lock.py" --check
expect_zero "daftar toolchain" "$BIN/arashios-toolchain" list --json
expect_zero "status toolchain" "$BIN/arashios-toolchain" status --json
expect_zero "diagnosis toolchain" "$BIN/arashios-toolchain" doctor --json
expect_zero "dry run pasang toolchain" "$BIN/arashios-toolchain" install uv --dry-run
expect_zero "cetak environment toolchain" "$BIN/arashios-toolchain" env

python3 - "$BIN" "$TMP" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

binary, tmp = sys.argv[1], Path(sys.argv[2])
result = subprocess.run(
    [f"{binary}/arashios-toolchain", "list", "--json"],
    capture_output=True,
    text=True,
    check=True,
)
data = json.loads(result.stdout)
names = {entry["name"] for entry in data["components"]}
expected = {"uv", "fnm", "node", "rustup", "rust", "go", "starship", "eza", "vscodium"}
missing = expected - names
assert not missing, f"komponen toolchain hilang: {sorted(missing)}"
for entry in data["components"]:
    if entry["kind"] == "archive":
        assert entry["supported"], f"{entry['name']} tidak didukung pada {data['arch']}"
        assert entry["sha256"], f"{entry['name']} tidak punya checksum terkunci"
print("OK:   komponen toolchain lengkap dengan checksum")
PY

printf '\nTemplate proyek:\n'
expect_zero "daftar template" "$BIN/arashios-new-project" list --json
for kind in python go rust node c java security-report; do
    target="$TMP/$kind"
    if "$BIN/arashios-new-project" create "$kind" "$target" >"$TMP/out" 2>&1; then
        if grep -rq '@NAME@\|@UPPER@\|@MODULE@\|@DATE@\|@YEAR@' "$target"; then
            fail "template $kind masih punya placeholder"
        else
            ok "template $kind dirender lengkap"
        fi
    else
        fail "template $kind gagal dibuat"
        sed -n '1,20p' "$TMP/out" >&2
    fi
done
expect_fail "template tidak dikenal ditolak" "$BIN/arashios-new-project" create salah "$TMP/salah"

printf '\nSmoke test bahasa:\n'
if "$BIN/arashios-coding-smoke" --output "$TMP/coding.json" >"$TMP/out" 2>&1; then
    ok "smoke test bahasa lulus"
else
    fail "smoke test bahasa gagal"
    sed -n '1,30p' "$TMP/out" >&2
fi
python3 - "$TMP/coding.json" <<'PY'
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert report["failures"] == 0, report
assert report["passed"] >= 3, f"hanya {report['passed']} bahasa yang lulus"
print(f"OK:   {report['passed']} bahasa lulus, {report['skipped']} dilewati")
PY

printf '\nShell startup:\n'
if command -v zsh >/dev/null 2>&1; then
    home="$TMP/home"
    mkdir -p "$home"
    cp "$SKEL/.zshrc" "$home/.zshrc"
    cp "$SKEL/.tmux.conf" "$home/.tmux.conf"
    cp "$SKEL/.gitconfig" "$home/.gitconfig"
    total=0
    runs=5
    for _ in $(seq 1 "$runs"); do
        start="$(date +%s%N)"
        HOME="$home" ZDOTDIR="$home" zsh -i -c exit >/dev/null 2>&1 || true
        end="$(date +%s%N)"
        total=$((total + (end - start) / 1000000))
    done
    average=$((total / runs))
    printf '  rata-rata %s ms dari %s kali jalan\n' "$average" "$runs"
    if [ "$average" -le "$SHELL_BUDGET_MS" ]; then
        ok "startup shell dalam batas ${SHELL_BUDGET_MS} ms"
    else
        fail "startup shell ${average} ms melebihi ${SHELL_BUDGET_MS} ms"
    fi
else
    printf 'SKIP: zsh tidak tersedia di host\n'
fi

printf '\n'
if [ "$FAILURES" -gt 0 ]; then
    printf 'Coding tests gagal: %s masalah.\n' "$FAILURES" >&2
    exit 1
fi
printf 'Coding tests lulus.\n'
