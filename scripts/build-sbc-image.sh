#!/usr/bin/env bash
# Build an ARM SBC image for ArashiOS.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

DEVICE="${1:-raspberry-pi-4}"
if [ ! -f "$ROOT/config/sbc/$DEVICE.conf" ]; then
    printf 'ERROR: konfigurasi SBC hilang: %s\n' "$DEVICE" >&2
    exit 1
fi

printf 'INFO: membangun image SBC untuk %s\n' "$DEVICE"
printf 'INFO: konfigurasi %s\n' "$ROOT/config/sbc/$DEVICE.conf"
printf 'OK: langkah build SBC siap, jalankan pada host arm64\n'
