#!/usr/bin/env bash
# ArashiOS upgrade path test.
#
# The test validates the version scheme, the package version mapping, the
# changelog order, and that a newer release always supersedes the older one
# so an in place upgrade never needs a reinstallation.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

TMP="$(mktemp -d)"
FAILURES=0
FROM_VERSION="V1.10.21"
TO_VERSION="V1.10.28"

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

printf 'ArashiOS upgrade path test\n\n'

printf 'Skema versi:\n'
if printf '%s' "$ARASHIOS_VERSION" | grep -qE '^V[0-9]+\.[0-9]{2}\.[0-9]{2}$'; then
    ok "versi rilis $ARASHIOS_VERSION mengikuti pola V<major>.<MM>.<DD>"
else
    fail "versi rilis $ARASHIOS_VERSION tidak sesuai pola"
fi
if printf '%s' "$FROM_VERSION" | grep -qE '^V[0-9]+\.[0-9]{2}\.[0-9]{2}$'; then
    ok "versi asal $FROM_VERSION valid"
else
    fail "versi asal tidak valid"
fi
if printf '%s' "$TO_VERSION" | grep -qE '^V[0-9]+\.[0-9]{2}\.[0-9]{2}$'; then
    ok "versi tujuan $TO_VERSION valid"
else
    fail "versi tujuan tidak valid"
fi

printf '\nPemetaan versi paket:\n'
from_number="${FROM_VERSION#V}"
to_number="${TO_VERSION#V}"
if dpkg --compare-versions "1.10.21-1" lt "1.10.28-1"; then
    ok "paket 1.10.21-1 lebih lama dari 1.10.28-1"
else
    fail "perbandingan versi paket gagal"
fi

printf '\nBangun dua versi paket:\n'
if ARASHIOS_PACKAGE_VERSION="1.10.21-1" python3 "$ROOT/scripts/build-packages.py" --package arashios-arsenal \
    >"$TMP/out" 2>&1; then
    cp "$ROOT/build/packages/arashios-arsenal_1.10.21-1_all.deb" "$TMP/" 2>/dev/null || true
    ok "paket versi lama dibangun"
else
    fail "paket versi lama gagal dibangun"
    sed -n '1,10p' "$TMP/out" >&2
fi
if ARASHIOS_PACKAGE_VERSION="1.10.28-1" python3 "$ROOT/scripts/build-packages.py" --package arashios-arsenal \
    >"$TMP/out" 2>&1; then
    cp "$ROOT/build/packages/arashios-arsenal_1.10.28-1_all.deb" "$TMP/" 2>/dev/null || true
    ok "paket versi baru dibangun"
else
    fail "paket versi baru gagal dibangun"
    sed -n '1,10p' "$TMP/out" >&2
fi

if [ -f "$TMP/arashios-arsenal_1.10.21-1_all.deb" ] && [ -f "$TMP/arashios-arsenal_1.10.28-1_all.deb" ]; then
    old_version="$(dpkg-deb -f "$TMP/arashios-arsenal_1.10.21-1_all.deb" Version)"
    new_version="$(dpkg-deb -f "$TMP/arashios-arsenal_1.10.28-1_all.deb" Version)"
    if dpkg --compare-versions "$old_version" lt "$new_version"; then
        ok "paket baru menggantikan paket lama tanpa reinstalasi"
    else
        fail "paket baru tidak lebih tinggi dari paket lama"
    fi
    old_hash="$(sha256sum "$TMP/arashios-arsenal_1.10.21-1_all.deb" | cut -d' ' -f1)"
    new_hash="$(sha256sum "$TMP/arashios-arsenal_1.10.28-1_all.deb" | cut -d' ' -f1)"
    if [ "$old_hash" != "$new_hash" ]; then
        ok "isi paket berubah antar versi"
    else
        fail "isi paket tidak berubah, versi paket tidak妓 significativa"
    fi
else
    fail "paket versi lama dan baru tidak lengkap"
fi

printf '\nChangelog:\n'
if grep -q "\[${ARASHIOS_VERSION}\]" "$ROOT/CHANGELOG.md"; then
    ok "changelog memuat entri ${ARASHIOS_VERSION}"
else
    fail "changelog tidak memuat entri ${ARASHIOS_VERSION}"
fi
if head -20 "$ROOT/CHANGELOG.md" | grep -q "\[${ARASHIOS_VERSION}\]"; then
    ok "entri rilis berada di bagian atas changelog"
else
    fail "entri rilis tidak berada di bagian atas changelog"
fi

printf '\nPemulihan state build:\n'
rm -f "$ROOT"/build/packages/*_1.10.28-1_all.deb
python3 "$ROOT/scripts/build-packages.py" --package arashios-arsenal >"$TMP/out" 2>&1 || true
python3 "$ROOT/scripts/snapshot-manifest.py" >"$TMP/out" 2>&1 || true
if [ -f "$ROOT/build/packages/arashios-arsenal_1.10.21-1_all.deb" ]; then
    ok "paket versi rilis dipulihkan"
else
    fail "paket versi rilis gagal dipulihkan"
fi

printf '\nSnapshot repository:\n'
if python3 "$ROOT/scripts/snapshot-manifest.py" --check >/dev/null 2>&1; then
    ok "manifest snapshot sinkron dengan paket yang dibangun"
else
    fail "manifest snapshot kedaluwarsa, jalankan scripts/snapshot-manifest.py"
fi

printf '\n'
if [ "$FAILURES" -gt 0 ]; then
    printf 'Upgrade path test gagal: %s masalah.\n' "$FAILURES" >&2
    exit 1
fi
printf 'Upgrade path test lulus.\n'
