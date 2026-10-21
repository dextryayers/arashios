#!/usr/bin/env bash
# Build and verify the local arashios-branding package.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"
EXPECTED_VERSION="${ARASHIOS_PACKAGE_VERSION:-${ARASHIOS_VERSION#V}-1}"
DEB="$("$ROOT/scripts/build-branding-package.sh")"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() {
    printf 'FAIL  %s\n' "$*" >&2
    exit 1
}

pass() {
    printf 'PASS  %s\n' "$*"
}

[ -f "$DEB" ] || fail "package was not created"
pass "package exists"

for field in Package Version Architecture Maintainer Description; do
    value="$(dpkg-deb -f "$DEB" "$field" 2>/dev/null || true)"
    [ -n "$value" ] || fail "control field $field is empty"
    pass "control $field: $value"
done

[ "$(dpkg-deb -f "$DEB" Package)" = "arashios-branding" ] || fail "wrong package name"
[ "$(dpkg-deb -f "$DEB" Architecture)" = "all" ] || fail "branding package must be Architecture: all"
[ "$(dpkg-deb -f "$DEB" Version)" = "$EXPECTED_VERSION" ] || fail "wrong package version"
pass "control identity"

mkdir -p "$TMP/root" "$TMP/control"
dpkg-deb -x "$DEB" "$TMP/root"
dpkg-deb -e "$DEB" "$TMP/control"

required=(
    "usr/share/themes/ArashiKage/index.theme"
    "usr/share/themes/ArashiKage-HC/index.theme"
    "usr/share/themes/ArashiKage/gtk-3.0/gtk.css"
    "usr/share/themes/ArashiKage/gtk-4.0/gtk.css"
    "usr/share/themes/ArashiKage/cinnamon/cinnamon.css"
    "usr/share/themes/ArashiKage/xfwm4/title-1-active.png"
    "usr/share/themes/ArashiKage/openbox-3/themerc"
    "usr/share/themes/ArashiKage/metacity-1/metacity-theme-3.xml"
    "usr/share/Kvantum/ArashiKage/ArashiKage.kvconfig"
    "usr/share/Kvantum/ArashiKage/ArashiKage.svg"
    "usr/share/backgrounds/arashios/kage-sumi.png"
    "usr/share/backgrounds/arashios/kage-shuriken.png"
    "usr/share/backgrounds/arashios/kage-bamboo.png"
    "usr/share/backgrounds/arashios/kage-washi.png"
    "usr/share/backgrounds/arashios/kage-storm.png"
    "usr/share/icons/hicolor/256x256/apps/arashios.png"
    "usr/share/icons/hicolor/scalable/apps/arashios.svg"
    "usr/share/grub/themes/arashios/theme.txt"
    "usr/share/plymouth/themes/arashios/arashios.plymouth"
    "usr/share/plymouth/themes/arashios/logo.png"
    "usr/share/plymouth/themes/arashios/progress_box.png"
    "usr/share/plymouth/themes/arashios/progress_bar.png"
    "usr/share/doc/arashios-branding/copyright"
    "usr/share/doc/arashios-branding/NOTICE"
    "usr/share/doc/arashios-branding/CHANGELOG.md"
)
for path in "${required[@]}"; do
    [ -f "$TMP/root/$path" ] || fail "package lacks $path"
done
pass "required package files"
PAYLOAD_COUNT="$(dpkg-deb -c "$DEB" | awk '$1 !~ /^d/ { count++ } END { print count + 0 }')"
[ "$PAYLOAD_COUNT" -ge 200 ] || fail "package payload is unexpectedly small: $PAYLOAD_COUNT files"
pass "payload file count: $PAYLOAD_COUNT"

for variant in ArashiKage ArashiKage-HC; do
    count="$(find "$TMP/root/usr/share/themes/$variant/xfwm4" -name '*.png' -type f | wc -l)"
    [ "$count" -eq 70 ] || fail "$variant has $count XFWM PNG files"
done
pass "70 XFWM assets per theme"

# Every file in md5sums must exist in the extracted package and match.
if [ ! -s "$TMP/control/md5sums" ]; then
    fail "md5sums is missing"
fi
(
    cd "$TMP/root"
    md5sum -c "$TMP/control/md5sums" --quiet
) || fail "package md5sums verification failed"
pass "md5sums"

# Parse every XML, SVG, and theme index in the extracted payload.
python3 - "$TMP/root" <<'PY'
import configparser
import sys
from pathlib import Path
from xml.etree import ElementTree

root = Path(sys.argv[1])
for path in sorted(root.rglob("*")):
    if path.suffix.lower() in {".xml", ".svg"}:
        ElementTree.parse(path)
for variant in ("ArashiKage", "ArashiKage-HC"):
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(root / "usr/share/themes" / variant / "index.theme", encoding="utf-8")
    assert parser.get("Desktop Entry", "Name") == variant
    kv = root / "usr/share/Kvantum" / variant / f"{variant}.kvconfig"
    assert "[GeneralColors]" in kv.read_text(encoding="utf-8")
PY
pass "XML, SVG, index, and Kvantum payload parsing"

# Local package installation simulation with dpkg-deb extraction and no scripts.
[ ! -d "$TMP/root/DEBIAN" ] || fail "payload contains DEBIAN directory"
if find "$TMP/root" -type f -perm /022 -print -quit | grep -q .; then
    fail "package contains a world-writable file"
fi
pass "payload permissions"

SIZE="$(stat -c %s "$DEB")"
[ "$SIZE" -lt 2097152 ] || fail "package is unexpectedly large: $SIZE bytes"
pass "package size: $SIZE bytes"

# The package must be byte-for-byte reproducible when SOURCE_DATE_EPOCH is set.
FIRST_HASH="$(sha256sum "$DEB" | cut -d' ' -f1)"
SECOND_DEB="$("$ROOT/scripts/build-branding-package.sh")"
SECOND_HASH="$(sha256sum "$SECOND_DEB" | cut -d' ' -f1)"
[ "$FIRST_HASH" = "$SECOND_HASH" ] || fail "package is not reproducible"
pass "reproducible package: $FIRST_HASH"

printf 'Branding package checks passed\n'
