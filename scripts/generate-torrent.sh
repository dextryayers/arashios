#!/usr/bin/env bash
# Generate torrent metadata for ArashiOS artifacts.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

if [ "$#" -lt 1 ]; then
    printf 'Pemakaian: %s <berkas-iso>\n' "$0" >&2
    exit 2
fi

ISO="$1"
if [ ! -f "$ISO" ]; then
    printf 'ERROR: ISO tidak ditemukan: %s\n' "$ISO" >&2
    exit 1
fi

if command -v mktorrent >/dev/null 2>&1; then
    mktorrent -a "udp://tracker.opentrackr.org:1337/announce" \
        -n "ArashiOS-$(basename "$ISO")" \
        -o "${ISO}.torrent" "$ISO"
    printf 'OK: torrent dibuat dengan mktorrent\n'
else
    printf 'WARN: mktorrent tidak tersedia, membuat manifest pengganti\n'
    sha256sum "$ISO" > "${ISO}.torrent.manifest"
    printf 'OK: manifest dibuat\n'
fi
