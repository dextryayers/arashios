#!/usr/bin/env bash
# Run all release candidate gates.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

run() {
    printf '\n=== %s ===\n' "$*"
    "$@"
}

run "$ROOT/scripts/check-docs.sh"
run "$ROOT/scripts/validate-config.sh"
run "$ROOT/scripts/check-release.sh"
run python3 "$ROOT/scripts/check-traceability.py"

printf '\nOK: semua gate kandidat rilis lulus\n'
