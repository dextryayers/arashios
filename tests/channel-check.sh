#!/usr/bin/env bash
# Check release channel configuration.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ERRORS=0
for channel in stable edge nightly; do
    if [ -f "$ROOT/config/channels/$channel.sources" ]; then
        printf 'OK:   %s.sources\n' "$channel"
    else
        printf 'FAIL: %s.sources hilang\n' "$channel" >&2
        ERRORS=$((ERRORS + 1))
    fi
done

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi
printf 'OK: kanal rilis valid\n'
