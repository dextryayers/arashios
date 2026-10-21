#!/usr/bin/env bash
# Generate Kage theme output from design tokens.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT/scripts/generate-tokens.py"
"$ROOT/scripts/generate-theme.py" "$@"
