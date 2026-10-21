#!/usr/bin/env bash
# Static Cinnamon, XFCE, and LXQt integration verification plus a sandboxed
# accessibility helper test. No live desktop session is started.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$ROOT/scripts/check-desktop.py"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
HELPER="$ROOT/config/common/includes.chroot/usr/local/bin/arashios-accessibility"

run_helper() {
    env -i HOME="$TMP" PATH=/usr/bin:/bin XDG_CURRENT_DESKTOP=XFCE "$HELPER" "$@"
}

run_helper contrast on >/dev/null
grep -q '^gtk-theme-name=ArashiKage-HC$' "$TMP/.config/gtk-3.0/settings.ini"
grep -q 'ArashiKage-HC/gtk-4.0/gtk.css' "$TMP/.config/gtk-4.0/gtk.css"
grep -q '^theme=ArashiKage-HC$' "$TMP/.config/Kvantum/kvantum.kvconfig"
status_output="$(run_helper status)"
grep -q '^gtk-theme : ArashiKage-HC$' <<<"$status_output"

run_helper motion off >/dev/null
grep -q '^gtk-enable-animations=false$' "$TMP/.config/gtk-3.0/settings.ini"

run_helper contrast off >/dev/null
grep -q '^gtk-theme-name=ArashiKage$' "$TMP/.config/gtk-3.0/settings.ini"
grep -q '^gtk-enable-animations=false$' "$TMP/.config/gtk-3.0/settings.ini"
grep -q 'ArashiKage/gtk-4.0/gtk.css' "$TMP/.config/gtk-4.0/gtk.css"
grep -q '^theme=ArashiKage$' "$TMP/.config/Kvantum/kvantum.kvconfig"

printf 'Accessibility helper checks passed\n'
