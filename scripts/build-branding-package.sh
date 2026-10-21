#!/usr/bin/env bash
# Build the local arashios-branding package from generated theme and assets.
# Prints the absolute .deb path on stdout. Diagnostics go to stderr.
set -Eeuo pipefail
export TZ=UTC

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

VERSION_NUM="${ARASHIOS_VERSION#V}"
PKG_VERSION="${ARASHIOS_PACKAGE_VERSION:-${VERSION_NUM}-1}"
EPOCH="${SOURCE_DATE_EPOCH:-0}"
export SOURCE_DATE_EPOCH="$EPOCH"
STAGE="$ROOT/build/branding-package"
PKGDIR="$ROOT/build/packages"
DEB="$PKGDIR/arashios-branding_${PKG_VERSION}_all.deb"

log() {
    printf '[branding-package] %s\n' "$*" >&2
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

command -v dpkg-deb >/dev/null 2>&1 || die "dpkg-deb tidak ditemukan."
[ -d "$ROOT/build/theme/themes/ArashiKage" ] || \
    die "tema belum dihasilkan. Jalankan ./scripts/generate-theme.sh."
[ -f "$ROOT/build/theme/manifest.json" ] || die "manifest tema hilang."
[ -f "$ROOT/build/tokens/tokens.css" ] || die "token CSS hilang."

rm -rf "$STAGE"
mkdir -p \
    "$STAGE/DEBIAN" \
    "$STAGE/usr/share/themes" \
    "$STAGE/usr/share/Kvantum" \
    "$STAGE/usr/share/backgrounds/arashios" \
    "$STAGE/usr/share/arashios/branding/wallpaper" \
    "$STAGE/usr/share/arashios/theme" \
    "$STAGE/usr/share/grub/themes/arashios" \
    "$STAGE/usr/share/plymouth/themes/arashios" \
    "$STAGE/usr/share/icons/hicolor/scalable/apps" \
    "$STAGE/usr/share/doc/arashios-branding"

cp -a "$ROOT/build/theme/themes/ArashiKage" "$STAGE/usr/share/themes/"
cp -a "$ROOT/build/theme/themes/ArashiKage-HC" "$STAGE/usr/share/themes/"
cp -a "$ROOT/build/theme/Kvantum/ArashiKage" "$STAGE/usr/share/Kvantum/"
cp -a "$ROOT/build/theme/Kvantum/ArashiKage-HC" "$STAGE/usr/share/Kvantum/"
install -m644 "$ROOT/build/theme/manifest.json" \
    "$STAGE/usr/share/arashios/theme/theme-manifest.json"
install -m644 "$ROOT/build/tokens/tokens.css" "$STAGE/usr/share/arashios/theme/tokens.css"
install -m644 "$ROOT/build/tokens/kage.qss" "$STAGE/usr/share/arashios/theme/kage.qss"
install -m644 "$ROOT/build/tokens/tokens.resolved.json" \
    "$STAGE/usr/share/arashios/theme/tokens.resolved.json"

for wallpaper in "$ROOT"/branding/wallpaper/kage-*.png; do
    install -m644 "$wallpaper" "$STAGE/usr/share/backgrounds/arashios/$(basename "$wallpaper")"
done
for source in "$ROOT"/branding/wallpaper/kage-*.svg; do
    install -m644 "$source" "$STAGE/usr/share/arashios/branding/wallpaper/$(basename "$source")"
done

install -m644 "$ROOT/branding/logo/arashios-mark.svg" \
    "$STAGE/usr/share/icons/hicolor/scalable/apps/arashios.svg"
install -m644 "$ROOT/branding/logo/arashios-wordmark.svg" \
    "$STAGE/usr/share/arashios/branding/arashios-wordmark.svg"
install -m644 "$ROOT/branding/logo/arashios-mark-dark.svg" \
    "$STAGE/usr/share/arashios/branding/arashios-mark-dark.svg"
install -m644 "$ROOT/branding/logo/arashios-mark-mono.svg" \
    "$STAGE/usr/share/arashios/branding/arashios-mark-mono.svg"
install -m644 "$ROOT/branding/logo/arashios-favicon.svg" \
    "$STAGE/usr/share/arashios/branding/arashios-favicon.svg"
install -m644 "$ROOT/branding/logo/arashios-favicon.ico" \
    "$STAGE/usr/share/arashios/branding/arashios-favicon.ico"
for png in "$ROOT"/branding/logo/hicolor/*/apps/arashios.png; do
    rel="${png#"$ROOT/branding/logo/"}"
    install -Dm644 "$png" "$STAGE/usr/share/icons/$rel"
done

install -m644 "$ROOT/branding/grub/theme.txt" "$STAGE/usr/share/grub/themes/arashios/theme.txt"
for png in "$ROOT"/branding/grub/*.png; do
    install -m644 "$png" "$STAGE/usr/share/grub/themes/arashios/$(basename "$png")"
done
install -m644 "$ROOT/branding/plymouth/arashios.plymouth" \
    "$STAGE/usr/share/plymouth/themes/arashios/arashios.plymouth"
install -m644 "$ROOT/branding/plymouth/arashios.script" \
    "$STAGE/usr/share/plymouth/themes/arashios/arashios.script"
install -m644 "$ROOT/branding/plymouth/logo.png" \
    "$STAGE/usr/share/plymouth/themes/arashios/logo.png"
install -m644 "$ROOT/branding/plymouth/progress_box.png" \
    "$STAGE/usr/share/plymouth/themes/arashios/progress_box.png"
install -m644 "$ROOT/branding/plymouth/progress_bar.png" \
    "$STAGE/usr/share/plymouth/themes/arashios/progress_bar.png"
install -m644 "$ROOT/branding/boot/splash.png" \
    "$STAGE/usr/share/plymouth/themes/arashios/splash.png"
install -m644 "$ROOT/branding/boot/grub-splash.png" \
    "$STAGE/usr/share/grub/themes/arashios/grub-splash.png"

install -m644 "$ROOT/docs/LEGAL.md" "$STAGE/usr/share/doc/arashios-branding/copyright"
install -m644 "$ROOT/docs/LEGAL.md" "$STAGE/usr/share/doc/arashios-branding/LEGAL.md"
install -m644 "$ROOT/LICENSE" "$STAGE/usr/share/doc/arashios-branding/LICENSE"
install -m644 "$ROOT/NOTICE" "$STAGE/usr/share/doc/arashios-branding/NOTICE"
install -m644 "$ROOT/CHANGELOG.md" "$STAGE/usr/share/doc/arashios-branding/CHANGELOG.md"

INSTALLED_SIZE="$(du -sk "$STAGE" | cut -f1)"
cat > "$STAGE/DEBIAN/control" <<EOF
Package: arashios-branding
Version: ${PKG_VERSION}
Section: x11
Priority: optional
Architecture: all
Maintainer: ArashiOS Project <maintainers@arashios.example>
Installed-Size: ${INSTALLED_SIZE}
Depends: gtk2-engines-murrine, qt5-style-kvantum, qt5ct, papirus-icon-theme, bibata-cursor-theme, fonts-inter, fonts-jetbrains-mono
Recommends: cinnamon | xfce4 | lxqt-core
Description: ArashiOS Kage branding, desktop themes, and boot assets
 The package installs the ArashiKage GTK, Cinnamon, XFWM, Openbox, and
 Kvantum themes plus the Kage wallpaper, icon, GRUB, and Plymouth assets.
 It is built locally from the pinned design tokens during each image build.
EOF

(
    cd "$STAGE"
    find . -type f ! -path './DEBIAN/*' -printf '%P\n' | sort | \
        while IFS= read -r file; do
            printf '%s  %s\n' "$(md5sum "$file" | cut -d' ' -f1)" "$file"
        done > DEBIAN/md5sums
)

find "$STAGE" -type d -exec chmod 0755 {} +
find "$STAGE" -type f ! -path "$STAGE/DEBIAN/*" -exec chmod 0644 {} +
find "$STAGE" -type f -path "$STAGE/DEBIAN/*" -exec chmod 0644 {} +
chmod 0755 "$STAGE/DEBIAN"
find "$STAGE" -exec touch -h -d "@${EPOCH}" {} +

mkdir -p "$PKGDIR"
rm -f "$DEB"
if ! dpkg-deb --root-owner-group --build "$STAGE" "$DEB" >/dev/null 2>&1; then
    dpkg-deb --root-owner-group --build "$STAGE" "$DEB" >&2
    die "pembuatan paket branding gagal."
fi

log "paket ditulis: ${DEB#"$ROOT/"}"
printf '%s\n' "$DEB"
