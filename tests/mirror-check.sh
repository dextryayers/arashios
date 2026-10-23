#!/usr/bin/env bash
# Check mirror structure.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

MIRROR="${MIRROR_DIR:-$ROOT/build/mirror}"
ERRORS=0

if [ ! -d "$MIRROR" ]; then
    printf 'INFO: mirror belum ada, pemeriksaan dilewati\n'
    exit 0
fi

if [ -L "$MIRROR/stable/current" ]; then
    printf 'OK:   symlink current\n'
else
    printf 'FAIL: symlink current hilang\n' >&2
    ERRORS=$((ERRORS + 1))
fi

if [ -f "$MIRROR/stable/$ARASHIOS_VERSION/SHA256SUMS" ]; then
    printf 'OK:   SHA256SUMS\n'
else
    printf 'FAIL: SHA256SUMS hilang\n' >&2
    ERRORS=$((ERRORS + 1))
fi

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi
printf 'OK: mirror valid\n'
