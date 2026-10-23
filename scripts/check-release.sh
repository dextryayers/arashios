#!/usr/bin/env bash
# Run final release gates for ArashiOS.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

ERRORS=0

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    ERRORS=$((ERRORS + 1))
}

ok() {
    printf 'OK:   %s\n' "$*"
}

printf 'ArashiOS release check\n'
printf 'Root: %s\n\n' "$ROOT"

printf 'Dokumentasi:\n'
for file in \
    docs/RELEASE.md docs/MIRROR.md docs/CHANNELS.md docs/COMMUNITY.md \
    docs/MONITORING.md docs/HOTFIX.md docs/RC-PROCESS.md docs/FAQ.md; do
    if [ -f "$ROOT/$file" ]; then
        ok "$file"
    else
        fail "berkas hilang: $file"
    fi
done

printf '\nKonfigurasi:\n'
for dir in config/channels config/mirror config/sbc config/secureboot config/wayland config/cloud config/wsl config/rebase; do
    if [ -d "$ROOT/$dir" ]; then
        ok "$dir"
    else
        fail "direktori hilang: $dir"
    fi
done

printf '\nSkrip:\n'
for file in \
    scripts/prepare-release.sh scripts/publish-mirror.sh scripts/generate-torrent.sh \
    scripts/channel-switch.sh scripts/monitor-release.sh scripts/rc-check.sh; do
    if [ -x "$ROOT/$file" ]; then
        ok "$file"
    else
        fail "tidak executable: $file"
    fi
done

printf '\nKanal:\n'
for channel in stable edge nightly; do
    if [ -f "$ROOT/config/channels/$channel.sources" ]; then
        ok "$channel.sources"
    else
        fail "berkas sumber kanal hilang: $channel"
    fi
done

printf '\nArtefak rilis:\n'
if [ -d "$ROOT/out" ]; then
    iso_count="$(find "$ROOT/out" -maxdepth 1 -type f -name 'ArashiOS-*.iso' | wc -l | tr -d ' ')"
    printf 'INFO: %s artefak ISO ditemukan di out/\n' "$iso_count"
else
    printf 'INFO: direktori out/ belum ada\n'
fi

printf '\n'
if [ "$ERRORS" -gt 0 ]; then
    printf 'Status: GAGAL dengan %s masalah.\n' "$ERRORS" >&2
    exit 1
fi

printf 'Status: rilis siap diperiksa.\n'
