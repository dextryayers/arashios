#!/usr/bin/env bash
# Validate live-build configuration for every supported architecture and edition.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

LOG="$(mktemp)"
trap 'rm -f "$LOG"' EXIT

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

if ! command -v lb >/dev/null 2>&1; then
    die "Perintah 'lb' tidak ditemukan. Pasang live-build atau jalankan scripts/check-env.sh."
fi

count=0
for combo in $SUPPORTED_COMBINATIONS; do
    arch="${combo%%:*}"
    edition="${combo#*:}"
    config="$ROOT/build/${edition}-${arch}/config"

    printf '[matrix] %s\n' "$combo"
    if ! "$ROOT/build.sh" --edition "$edition" --arch "$arch" --dry-run >"$LOG" 2>&1; then
        tail -40 "$LOG" >&2
        die "dry-run gagal untuk $combo"
    fi

    [ -f "$config/package-lists/00-base.list.chroot" ] || die "package list dasar hilang untuk $combo"
    [ -f "$config/includes.chroot/etc/os-release" ] || die "os-release hilang untuk $combo"
    [ -f "$config/includes.chroot/etc/arashios/build-info" ] || die "build-info hilang untuk $combo"
    [ -f "$config/includes.chroot/etc/lightdm/lightdm.conf.d/50-arashios.conf" ] || die "konfigurasi LightDM hilang untuk $combo"
    branding_deb="$config/packages.chroot/arashios-branding_${ARASHIOS_VERSION#V}-1_all.deb"
    [ -f "$branding_deb" ] || die "paket branding hilang untuk $combo"
    [ -f "$config/bootloaders/grub-pc/splash.png" ] || die "splash GRUB hilang untuk $combo"
    [ -f "$config/bootloaders/grub-pc/live-theme/theme.txt" ] || die "tema GRUB live hilang untuk $combo"
    [ -f "$config/bootloaders/grub-pc/live-theme/select_c.png" ] || die "pixmap pilihan GRUB hilang untuk $combo"
    grep -q 'ARASHIOS / KAGE' "$config/bootloaders/grub-pc/live-theme/theme.txt" || \
        die "tema GRUB live bukan Kage untuk $combo"
    grep -q 'desktop-image: "../splash.png"' "$config/bootloaders/grub-pc/live-theme/theme.txt" || \
        die "latar tema GRUB live salah untuk $combo"
    [ -f "$config/bootloaders/syslinux_common/splash.png" ] || die "splash syslinux hilang untuk $combo"
    [ -f "$config/includes.chroot/etc/gtk-3.0/settings.ini" ] || die "konfigurasi GTK3 hilang untuk $combo"
    [ -f "$config/includes.chroot/etc/xdg/mimeapps.list" ] || die "mimeapps.list hilang untuk $combo"
    grep -q '^gtk-theme-name=ArashiKage$' "$config/includes.chroot/etc/gtk-3.0/settings.ini" || \
        die "tema GTK3 bukan ArashiKage untuk $combo"

    [ -f "$config/includes.chroot/usr/share/arashios/toolstack/catalog.json" ] || \
        die "katalog toolstack hilang untuk $combo"
    [ -f "$config/includes.chroot/usr/share/arashios/toolchain/catalog.json" ] || \
        die "katalog toolchain hilang untuk $combo"
    [ -f "$config/includes.chroot/usr/share/arashios/labs.json" ] || die "katalog lab hilang untuk $combo"
    [ -f "$config/includes.chroot/usr/local/bin/arashios-arsenal" ] || die "Arsenal hilang untuk $combo"
    [ -f "$config/includes.chroot/usr/local/bin/arashios-toolchain" ] || die "toolchain CLI hilang untuk $combo"
    [ -f "$config/includes.chroot/usr/local/bin/arashios-lab" ] || die "lab CLI hilang untuk $combo"
    [ -f "$config/includes.chroot/usr/share/wordlists/arashios/manifest.json" ] || \
        die "manifest wordlist hilang untuk $combo"
    [ -f "$config/includes.chroot/etc/containers/containers.conf" ] || die "konfigurasi container hilang untuk $combo"
    [ -f "$config/includes.chroot/usr/share/doc/arashios/TOOLSTACK.md" ] || die "dokumen toolstack hilang untuk $combo"
    grep -q '"T0"' "$config/includes.chroot/usr/share/arashios/toolstack/catalog.json" || \
        die "katalog toolstack tidak memuat tier T0 untuk $combo"

    grep -q '^ID=arashios$' "$config/includes.chroot/etc/os-release" || die "ID os-release salah untuk $combo"
    grep -q "^ARASHIOS_ARCH=$arch$" "$config/includes.chroot/etc/arashios/build-info" || die "arsitektur build-info salah untuk $combo"
    grep -q "^ARASHIOS_EDITION=$edition$" "$config/includes.chroot/etc/arashios/build-info" || die "edisi build-info salah untuk $combo"
    grep -q "^user-session=$edition$" "$config/includes.chroot/etc/lightdm/lightdm.conf.d/50-arashios.conf" || die "sesi LightDM salah untuk $combo"

    case "$arch" in
        amd64)
            grep -q '^LB_BOOTLOADERS="syslinux grub-efi"$' "$config/binary" || die "bootloader amd64 salah"
            grep -q '^LB_LINUX_FLAVOURS_WITH_ARCH="amd64"$' "$config/chroot" || die "kernel amd64 salah"
            ;;
        arm64)
            grep -q '^LB_BOOTLOADERS="grub-efi"$' "$config/binary" || die "bootloader arm64 salah"
            grep -q '^LB_LINUX_FLAVOURS_WITH_ARCH="arm64"$' "$config/chroot" || die "kernel arm64 salah"
            ;;
        i386)
            grep -q '^LB_BOOTLOADERS="syslinux"$' "$config/binary" || die "bootloader i386 salah"
            grep -q '^LB_LINUX_FLAVOURS_WITH_ARCH="686-pae"$' "$config/chroot" || die "kernel i386 salah"
            ;;
    esac

    count=$((count + 1))
    printf 'OK:   %s\n' "$combo"
done

printf 'OK: %d kombinasi konfigurasi valid.\n' "$count"
