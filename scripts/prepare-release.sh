#!/usr/bin/env bash
# Prepare an ArashiOS release directory with checksums and notes.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

VERSION="${1:-$ARASHIOS_VERSION}"
OUT_DIR="$ROOT/out"
RELEASE_DIR="$ROOT/build/release-$VERSION"

usage() {
    cat <<EOF
Pemakaian: $0 [versi]

Menyiapkan direktori rilis dengan checksum dan catatan.
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
    exit 0
fi

mkdir -p "$RELEASE_DIR"
if [ -d "$OUT_DIR" ]; then
    find "$OUT_DIR" -maxdepth 1 -type f -name "ArashiOS-*-$VERSION*.iso" -print0 |
        xargs -0 -r -n1 cp -t "$RELEASE_DIR"
fi

(
    cd "$RELEASE_DIR"
    if ls *.iso >/dev/null 2>&1; then
        sha256sum *.iso > SHA256SUMS
        sha512sum *.iso > SHA512SUMS
    fi
)

cat > "$RELEASE_DIR/RELEASE.txt" <<EOF
ArashiOS $VERSION
Codename: $ARASHIOS_CODENAME
Design: $ARASHIOS_DESIGN
Basis: Debian $DEBIAN_CODENAME
EOF

printf 'OK: direktori rilis disiapkan di %s\n' "$RELEASE_DIR"
