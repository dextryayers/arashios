#!/usr/bin/env bash
# Generate the ArashiOS repository signing key and export the public keyring.
#
# The private key stays inside the repository key directory and is never
# copied into an image. For a release, set
# ARASHIOS_REPO_KEY_PASSPHRASE in the environment so the key is protected.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KEY_DIR="$ROOT/repo/keys"
GNUPG_HOME="$KEY_DIR/gnupg"
KEY_UID="ArashiOS Archive Signing Key <maintainers@arashios.example>"
FINGERPRINT_FILE="$KEY_DIR/arashios-archive.fingerprint"

command -v gpg >/dev/null 2>&1 || {
    printf 'ERROR: gpg tidak ditemukan. Pasang paket gnupg.\n' >&2
    exit 1
}

log() {
    printf '[repo-key] %s\n' "$*"
}

mkdir -p "$KEY_DIR"
chmod 0700 "$GNUPG_HOME" 2>/dev/null || true
mkdir -p "$GNUPG_HOME"
chmod 0700 "$GNUPG_HOME"

export GNUPGHOME="$GNUPG_HOME"

if [ -f "$FINGERPRINT_FILE" ]; then
    log "kunci sudah ada: $(cat "$FINGERPRINT_FILE")"
else
    if [ -n "${ARASHIOS_REPO_KEY_PASSPHRASE:-}" ]; then
        log "membuat kunci RSA 4096 dengan passphrase dari environment"
    else
        log "PERINGATAN: membuat kunci development tanpa passphrase"
        log "set ARASHIOS_REPO_KEY_PASSPHRASE untuk kunci rilis"
    fi
    cat > "$KEY_DIR/key-params" <<EOF
%no-protection
Key-Type: RSA
Key-Length: 4096
Key-Usage: sign
Name-Real: ArashiOS Archive
Name-Comment: ArashiOS Archive Signing Key
Name-Email: maintainers@arashios.example
Expire-Date: 3y
%commit
EOF
    gpg --batch --gen-key "$KEY_DIR/key-params" >/dev/null 2>&1
    gpg --batch --yes --pinentry-mode loopback \
        --passphrase "${ARASHIOS_REPO_KEY_PASSPHRASE:-}" \
        --quick-set-expire 3y "$(gpg --list-keys --with-colons | awk -F: '/^fpr/ {print $10; exit}')" >/dev/null 2>&1 || true
    gpg --fingerprint --with-colons | awk -F: '/^fpr/ {print $10; exit}' > "$FINGERPRINT_FILE"
    log "kunci dibuat: $(cat "$FINGERPRINT_FILE")"
fi

FINGERPRINT="$(cat "$FINGERPRINT_FILE")"

gpg --batch --yes --armor --export "$FINGERPRINT" > "$KEY_DIR/arashios-archive-keyring.asc"
gpg --batch --yes --export "$FINGERPRINT" > "$KEY_DIR/arashios-archive-keyring.gpg"
chmod 0644 "$KEY_DIR/arashios-archive-keyring.asc" "$KEY_DIR/arashios-archive-keyring.gpg"
chmod 0600 "$KEY_DIR/key-params" 2>/dev/null || true

log "keyring publik: repo/keys/arashios-archive-keyring.gpg"
log "fingerprint   : $FINGERPRINT"
printf '%s\n' "$FINGERPRINT"
