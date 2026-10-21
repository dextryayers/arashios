#!/usr/bin/env bash
# ArashiOS ISO builder.
# Pemakaian:
#   ./build.sh --edition cinnamon --arch amd64
#   ./build.sh --edition xfce --arch arm64 --version V1.10.21
#   ./build.sh --edition xfce --arch amd64 --dry-run
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=versions.env
source "$ROOT/versions.env"

export PATH="$PATH:/usr/sbin:/sbin"

EDITION=""
ARCH=""
VERSION="$ARASHIOS_VERSION"
JOBS="$(nproc)"
DRY_RUN=0

usage() {
    cat <<EOF
Pemakaian: $0 --edition <cinnamon|xfce|lxqt> --arch <amd64|arm64|i386> [opsi]

Opsi:
  --edition NAME   Edisi desktop. Wajib.
  --arch NAME      Arsitektur target. Wajib.
  --version VER    Versi rilis. Default: $ARASHIOS_VERSION
  --jobs N         Paralelisme mksquashfs. Default: $JOBS
  --dry-run        Siapkan konfigurasi live-build tanpa membangun ISO.
  -h, --help       Tampilkan bantuan ini.

Contoh:
  $0 --edition cinnamon --arch amd64
  $0 --edition lxqt --arch i386 --version V1.10.21
  $0 --edition xfce --arch amd64 --dry-run
EOF
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

log() {
    printf '[arashios] %s\n' "$*"
}

if [ "$(id -u)" -eq 0 ]; then
    log "Peringatan: build dijalankan sebagai root. Jalankan sebagai user biasa jika memungkinkan."
fi

while [ "$#" -gt 0 ]; do
    case "$1" in
        --edition) EDITION="${2:-}"; shift 2 ;;
        --arch) ARCH="${2:-}"; shift 2 ;;
        --version) VERSION="${2:-}"; shift 2 ;;
        --jobs) JOBS="${2:-}"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
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
    V[0-9]*.[0-9][0-9].[0-9][0-9]) ;;
    *) die "Format versi harus V<major>.<MM>.<DD>, contoh V1.10.21" ;;
esac

case "$JOBS" in
    ''|*[!0-9]*) die "--jobs harus bilangan bulat positif." ;;
esac
[ "$JOBS" -ge 1 ] || die "--jobs harus minimal 1."

if [ -n "${SOURCE_DATE_EPOCH:-}" ]; then
    case "$SOURCE_DATE_EPOCH" in
        *[!0-9]*) die "SOURCE_DATE_EPOCH harus bilangan bulat Unix timestamp." ;;
    esac
fi

VERSION_NUM="${VERSION#V}"
ISO_VOLUME="${ISO_VOLUME_PREFIX}_$(printf '%s' "$VERSION_NUM" | tr '.' '_' | tr '[:lower:]' '[:upper:]')"
[ "${#ISO_VOLUME}" -le 32 ] || die "Volume ID melebihi 32 karakter: $ISO_VOLUME"

case "$ARCH:$EDITION" in
    amd64:cinnamon|arm64:xfce|i386:lxqt) SUFFIX="" ;;
    *) SUFFIX="-$EDITION" ;;
esac

case "$ARCH" in
    amd64) KERNEL_FLAVOUR="amd64"; BOOTLOADERS="syslinux,grub-efi" ;;
    arm64) KERNEL_FLAVOUR="arm64"; BOOTLOADERS="grub-efi" ;;
    i386)  KERNEL_FLAVOUR="686-pae"; BOOTLOADERS="syslinux" ;;
esac

require_cmd() {
    local cmd
    for cmd in "$@"; do
        command -v "$cmd" >/dev/null 2>&1 || \
            die "Perintah '$cmd' tidak ditemukan. Jalankan scripts/check-env.sh."
    done
}

if [ "$DRY_RUN" -eq 1 ]; then
    require_cmd lb
else
    require_cmd lb debootstrap xorriso mksquashfs
    case ",$BOOTLOADERS," in
        *,syslinux,*) require_cmd isohybrid ;;
    esac
    case ",$BOOTLOADERS," in
        *,grub-efi,*) require_cmd grub-mkimage mcopy mkfs.vfat ;;
    esac
fi

WORK="$ROOT/build/${EDITION}-${ARCH}"
OUT="$ROOT/out"
LOG="$WORK/build.log"

rm -rf "$WORK"
mkdir -p "$WORK" "$OUT"

log "Menyiapkan konfigurasi live-build"
log "  edisi     : $EDITION"
log "  arsitektur: $ARCH"
log "  versi     : $VERSION"
log "  kernel    : $KERNEL_FLAVOUR"
log "  boot      : $BOOTLOADERS"
log "  volume    : $ISO_VOLUME"
log "  jobs      : $JOBS"
log "  dry-run   : $DRY_RUN"

cd "$WORK"

LIVE_OPTS=(
    "boot=live"
    "components"
    "quiet"
    "splash"
    "console=tty0"
    "console=ttyS0,115200"
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

if [ -n "${DEBIAN_SNAPSHOT:-}" ]; then
    SNAPSHOT_BASE="http://snapshot.debian.org/archive/debian/${DEBIAN_SNAPSHOT}"
    LB_ARGS+=(
        --mirror-bootstrap "$SNAPSHOT_BASE"
        --mirror-chroot "$SNAPSHOT_BASE"
        --mirror-binary "$SNAPSHOT_BASE"
    )
    log "Snapshot Debian: $SNAPSHOT_BASE"
fi

if [ -n "${APT_PROXY:-}" ]; then
    LB_ARGS+=(--apt-http-proxy "$APT_PROXY")
    log "APT proxy: $APT_PROXY"
fi

lb config "${LB_ARGS[@]}"

log "Menerapkan overlay common, edisi, dan arsitektur"
cp -a "$ROOT/config/common/." "$WORK/config/"
cp -a "$ROOT/config/editions/$EDITION/." "$WORK/config/"

if [ -d "$ROOT/config/arches/$ARCH" ]; then
    cp -a "$ROOT/config/arches/$ARCH/." "$WORK/config/"
fi

INCLUDES="$WORK/config/includes.chroot"
mkdir -p \
    "$INCLUDES/etc/arashios" \
    "$INCLUDES/usr/share/arashios/theme" \
    "$INCLUDES/usr/share/arashios/branding" \
    "$INCLUDES/usr/share/backgrounds/arashios" \
    "$INCLUDES/usr/share/grub/themes/arashios" \
    "$INCLUDES/usr/share/plymouth/themes/arashios" \
    "$INCLUDES/usr/share/icons/hicolor/scalable/apps" \
    "$INCLUDES/usr/share/doc/arashios" \
    "$INCLUDES/usr/local/bin"

printf '%s\n' "$EDITION" > "$INCLUDES/etc/arashios/edition"
printf '%s\n' "$VERSION" > "$INCLUDES/etc/arashios/version"
printf '%s\n' "$ARCH" > "$INCLUDES/etc/arashios/arch"

GIT_COMMIT="$(git -c safe.directory="$ROOT" -C "$ROOT" rev-parse --short HEAD 2>/dev/null || printf 'unknown')"
if [ -n "${SOURCE_DATE_EPOCH:-}" ]; then
    BUILD_DATE="$(date -u -d "@${SOURCE_DATE_EPOCH}" +%Y-%m-%dT%H:%M:%SZ)"
else
    BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi
HOST_OS="$(grep -m1 '^PRETTY_NAME=' /etc/os-release 2>/dev/null | cut -d= -f2- | tr -d '"' || true)"
[ -n "$HOST_OS" ] || HOST_OS="unknown"
HOST_KERNEL="$(uname -r)"
HOST_ARCH="$(uname -m)"
LB_VERSION="$(lb --version 2>/dev/null | head -1 || printf 'unknown')"
CONFIG_HASH="$(
    cd "$ROOT" && find config branding versions.env -type f -print0 |
        sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1
)"

cat > "$INCLUDES/etc/arashios/build-info" <<EOF
ARASHIOS_VERSION=$VERSION
ARASHIOS_CODENAME=$ARASHIOS_CODENAME
ARASHIOS_EDITION=$EDITION
ARASHIOS_ARCH=$ARCH
ARASHIOS_DESIGN=$ARASHIOS_DESIGN
DEBIAN_CODENAME=$DEBIAN_CODENAME
DEBIAN_SNAPSHOT=${DEBIAN_SNAPSHOT:-none}
GIT_COMMIT=$GIT_COMMIT
BUILD_DATE=$BUILD_DATE
BUILD_JOBS=$JOBS
BUILD_DRY_RUN=$DRY_RUN
ISO_VOLUME=$ISO_VOLUME
CONFIG_HASH=$CONFIG_HASH
HOST_OS=$HOST_OS
HOST_KERNEL=$HOST_KERNEL
HOST_ARCH=$HOST_ARCH
LIVE_BUILD_VERSION=$LB_VERSION
EOF

for file in "$INCLUDES/etc/os-release" "$INCLUDES/etc/lsb-release" "$INCLUDES/etc/issue"; do
    [ -f "$file" ] || continue
    sed -i \
        -e "s/@VERSION@/$VERSION/g" \
        -e "s/@VERSION_NUM@/$VERSION_NUM/g" \
        -e "s/@CODENAME@/$ARASHIOS_CODENAME/g" \
        "$file"
done

log "Menghasilkan token dan aset brand"
"$ROOT/scripts/generate-tokens.py" >/dev/null
"$ROOT/scripts/generate-brand-assets.py" >/dev/null

install -Dm644 "$ROOT/branding/logo/arashios-mark.svg" \
    "$INCLUDES/usr/share/icons/hicolor/scalable/apps/arashios.svg"
install -Dm644 "$ROOT/branding/logo/arashios-wordmark.svg" \
    "$INCLUDES/usr/share/arashios/branding/arashios-wordmark.svg"
install -Dm644 "$ROOT/branding/wallpaper/kage-sumi.svg" \
    "$INCLUDES/usr/share/backgrounds/arashios/kage-sumi.svg"

install -Dm644 "$ROOT/branding/grub/theme.txt" \
    "$INCLUDES/usr/share/grub/themes/arashios/theme.txt"
for png in "$ROOT"/branding/grub/*.png; do
    install -Dm644 "$png" "$INCLUDES/usr/share/grub/themes/arashios/$(basename "$png")"
done

install -Dm644 "$ROOT/branding/plymouth/arashios.plymouth" \
    "$INCLUDES/usr/share/plymouth/themes/arashios/arashios.plymouth"
install -Dm644 "$ROOT/branding/plymouth/arashios.script" \
    "$INCLUDES/usr/share/plymouth/themes/arashios/arashios.script"
install -Dm644 "$ROOT/branding/plymouth/logo.png" \
    "$INCLUDES/usr/share/plymouth/themes/arashios/logo.png"

install -Dm644 "$ROOT/build/tokens/tokens.css" \
    "$INCLUDES/usr/share/arashios/theme/tokens.css"
install -Dm644 "$ROOT/build/tokens/kage.qss" \
    "$INCLUDES/usr/share/arashios/theme/kage.qss"
install -Dm644 "$ROOT/build/tokens/tokens.resolved.json" \
    "$INCLUDES/usr/share/arashios/theme/tokens.resolved.json"

install -Dm644 "$ROOT/LICENSE" "$INCLUDES/usr/share/doc/arashios/LICENSE"
install -Dm644 "$ROOT/LICENSE" "$INCLUDES/usr/share/doc/arashios/copyright"
install -Dm644 "$ROOT/CHANGELOG.md" "$INCLUDES/usr/share/doc/arashios/CHANGELOG.md"
install -Dm644 "$ROOT/docs/LEGAL.md" "$INCLUDES/usr/share/doc/arashios/LEGAL.md"
install -Dm644 "$ROOT/docs/PRIVACY.md" "$INCLUDES/usr/share/doc/arashios/PRIVACY.md"
install -Dm644 "$ROOT/docs/TRADEMARK.md" "$INCLUDES/usr/share/doc/arashios/TRADEMARK.md"

install -Dm755 "$ROOT/tests/smoke.sh" "$INCLUDES/usr/local/bin/arashios-smoke"

log "Konfigurasi siap di $WORK/config"

if [ "$DRY_RUN" -eq 1 ]; then
    log "Dry run selesai. Tidak ada ISO yang dibangun."
    exit 0
fi

log "Build dimulai. Log: $LOG"
export MKSQUASHFS_OPTIONS="-processors $JOBS"
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
