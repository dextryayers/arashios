#!/usr/bin/env bash
# Verify an ArashiOS ISO artifact before it is published.
# Usage: ./tests/verify-artifact.sh out/ArashiOS-amd64-V1.10.21.iso
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
source "$ROOT/versions.env"

ISO=""
ERRORS=0

usage() {
    cat <<EOF
Pemakaian: $0 <iso>

Memeriksa nama, ukuran, struktur ISO 9660, bootloader, checksum, dan tanda tangan.
EOF
}

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    ERRORS=$((ERRORS + 1))
}

ok() {
    printf 'OK:   %s\n' "$*"
}

warn() {
    printf 'WARN: %s\n' "$*"
}

log() {
    printf 'INFO: %s\n' "$*"
}

for arg in "$@"; do
    case "$arg" in
        -h|--help) usage; exit 0 ;;
        *) [ -z "$ISO" ] || { printf 'ERROR: hanya satu ISO yang diterima.\n' >&2; exit 2; }; ISO="$arg" ;;
    esac
done

[ -n "$ISO" ] || { usage; exit 2; }
[ -f "$ISO" ] || { printf 'ERROR: ISO tidak ditemukan: %s\n' "$ISO" >&2; exit 1; }
ISO="$(readlink -f "$ISO")"
base="$(basename "$ISO")"

printf 'ArashiOS artifact verification\n'
printf 'File: %s\n\n' "$ISO"

if [[ "$base" =~ ^ArashiOS-(amd64|arm64|i386)-(V[0-9]+\.[0-9]{2}\.[0-9]{2})(-(cinnamon|xfce|lxqt))?\.iso$ ]]; then
    arch="${BASH_REMATCH[1]}"
    version="${BASH_REMATCH[2]}"
    variant="${BASH_REMATCH[4]:-}"
else
    printf 'ERROR: nama ISO tidak sesuai skema ArashiOS-<arch>-<version>[-<edition>].iso\n' >&2
    exit 1
fi

if [ -n "$variant" ]; then
    edition="$variant"
else
    default_var="DEFAULT_EDITION_${arch^^}"
    edition="${!default_var}"
fi

max_var="MAX_ISO_MIB_${edition^^}"
max_mib="${!max_var}"

ok "nama: arch=$arch edition=$edition version=$version"
log "edition default untuk $arch: $default_var=${!default_var}"

size_bytes="$(stat -c %s "$ISO")"
size_mib=$(( (size_bytes + 1048575) / 1048576 ))
log "ukuran: ${size_mib} MiB (${size_bytes} byte), batas ${max_mib} MiB"
if [ "$size_mib" -le "$max_mib" ]; then
    ok "ukuran di bawah batas"
else
    fail "ukuran ${size_mib} MiB melebihi batas ${max_mib} MiB"
fi

if python3 - "$ISO" <<'PY'
import sys

with open(sys.argv[1], "rb") as handle:
    handle.seek(32768)
    descriptor = handle.read(6)
if descriptor[1:6] != b"CD001":
    print("ISO 9660 primary volume descriptor tidak ditemukan", file=sys.stderr)
    raise SystemExit(1)
PY
then
    ok "ISO 9660 primary volume descriptor"
else
    fail "struktur ISO 9660 tidak valid"
fi

if command -v xorriso >/dev/null 2>&1; then
    volume_id="$(xorriso -indev "$ISO" -pvd_info 2>/dev/null | sed -n "s/^Volume id[^:]*: *//p" | head -1 | tr -d \"'\")"
    if [ -n "$volume_id" ]; then
        expected="ARASHIOS_$(printf '%s' "${version#V}" | tr '.' '_')"
        log "volume ID: $volume_id"
        if [ "$volume_id" = "$expected" ]; then
            ok "volume ID sesuai: $expected"
        else
            warn "volume ID tidak sama dengan $expected"
        fi
    else
        warn "volume ID tidak dapat dibaca"
    fi

    if xorriso -indev "$ISO" -ls / 2>/dev/null | grep -q 'live'; then
        ok "direktori /live ditemukan"
    else
        fail "direktori /live tidak ditemukan"
    fi

    if xorriso -indev "$ISO" -ls /live 2>/dev/null | grep -Eq 'vmlinuz|initrd'; then
        ok "kernel dan initrd ditemukan"
    else
        fail "kernel atau initrd tidak ditemukan di /live"
    fi

    if [ "$arch" = "amd64" ] || [ "$arch" = "i386" ]; then
        if xorriso -indev "$ISO" -ls /isolinux 2>/dev/null | grep -q 'isolinux.bin'; then
            ok "bootloader BIOS isolinux"
        else
            fail "isolinux.bin tidak ditemukan"
        fi
    fi

    case "$arch" in
        amd64) efi_name="BOOTX64.EFI" ;;
        i386) efi_name="BOOTIA32.EFI" ;;
        arm64) efi_name="BOOTAA64.EFI" ;;
    esac
    if xorriso -indev "$ISO" -ls /EFI/BOOT 2>/dev/null | grep -qi "$efi_name"; then
        ok "bootloader UEFI $efi_name"
    else
        fail "bootloader UEFI $efi_name tidak ditemukan"
    fi
else
    warn "xorriso tidak terpasang, pemeriksaan isi ISO dilewati"
fi

sha_file="${ISO}.sha256"
if [ -f "$sha_file" ]; then
    if ( cd "$(dirname "$ISO")" && sha256sum -c "$(basename "$sha_file")" >/dev/null ); then
        ok "checksum SHA-256 cocok"
    else
        fail "checksum SHA-256 tidak cocok"
    fi
else
    warn "berkas .sha256 tidak ditemukan"
fi

sha512_file="${ISO}.sha512"
if [ -f "$sha512_file" ]; then
    if ( cd "$(dirname "$ISO")" && sha512sum -c "$(basename "$sha512_file")" >/dev/null ); then
        ok "checksum SHA-512 cocok"
    else
        fail "checksum SHA-512 tidak cocok"
    fi
else
    warn "berkas .sha512 tidak ditemukan"
fi

sig_file="${ISO}.sig"
if [ -f "$sig_file" ]; then
    if command -v minisign >/dev/null 2>&1; then
        if minisign -Vm "$ISO" -x "$sig_file" >/dev/null; then
            ok "tanda tangan minisign valid"
        else
            fail "tanda tangan minisign tidak valid"
        fi
    else
        warn "berkas .sig ada tetapi minisign tidak terpasang"
    fi
else
    warn "ISO belum ditandatangani (fase 1 belum memakai signing key produksi)"
fi

printf '\n'
if [ "$ERRORS" -gt 0 ]; then
    printf 'Status: GAGAL dengan %s masalah.\n' "$ERRORS" >&2
    exit 1
fi

printf 'Status: artefak valid.\n'
