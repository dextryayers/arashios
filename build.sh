#!/usr/bin/env bash
# ArashiOS ISO builder.
# Pemakaian:
#   ./build.sh --edition cinnamon --arch amd64
#   ./build.sh --edition xfce --arch arm64 --version V1.10.21
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=versions.env
source "$ROOT/versions.env"

EDITION=""
ARCH=""
VERSION="$ARASHIOS_VERSION"
JOBS="$(nproc)"

usage() {
    cat <<EOF
Pemakaian: $0 --edition <cinnamon|xfce|lxqt> --arch <amd64|arm64|i386> [opsi]

Opsi:
  --edition NAME   Edisi desktop. Wajib.
  --arch NAME      Arsitektur target. Wajib.
  --version VER    Versi rilis. Default: $ARASHIOS_VERSION
  --jobs N         Paralelisme mksquashfs. Default: $JOBS
  -h, --help       Tampilkan bantuan ini.

Contoh:
  $0 --edition cinnamon --arch amd64
  $0 --edition lxqt --arch i386 --version V1.10.21
EOF
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

log() {
    printf '[arashios] %s\n' "$*"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --edition) EDITION="${2:-}"; shift 2 ;;
        --arch) ARCH="${2:-}"; shift 2 ;;
        --version) VERSION="${2:-}"; shift 2 ;;
        --jobs) JOBS="${2:-}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) die "Argumen tidak dikenal: $1" ;;
    esac
done

[ -n "$EDITION" ] || die "Opsi --edition wajib diisi."
[ -n "$ARCH" ] || die "Opsi --arch wajib diisi."

case " $SUPPORTED_EDITIONS " in
    *" $EDITION "*) ;;
    *) die "Edisi tidak didukung: $EDITION. Pilihan: $SUPPORTED_EDITIONS" ;;
esac

case " $SUPPORTED_ARCHES " in
    *" $ARCH "*) ;;
    *) die "Arsitektur tidak didukung: $ARCH. Pilihan: $SUPPORTED_ARCHES" ;;
esac

case "$VERSION" in
    V[0-9]*.[0-9]*.[0-9]*) ;;
    *) die "Format versi harus V<major>.<MM>.<DD>, contoh V1.10.21" ;;
esac

case "$ARCH:$EDITION" in
    amd64:cinnamon|arm64:xfce|i386:lxqt) SUFFIX="" ;;
    *) SUFFIX="-$EDITION" ;;
esac

case "$ARCH" in
    amd64) KERNEL_FLAVOUR="amd64"; BOOTLOADERS="syslinux,grub-efi" ;;
    arm64) KERNEL_FLAVOUR="arm64"; BOOTLOADERS="grub-efi" ;;
    i386)  KERNEL_FLAVOUR="686-pae"; BOOTLOADERS="syslinux,grub-efi" ;;
esac

for cmd in lb debootstrap xorriso mksquashfs; do
    command -v "$cmd" >/dev/null 2>&1 || die "Perintah '$cmd' tidak ditemukan. Jalankan scripts/check-env.sh."
done

WORK="$ROOT/build/${EDITION}-${ARCH}"
OUT="$ROOT/out"
LOG="$WORK/build.log"

rm -rf "$WORK"
mkdir -p "$WORK" "$OUT"

log "Menyiapkan konfigurasi live-build"
log "  edisi    : $EDITION"
log "  arsitektur: $ARCH"
log "  versi    : $VERSION"
log "  kernel   : $KERNEL_FLAVOUR"
log "  boot     : $BOOTLOADERS"

cd "$WORK"

LIVE_OPTS=(
    "boot=live"
    "components"
    "quiet"
    "splash"
    "username=arashi"
    "hostname=arashios"
    "locales=en_US.UTF-8"
    "keyboard-layouts=us"
    "timezone=UTC"
)

LB_ARGS=(
    --distribution "$DEBIAN_CODENAME"
    --architectures "$ARCH"
    --binary-images iso-hybrid
    --bootloaders "$BOOTLOADERS"
    --debian-installer none
    --archive-areas "main contrib non-free non-free-firmware"
    --linux-flavours "$KERNEL_FLAVOUR"
    --iso-application "$ISO_APPLICATION"
    --iso-publisher "$ISO_PUBLISHER"
    --iso-volume "$ISO_VOLUME"
    --hostname arashios
    --bootappend-live "${LIVE_OPTS[*]}"
    --apt-indices false
    --memtest none
    --zsync false
)

if [ -n "${APT_PROXY:-}" ]; then
    LB_ARGS+=(--apt-http-proxy "$APT_PROXY")
fi

lb config "${LB_ARGS[@]}"

log "Menerapkan overlay common dan edisi"
cp -a "$ROOT/config/common/." "$WORK/config/"
cp -a "$ROOT/config/editions/$EDITION/." "$WORK/config/"

printf '%s\n' "$EDITION" > "$WORK/config/includes.chroot/etc/arashios/edition"
printf '%s\n' "$VERSION" > "$WORK/config/includes.chroot/etc/arashios/version"
printf '%s\n' "$ARCH" > "$WORK/config/includes.chroot/etc/arashios/arch"

log "Build dimulai. Log: $LOG"
set +e
lb build 2>&1 | tee "$LOG"
BUILD_STATUS=${PIPESTATUS[0]}
set -e

if [ "$BUILD_STATUS" -ne 0 ]; then
    die "Build gagal dengan status $BUILD_STATUS. Periksa $LOG"
fi

ISO_SOURCE="$(find "$WORK" -maxdepth 1 -name '*.hybrid.iso' -print -quit)"
[ -n "$ISO_SOURCE" ] || die "ISO tidak ditemukan di $WORK"

ISO_TARGET="$OUT/ArashiOS-${ARCH}-${VERSION}${SUFFIX}.iso"
mv "$ISO_SOURCE" "$ISO_TARGET"

log "Menghitung checksum"
( cd "$OUT" && sha256sum "$(basename "$ISO_TARGET")" > "$(basename "$ISO_TARGET").sha256" )
( cd "$OUT" && sha512sum "$(basename "$ISO_TARGET")" > "$(basename "$ISO_TARGET").sha512" )

if [ -n "${MINISIGN_KEY:-}" ] && command -v minisign >/dev/null 2>&1; then
    log "Menandatangani artefak"
    minisign -S -s "$MINISIGN_KEY" -m "$ISO_TARGET" -x "$ISO_TARGET.sig"
fi

log "Selesai: $ISO_TARGET"
log "Ukuran : $(du -h "$ISO_TARGET" | cut -f1)"
