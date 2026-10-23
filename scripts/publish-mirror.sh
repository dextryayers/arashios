#!/usr/bin/env bash
# Publish ArashiOS artifacts to a mirror directory.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

DRY_RUN=0
MIRROR="${MIRROR_DIR:-$ROOT/build/mirror}"

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        -h|--help)
            printf 'Pemakaian: %s [--dry-run]\n' "$0"
            exit 0
            ;;
        *) printf 'ERROR: argumen tidak dikenal: %s\n' "$arg" >&2; exit 2 ;;
    esac
done

RELEASE_DIR="$ROOT/build/release-$ARASHIOS_VERSION"
if [ ! -d "$RELEASE_DIR" ]; then
    printf 'ERROR: direktori rilis belum ada. Jalankan prepare-release.sh dulu.\n' >&2
    exit 1
fi

if [ "$DRY_RUN" -eq 1 ]; then
    printf 'INFO: dry run, mirror target %s\n' "$MIRROR"
    printf 'INFO: berkas yang akan disalin:\n'
    find "$RELEASE_DIR" -maxdepth 1 -type f -printf '  %f\n'
    exit 0
fi

mkdir -p "$MIRROR/stable/$ARASHIOS_VERSION"
cp -a "$RELEASE_DIR"/. "$MIRROR/stable/$ARASHIOS_VERSION"/
ln -sfn "$ARASHIOS_VERSION" "$MIRROR/stable/current"

printf 'OK: artefak dipublikasikan ke %s\n' "$MIRROR"
