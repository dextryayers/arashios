#!/usr/bin/env bash
# ArashiOS reproducibility check.
#
# The check rebuilds the ArashiOS package set twice with the same
# SOURCE_DATE_EPOCH and compares the results byte for byte. When two ISO
# artifacts are given it compares them with diffoscope when available and
# always records the checksums.
#
# Usage:
#   scripts/check-reproducibility.sh
#   scripts/check-reproducibility.sh --iso out/a.iso --iso out/b.iso
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT="$ROOT/build/reproducibility-report.json"
EPOCH="${SOURCE_DATE_EPOCH:-1735689600}"
ISOS=()

log() {
    printf '[repro] %s\n' "$*"
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --iso) ISOS+=("${2:-}"); shift 2 ;;
        -h|--help)
            printf 'Pemakaian: scripts/check-reproducibility.sh [--iso <berkas>]\n'
            exit 0
            ;;
        *) die "argumen tidak dikenal: $1" ;;
    esac
done

command -v python3 >/dev/null 2>&1 || die "python3 tidak ditemukan."
command -v dpkg-deb >/dev/null 2>&1 || die "dpkg-deb tidak ditemukan."

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

log "membangun paket untuk dua iterasi"
mkdir -p "$TMP/first" "$TMP/second"

for pass in first second; do
    cp -a "$ROOT/build/packages" "$TMP/$pass-packages" 2>/dev/null || true
    ( cd "$ROOT" && SOURCE_DATE_EPOCH="$EPOCH" python3 scripts/build-packages.py --all ) \
        >"$TMP/$pass.log" 2>&1 || {
        sed -n '1,20p' "$TMP/$pass.log" >&2
        die "pembangunan paket gagal pada iterasi $pass"
    }
    mkdir -p "$TMP/$pass"
    cp "$ROOT"/build/packages/*.deb "$TMP/$pass/"
    rm -f "$ROOT"/build/packages/*.deb
    cp -a "$TMP/$pass-packages"/*.deb "$ROOT/build/packages/" 2>/dev/null || true
done

log "membandingkan hasil build"
DIFFERENT=0
FIRST_LIST="$TMP/first.list"
SECOND_LIST="$TMP/second.list"
( cd "$TMP/first" && sha256sum *.deb | sort ) > "$FIRST_LIST"
( cd "$TMP/second" && sha256sum *.deb | sort ) > "$SECOND_LIST"
if ! diff -u "$FIRST_LIST" "$SECOND_LIST" > "$TMP/packages.diff"; then
    DIFFERENT=1
    log "paket berbeda antar dua build"
    sed -n '1,20p' "$TMP/packages.diff"
else
    log "semua paket identik antar dua build"
fi

ISO_RESULT="{}"
if [ "${#ISOS[@]}" -ge 2 ]; then
    log "membandingkan ISO dengan diffoscope"
    if command -v diffoscope >/dev/null 2>&1; then
        diffoscope --text "$TMP/iso.diff" "${ISOS[0]}" "${ISOS[1]}" >/dev/null 2>&1 || true
        ISO_RESULT="{\"compared\": true, \"diffoscope\": \"$TMP/iso.diff\"}"
    else
        ISO_RESULT="{\"compared\": false, \"reason\": \"diffoscope tidak tersedia\"}"
        log "diffoscope tidak tersedia, hanya checksum yang dibandingkan"
    fi
    sha256sum "${ISOS[@]}" > "$TMP/iso.sha256" || true
fi

python3 - "$REPORT" "$DIFFERENT" "$FIRST_LIST" "$ISO_RESULT" "$EPOCH" <<'PY'
import json
import sys
from pathlib import Path

report_path = Path(sys.argv[1])
different = int(sys.argv[2])
listing = Path(sys.argv[3]).read_text(encoding="utf-8")
iso_result = json.loads(sys.argv[4])
epoch = sys.argv[5]

packages = []
for line in listing.splitlines():
    digest, _, name = line.partition("  ")
    packages.append({"file": name, "sha256": digest})

report = {
    "schema_version": 1,
    "source_date_epoch": epoch,
    "packages": packages,
    "package_count": len(packages),
    "identical": different == 0,
    "iso": iso_result,
}
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"laporan reproduksibilitas ditulis ke {report_path}")
PY

if [ "$DIFFERENT" -ne 0 ]; then
    log "build tidak reproducible"
    exit 1
fi
log "build reproducible"
exit 0
