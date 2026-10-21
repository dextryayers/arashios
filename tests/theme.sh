#!/usr/bin/env bash
# Static theme, wallpaper, icon, and boot asset verification.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/scripts/check-theme.py"
