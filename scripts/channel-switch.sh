#!/usr/bin/env bash
# Switch the configured APT channel for ArashiOS.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

CHANNEL="${1:-stable}"
case "$CHANNEL" in
    stable|edge|nightly) ;;
    *) printf 'ERROR: kanal tidak dikenal: %s\n' "$CHANNEL" >&2; exit 2 ;;
esac

if [ ! -f "$ROOT/config/channels/$CHANNEL.sources" ]; then
    printf 'ERROR: berkas sumber kanal hilang: %s\n' "$CHANNEL" >&2
    exit 1
fi

printf 'INFO: kanal target %s\n' "$CHANNEL"
printf 'INFO: salin config/channels/%s.sources ke /etc/apt/sources.list.d/\n' "$CHANNEL"
printf 'OK: instruksi perpindahan kanal siap\n'
