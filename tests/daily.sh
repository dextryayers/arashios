#!/usr/bin/env bash
# ArashiOS daily use tests.
#
# The suite validates the daily driver configuration and exercises the
# diagnostic commands in a sandbox. It never changes system state.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/config/common/includes.chroot/usr/local/bin"
TMP="$(mktemp -d)"
FAILURES=0

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

printf 'ArashiOS daily use tests\n\n'

printf 'Pemeriksaan statis:\n'
expect_zero "konfigurasi penggunaan harian" python3 "$ROOT/scripts/check-daily.py"
expect_zero "katalog paket tetap sinkron" python3 "$ROOT/scripts/check-toolstack.py"
expect_zero "validasi konfigurasi live-build" "$ROOT/scripts/validate-config.sh"

printf '\nDiagnosis harian:\n'
expect_zero "diagnosis harian area locale" "$BIN/arashios-daily" locale
expect_zero "diagnosis harian area power" "$BIN/arashios-daily" power
expect_zero "diagnosis harian seluruh area" "$BIN/arashios-daily" all
expect_zero "diagnosis harian JSON" "$BIN/arashios-daily" all --json


python3 - "$BIN" <<'PY'
import json
import subprocess
import sys

binary = sys.argv[1]
strict = subprocess.run(
    [f"{binary}/arashios-daily", "all", "--strict", "--json"],
    capture_output=True,
    text=True,
    check=False,
)
assert strict.returncode in (0, 1), strict.returncode
json.loads(strict.stdout)

result = subprocess.run(
    [f"{binary}/arashios-daily", "all", "--json"],
    capture_output=True,
    text=True,
    check=True,
)
data = json.loads(result.stdout)
areas = {item["area"] for item in data["results"]}
expected = {"network", "audio", "power", "print", "locale", "firmware"}
assert areas == expected, f"area tidak lengkap: {areas ^ expected}"
for item in data["results"]:
    assert item["status"] in {"ok", "warn", "missing"}, item
    assert "problems" in item, item
print("OK:   keluaran JSON harian valid")
PY

printf '\nLaporan hardware:\n'
expect_zero "laporan hardware JSON" "$BIN/arashios-hardware-report" --output "$TMP/report.json"
expect_zero "laporan hardware markdown" "$BIN/arashios-hardware-report" --format markdown --output "$TMP/report.md"
if [ -s "$TMP/report.json" ] && [ -s "$TMP/report.md" ]; then
    ok "laporan hardware terisi"
else
    fail "laporan hardware kosong"
fi
if grep -q "## Sistem" "$TMP/report.md"; then
    ok "laporan hardware memuat bagian sistem"
else
    fail "laporan hardware tidak memuat bagian sistem"
fi

printf '\n'
if [ "$FAILURES" -gt 0 ]; then
    printf 'Daily tests gagal: %s masalah.\n' "$FAILURES" >&2
    exit 1
fi
printf 'Daily tests lulus.\n'
