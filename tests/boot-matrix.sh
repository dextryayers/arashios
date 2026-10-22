#!/usr/bin/env bash
# ArashiOS boot test matrix.
#
# The matrix boots every released ISO in the applicable firmware mode, checks
# the artifacts, and writes one report per artifact. Combinations without a
# built ISO are reported as skipped so the same script runs in CI and on the
# release host.
#
# Usage:
#   tests/boot-matrix.sh
#   tests/boot-matrix.sh --out out
#   tests/boot-matrix.sh --only amd64:cinnamon
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

OUT_DIR="$ROOT/out"
REPORT_DIR="$ROOT/build/boot-matrix"
ONLY=""
SKIPPED=0
PASSED=0
FAILED=0

usage() {
    cat <<'EOF'
Pemakaian: tests/boot-matrix.sh [opsi]

Opsi:
  --out DIR      Direktori artefak ISO. Default: out.
  --only COMBO   Uji satu kombinasi, contoh amd64:cinnamon.
  -h, --help     Tampilkan bantuan ini.
EOF
}

log() {
    printf '[boot-matrix] %s\n' "$*"
}

fail() {
    printf 'FAIL  %s\n' "$*" >&2
    FAILED=$((FAILED + 1))
}

pass() {
    printf 'PASS  %s\n' "$*"
    PASSED=$((PASSED + 1))
}

skip() {
    printf 'SKIP  %s\n' "$*"
    SKIPPED=$((SKIPPED + 1))
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --out) OUT_DIR="${2:-}"; shift 2 ;;
        --only) ONLY="${2:-}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'ERROR: argumen tidak dikenal: %s\n' "$1" >&2; exit 2 ;;
    esac
done

mkdir -p "$REPORT_DIR"

command -v qemu-system-x86_64 >/dev/null 2>&1 || log "qemu-system-x86_64 tidak tersedia"

log "matriks boot untuk kombinasi: $SUPPORTED_COMBINATIONS"

for combo in $SUPPORTED_COMBINATIONS; do
    arch="${combo%%:*}"
    edition="${combo#*:}"
    if [ -n "$ONLY" ] && [ "$combo" != "$ONLY" ]; then
        continue
    fi

    default_var="DEFAULT_EDITION_${arch^^}"
    if [ "$edition" = "${!default_var}" ]; then
        suffix=""
    else
        suffix="-$edition"
    fi
    iso="$OUT_DIR/ArashiOS-$arch-$ARASHIOS_VERSION$suffix.iso"

    if [ ! -f "$iso" ]; then
        skip "$combo: ISO belum dibangun ($iso)"
        continue
    fi

    if ! "$ROOT/tests/verify-artifact.sh" "$iso" >"$REPORT_DIR/verify-$arch-$edition.log" 2>&1; then
        fail "$combo: verifikasi artefak gagal, log di verify-$arch-$edition.log"
        continue
    fi
    pass "$combo: artefak valid"

    if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
        skip "$combo: QEMU tidak tersedia"
        continue
    fi
    if [ "$arch" = "arm64" ]; then
        skip "$combo: boot arm64 membutuhkan runner arm64"
        continue
    fi

    for mode in uefi bios; do
        if [ "$arch" = "i386" ] && [ "$mode" = "uefi" ]; then
            skip "$combo: UEFI tidak berlaku untuk i386"
            continue
        fi
        log "$combo: boot $mode"
        if "$ROOT/tests/qemu-boot.sh" "$iso" "$mode" 120 \
            >"$REPORT_DIR/boot-$arch-$edition-$mode.log" 2>&1; then
            pass "$combo: boot $mode"
        else
            fail "$combo: boot $mode gagal, log di boot-$arch-$edition-$mode.log"
        fi
    done
done

printf '\nRingkasan: %s lulus, %s gagal, %s dilewati.\n' "$PASSED" "$FAILED" "$SKIPPED"
[ "$FAILED" -eq 0 ]
