#!/usr/bin/env bash
# Check release artifacts and their verification files.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

ERRORS=0

if [ ! -d "$ROOT/out" ]; then
    printf 'INFO: direktori out/ belum ada, pemeriksaan dilewati\n'
    exit 0
fi

for iso in "$ROOT"/out/ArashiOS-*.iso; do
    [ -f "$iso" ] || continue
    base="$(basename "$iso")"
    if [ -f "$iso.sha256" ]; then
        printf 'OK:   checksum SHA-256 %s\n' "$base"
    else
        printf 'FAIL: checksum SHA-256 hilang %s\n' "$base" >&2
        ERRORS=$((ERRORS + 1))
    fi
    if [ -f "$iso.sbom.json" ]; then
        printf 'OK:   SBOM %s\n' "$base"
    else
        printf 'FAIL: SBOM hilang %s\n' "$base" >&2
        ERRORS=$((ERRORS + 1))
    fi
done

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi
printf 'OK: matriks rilis selesai\n'
