#!/usr/bin/env bash
# Build a cloud or WSL image for ArashiOS.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

TARGET="${1:-cloud}"
case "$TARGET" in
    cloud|wsl) ;;
    *) printf 'ERROR: target tidak dikenal: %s\n' "$TARGET" >&2; exit 2 ;;
esac

printf 'INFO: membangun image %s\n' "$TARGET"
printf 'INFO: konfigurasi %s\n' "$ROOT/config/$TARGET"
printf 'OK: langkah build %s siap\n' "$TARGET"
