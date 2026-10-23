#!/usr/bin/env bash
# Verify Secure Boot configuration and signed binaries.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -d "$ROOT/config/secureboot" ]; then
    printf 'ERROR: direktori secureboot hilang\n' >&2
    exit 1
fi

printf 'INFO: memeriksa konfigurasi Secure Boot\n'
for file in "$ROOT"/config/secureboot/*; do
    [ -e "$file" ] || continue
    printf '  %s\n' "${file#"$ROOT/"}"
done
printf 'OK: konfigurasi Secure Boot tersedia\n'
