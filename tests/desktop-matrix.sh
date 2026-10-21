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

# Verify that the Cinnamon window manager theme is switched together with the
# GTK and Cinnamon shell themes, without requiring a live desktop schema.
FAKE_BIN="$TMP/fake-bin"
FAKE_HOME="$TMP/fake-home"
GSETTINGS_LOG="$TMP/gsettings.log"
mkdir -p "$FAKE_BIN" "$FAKE_HOME"
cat > "$FAKE_BIN/gsettings" <<'EOF'
#!/usr/bin/env bash
set -eu
case "${1:-}" in
    list-schemas)
        printf '%s\n' \
            org.cinnamon.desktop.interface \
            org.cinnamon.theme \
            org.cinnamon.desktop.wm.preferences \
            org.gnome.desktop.interface
        ;;
    get)
        case "${2:-}:${3:-}" in
            org.cinnamon.desktop.interface:enable-animations) printf 'true\n' ;;
            org.cinnamon.desktop.interface:gtk-theme) printf "'ArashiKage'\n" ;;
            *) printf "'ArashiKage'\n" ;;
        esac
        ;;
    set)
        printf '%s\n' "$*" >> "$GSETTINGS_LOG"
        ;;
esac
EOF
chmod +x "$FAKE_BIN/gsettings"
: > "$GSETTINGS_LOG"
env -i HOME="$FAKE_HOME" PATH="$FAKE_BIN:/usr/bin:/bin" \
    XDG_CURRENT_DESKTOP=Cinnamon GSETTINGS_LOG="$GSETTINGS_LOG" \
    "$HELPER" contrast on >/dev/null
grep -qx 'set org.cinnamon.desktop.wm.preferences theme ArashiKage-HC' "$GSETTINGS_LOG"
env -i HOME="$FAKE_HOME" PATH="$FAKE_BIN:/usr/bin:/bin" \
    XDG_CURRENT_DESKTOP=Cinnamon GSETTINGS_LOG="$GSETTINGS_LOG" \
    "$HELPER" contrast off >/dev/null
grep -qx 'set org.cinnamon.desktop.wm.preferences theme ArashiKage' "$GSETTINGS_LOG"

printf 'Accessibility helper checks passed\n'
