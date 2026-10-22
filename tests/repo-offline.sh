#!/usr/bin/env bash
# ArashiOS offline repository test.
#
# The test copies the published repository to a temporary directory, lets apt
# read it with the archive keyring, rebuilds the package index straight from
# the pool, and compares the result with the shipped index.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

REPO="$ROOT/repo/public"
KEYRING="$ROOT/repo/keys/arashios-archive-keyring.gpg"
TMP="$(mktemp -d)"
FAILURES=0

cleanup() {
    rm -rf "$TMP"
}
trap cleanup EXIT

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    FAILURES=$((FAILURES + 1))
}

ok() {
    printf 'OK:   %s\n' "$*"
}

printf 'ArashiOS offline repository test\n\n'

[ -d "$REPO" ] || { printf 'ERROR: repository belum dibangun\n' >&2; exit 2; }
[ -f "$KEYRING" ] || { printf 'ERROR: keyring repository tidak ditemukan\n' >&2; exit 2; }

cp -a "$REPO" "$TMP/repo"
printf 'deb [signed-by=%s] file://%s stable main\n' \
    "$KEYRING" "$TMP/repo" > "$TMP/sources.list"
mkdir -p "$TMP/lists/partial" "$TMP/cache/archives/partial"

printf 'Pembacaan repository oleh apt:\n'
if apt-get \
    -o Dir::Etc::sourcelist="$TMP/sources.list" \
    -o Dir::Etc::sourceparts="-" \
    -o Dir::State::lists="$TMP/lists" \
    -o Dir::Cache="$TMP/cache" \
    -o APT::Get::List-Cleanup="0" \
    update >"$TMP/apt.log" 2>&1; then
    ok "apt update membaca repository bertanda tangan"
else
    fail "apt update gagal"
    sed -n '1,20p' "$TMP/apt.log" >&2
fi

if apt-cache \
    -o Dir::Etc::sourcelist="$TMP/sources.list" \
    -o Dir::Etc::sourceparts="-" \
    -o Dir::State::lists="$TMP/lists" \
    -o Dir::Cache="$TMP/cache" \
    policy arashios-arsenal >"$TMP/policy.log" 2>&1; then
    if grep -q "arashios-arsenal" "$TMP/policy.log"; then
        ok "apt melihat paket arashios-arsenal"
    else
        fail "apt tidak melihat paket arashios-arsenal"
        sed -n '1,20p' "$TMP/policy.log" >&2
    fi
else
    fail "apt-cache policy gagal"
fi

printf '\nRebuild index dari pool:\n'
if command -v dpkg-scanpackages >/dev/null 2>&1; then
    ( cd "$TMP/repo/pool" && dpkg-scanpackages --multiversion . /dev/null 2>/dev/null ) \
        > "$TMP/pool-packages" || true
    if [ -s "$TMP/pool-packages" ]; then
        pool_names="$(awk '/^Package: /{print $2}' "$TMP/pool-packages" | sort -u)"
        index_names="$(awk '/^Package: /{print $2}' \
            "$TMP/repo/dists/stable/main/binary-amd64/Packages" | sort -u)"
        if [ "$pool_names" = "$index_names" ]; then
            ok "indeks pool sama dengan indeks yang dipublikasikan"
        else
            fail "indeks pool berbeda dengan indeks yang dipublikasikan"
        fi
    else
        fail "pool tidak menghasilkan indeks paket"
    fi
else
    printf 'SKIP  dpkg-scanpackages tidak tersedia\n'
fi

printf '\nIsi pool:\n'
POOL_COUNT="$(find "$TMP/repo/pool" -name '*.deb' | wc -l | tr -d ' ')"
if [ "$POOL_COUNT" -ge 16 ]; then
    ok "pool memuat $POOL_COUNT paket"
else
    fail "pool hanya memuat $POOL_COUNT paket"
fi

printf '\n'
if [ "$FAILURES" -gt 0 ]; then
    printf 'Offline repository test gagal: %s masalah.\n' "$FAILURES" >&2
    exit 1
fi
printf 'Offline repository test lulus.\n'
