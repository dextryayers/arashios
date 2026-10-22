#!/usr/bin/env bash
# Sign and verify ArashiOS release artifacts.
#
# The script signs ISO images, checksum files, and SBOM files. minisign is
# used when a minisign key is available, otherwise GPG is used. The public key
# fingerprint is printed so it can be published with the release notes.
#
# Usage:
#   scripts/sign-artifact.sh --key <minisign-key> out/ArashiOS-amd64-V1.10.21.iso
#   scripts/sign-artifact.sh --verify out/ArashiOS-amd64-V1.10.21.iso.sig
#   scripts/sign-artifact.sh --gpg out/ArashiOS-amd64-V1.10.21.iso
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MINISIGN_KEY="${MINISIGN_KEY:-}"
GPG_KEY_ID="${GPG_KEY_ID:-}"
MODE="sign"
ARTIFACT=""
PUBKEY=""
FINGERPRINT_FILE="$ROOT/repo/keys/arashios-archive.fingerprint"

usage() {
    cat <<'EOF'
Pemakaian: scripts/sign-artifact.sh [opsi] <berkas>

Opsi:
  --key FILE     Kunci privat minisign untuk penandatanganan.
  --pubkey FILE  Kunci publik minisign untuk verifikasi.
  --gpg          Gunakan GPG dengan kunci dari GPG_KEY_ID.
  --verify       Verifikasi tanda tangan yang sudah ada.
  -h, --help     Tampilkan bantuan ini.
EOF
}

log() {
    printf '[sign] %s\n' "$*"
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --key) MINISIGN_KEY="${2:-}"; shift 2 ;;
        --pubkey) PUBKEY="${2:-}"; shift 2 ;;
        --gpg) GPG_KEY_ID="${GPG_KEY_ID:-arashios}"; shift ;;
        --verify) MODE="verify"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) ARTIFACT="$1"; shift ;;
    esac
done

[ -n "$ARTIFACT" ] || { usage; exit 2; }
[ -f "$ARTIFACT" ] || die "berkas tidak ditemukan: $ARTIFACT"

if [ "$MODE" = "verify" ]; then
    signature="$ARTIFACT"
    [ -f "$signature" ] || die "berkas tanda tangan tidak ditemukan: $signature"
    target="${signature%.sig}"
    [ -f "$target" ] || target="${signature%.minisig}"
    [ -f "$target" ] || die "berkas yang ditandatangani tidak ditemukan untuk $signature"
    if command -v minisign >/dev/null 2>&1 && [ -n "$PUBKEY" ]; then
        if minisign -Vm "$target" -x "$signature" -p "$PUBKEY" >/dev/null 2>&1; then
            log "tanda tangan minisign valid: $target"
            exit 0
        fi
        die "tanda tangan minisign tidak valid"
    fi
    if command -v gpgv >/dev/null 2>&1 && [ -f "$ROOT/repo/keys/arashios-archive-keyring.gpg" ]; then
        if gpgv --keyring "$ROOT/repo/keys/arashios-archive-keyring.gpg" "$signature" >/dev/null 2>&1; then
            log "tanda tangan GPG valid: $target"
            exit 0
        fi
        die "tanda tangan GPG tidak valid"
    fi
    die "tidak ada alat verifikasi yang tersedia"
fi

if [ -n "$MINISIGN_KEY" ]; then
    command -v minisign >/dev/null 2>&1 || die "minisign tidak ditemukan."
    [ -f "$MINISIGN_KEY" ] || die "kunci minisign tidak ditemukan: $MINISIGN_KEY"
    minisign -S -s "$MINISIGN_KEY" -m "$ARTIFACT" -x "$ARTIFACT.sig"
    log "ditandatangani dengan minisign: $ARTIFACT.sig"
    if [ -f "$FINGERPRINT_FILE" ]; then
        log "fingerprint kunci repository: $(cat "$FINGERPRINT_FILE")"
    fi
    exit 0
fi

if [ -n "$GPG_KEY_ID" ]; then
    command -v gpg >/dev/null 2>&1 || die "gpg tidak ditemukan."
    gpg --batch --yes --armor --detach-sign --output "$ARTIFACT.sig" "$ARTIFACT"
    log "ditandatangani dengan GPG: $ARTIFACT.sig"
    exit 0
fi

die "tentukan --key untuk minisign atau --gpg untuk GPG"
