#!/usr/bin/env bash
# ArashiOS installer, persistence, and recovery tests.
#
# The suite validates the Calamares configuration, the Kage branding of the
# installer, and the behaviour of the installer helper commands.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/config/common/includes.chroot/usr/local/bin"
CALAMARES="$ROOT/config/common/includes.chroot/etc/calamares"
BRANDING="$ROOT/config/common/includes.chroot/usr/share/calamares/branding/arashios"
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

expect_zero() {
    local label="$1"
    shift
    if "$@" >"$TMP/out" 2>&1; then
        ok "$label"
    else
        fail "$label"
        sed -n '1,20p' "$TMP/out" >&2
    fi
}

expect_fail() {
    local label="$1"
    shift
    if "$@" >"$TMP/out" 2>&1; then
        fail "$label, perintah seharusnya gagal"
        sed -n '1,20p' "$TMP/out" >&2
    else
        ok "$label"
    fi
}

printf 'ArashiOS installer tests\n\n'

printf 'Pemeriksaan statis:\n'
expect_zero "konfigurasi installer" python3 "$ROOT/scripts/check-installer.py"
expect_zero "paket installer tersedia di bookworm" python3 "$ROOT/scripts/check-packages-bookworm.py" --combinations

printf '\nKonfigurasi Calamares:\n'
python3 - "$CALAMARES" "$BRANDING" <<'PY'
import sys
from pathlib import Path

import yaml

calamares = Path(sys.argv[1])
branding = Path(sys.argv[2])

settings = yaml.safe_load((calamares / "settings.conf").read_text(encoding="utf-8"))
modules = yaml.safe_load((calamares / "modules.conf").read_text(encoding="utf-8"))
sequence = modules["sequence"]
assert settings["branding"] == "arashios", settings
assert sequence[0] == "welcome", sequence
assert sequence[-1] == "shellprocess", sequence
assert "partition" in sequence and "bootloader" in sequence, sequence

for name in ("partition", "fstab", "bootloader", "displaymanager", "users",
             "services-systemd", "packages", "shellprocess"):
    path = calamares / "modules" / f"{name}.conf"
    assert path.is_file(), f"modul {name} tidak punya konfigurasi"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), name

desc = (branding / "branding.desc").read_text(encoding="utf-8")
assert "componentName: arashios" in desc
assert "type: \"none\"" in desc
assert (branding / "stylesheet.qss").is_file()
assert (branding / "show.qml").is_file()
assert len(list((branding / "slides").glob("*.md"))) >= 3
print("OK:   konfigurasi Calamares dan branding Kage valid")
PY

printf '\nPerintah installer:\n'
expect_zero "pemeriksaan dual boot" "$BIN/arashios-dualboot-check"
expect_zero "pemeriksaan dual boot JSON" "$BIN/arashios-dualboot-check" --json
expect_zero "daftar partisi persistensi" "$BIN/arashios-persistence" list
expect_fail "partisi persistensi tanpa label ditolak" "$BIN/arashios-persistence" status
expect_zero "diagnosis pemulihan" "$BIN/arashios-recovery" diagnose
expect_zero "daftar disk pemulihan" "$BIN/arashios-recovery" list-disks
expect_fail "perintah pemulihan tidak dikenal ditolak" "$BIN/arashios-recovery" perintah-hantu
expect_fail "perintah persistensi tidak dikenal ditolak" "$BIN/arashios-persistence" perintah-hantu

python3 - "$BIN" <<'PY'
import json
import subprocess
import sys

binary = sys.argv[1]
result = subprocess.run(
    [f"{binary}/arashios-dualboot-check", "--json"],
    capture_output=True,
    text=True,
    check=True,
)
data = json.loads(result.stdout)
assert "problems" in data and "warnings" in data, data
print("OK:   keluaran JSON pemeriksaan dual boot valid")
PY

printf '\nSkrip post install:\n'
if bash -n "$BIN/arashios-postinstall" 2>/dev/null; then
    ok "skrip post install memiliki sintaks yang benar"
else
    fail "skrip post install salah sintaks"
fi
if grep -q "autologin-user" "$BIN/arashios-postinstall" && \
   grep -q "dpkg --purge" "$BIN/arashios-postinstall"; then
    ok "skrip post install menonaktifkan autologin dan menghapus installer"
else
    fail "skrip post install belum lengkap"
fi

printf '\n'
if [ "$FAILURES" -gt 0 ]; then
    printf 'Installer tests gagal: %s masalah.\n' "$FAILURES" >&2
    exit 1
fi
printf 'Installer tests lulus.\n'
