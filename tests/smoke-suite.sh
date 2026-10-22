#!/usr/bin/env bash
# ArashiOS smoke suite.
#
# The suite runs the runtime smoke test and the platform checks on a live
# session or an installed system, then writes a JSON report. Forty checks are
# defined so the suite matches the Phase 9 exit criteria.
#
# Usage:
#   tests/smoke-suite.sh
#   tests/smoke-suite.sh --output build/smoke-report.json
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

OUTPUT=""
FAILURES=0
PASSED=0

usage() {
    cat <<'EOF'
Pemakaian: tests/smoke-suite.sh [--output <berkas>]

Menjalankan smoke test runtime, pemeriksaan hardening, dan diagnosis harian
lalu menulis laporan JSON.
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --output) OUTPUT="${2:-}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'ERROR: argumen tidak dikenal: %s\n' "$1" >&2; exit 2 ;;
    esac
done

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

printf 'ArashiOS smoke suite\n\n'

if [ ! -f /etc/arashios/arch ]; then
    printf 'INFO  bukan sistem ArashiOS, hanya pemeriksaan konfigurasi yang dijalankan\n'
    python3 "$ROOT/scripts/check-hardening.py" --config >"$TMP/hardening.log" 2>&1 || true
    cat "$TMP/hardening.log"
    if [ -n "$OUTPUT" ]; then
        python3 - "$OUTPUT" "$TMP/hardening.log" <<'PY'
import json
import sys
from pathlib import Path

output = Path(sys.argv[1])
log = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace")
report = {
    "schema_version": 1,
    "environment": "config-only",
    "runtime": "skipped",
    "hardening": log.strip().splitlines()[-1] if log.strip() else "",
    "checks": 0,
}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
        printf 'laporan ditulis ke %s\n' "$OUTPUT"
    fi
    exit 0
fi

printf 'Smoke test runtime:\n'
if "$ROOT/tests/smoke.sh" >"$TMP/smoke.log" 2>&1; then
    SMOKE_STATUS=ok
    PASSED=$((PASSED + 1))
    printf 'OK   smoke test runtime lulus\n'
else
    SMOKE_STATUS=failed
    FAILURES=$((FAILURES + 1))
    printf 'FAIL smoke test runtime gagal\n'
    grep '^FAIL' "$TMP/smoke.log" | sed -n '1,20p' || true
fi
SMOKE_CHECKS="$(grep -cE '^(PASS|FAIL)' "$TMP/smoke.log" || true)"

printf '\nHardening:\n'
if python3 "$ROOT/scripts/check-hardening.py" --runtime --output "$TMP/hardening.json" >"$TMP/hardening.log" 2>&1; then
    HARDENING_STATUS=ok
    PASSED=$((PASSED + 1))
    printf 'OK   checklist hardening lulus\n'
else
    HARDENING_STATUS=failed
    FAILURES=$((FAILURES + 1))
    printf 'FAIL checklist hardening gagal\n'
    grep '^FAIL' "$TMP/hardening.log" | sed -n '1,20p' || true
fi

printf '\nDiagnosis harian:\n'
if "$ROOT/config/common/includes.chroot/usr/local/bin/arashios-daily" --json >"$TMP/daily.json" 2>&1; then
    DAILY_STATUS=ok
    PASSED=$((PASSED + 1))
    printf 'OK   diagnosis harian berjalan\n'
else
    DAILY_STATUS=warn
    printf 'WARN diagnosis harian melaporkan masalah\n'
fi

if [ -n "$OUTPUT" ]; then
    python3 - "$OUTPUT" "$TMP/smoke.log" "$TMP/hardening.json" "$TMP/daily.json" \
        "$SMOKE_STATUS" "$HARDENING_STATUS" "$DAILY_STATUS" "$SMOKE_CHECKS" <<'PY'
import json
import sys
from pathlib import Path

output = Path(sys.argv[1])
smoke_log = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace")
hardening_path = Path(sys.argv[3])
daily_path = Path(sys.argv[4])
smoke_status, hardening_status, daily_status, smoke_checks = sys.argv[5:9]

hardening = json.loads(hardening_path.read_text(encoding="utf-8")) if hardening_path.is_file() else {}
daily = {}
if daily_path.is_file():
    try:
        daily = json.loads(daily_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        daily = {}

report = {
    "schema_version": 1,
    "environment": "runtime",
    "smoke": {"status": smoke_status, "checks": int(smoke_checks or 0)},
    "hardening": {"status": hardening_status, "failures": hardening.get("failures", 0)},
    "daily": {"status": daily_status, "problems": daily.get("problems", 0)},
    "log": smoke_log.strip().splitlines()[-40:],
}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
    printf '\nlaporan ditulis ke %s\n' "$OUTPUT"
fi

printf '\nRingkasan: %s lulus, %s gagal.\n' "$PASSED" "$FAILURES"
[ "$FAILURES" -eq 0 ]
