#!/usr/bin/env bash
# Validate the ArashiOS configuration tree before a build.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../versions.env
# shellcheck disable=SC1091
source "$ROOT/versions.env"

ERRORS=0
TMP_FILES=()

cleanup() {
    if [ "${#TMP_FILES[@]}" -gt 0 ]; then
        rm -f "${TMP_FILES[@]}"
    fi
}
trap cleanup EXIT

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    ERRORS=$((ERRORS + 1))
}

info() {
    printf 'INFO: %s\n' "$*"
}

ok() {
    printf 'OK:   %s\n' "$*"
}

require_file() {
    if [ -f "$ROOT/$1" ]; then
        ok "$1"
    else
        fail "berkas hilang: $1"
    fi
}

require_dir() {
    if [ -d "$ROOT/$1" ]; then
        ok "$1"
    else
        fail "direktori hilang: $1"
    fi
}

require_exec() {
    if [ -x "$ROOT/$1" ]; then
        ok "executable: $1"
    else
        fail "tidak executable: $1"
    fi
}

read_list() {
    local file="$1"
    local line package
    while IFS= read -r line || [ -n "$line" ]; do
        line="${line%%#*}"
        line="${line#"${line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"
        [ -n "$line" ] || continue
        for package in $line; do
            printf '%s\n' "$package"
        done
    done < "$file"
}

printf 'ArashiOS configuration validation\n'
printf 'Root: %s\n\n' "$ROOT"

printf 'Struktur:\n'
require_dir config/common
require_dir config/common/package-lists
require_dir config/common/includes.chroot/etc
require_dir config/common/hooks/live
for edition in $SUPPORTED_EDITIONS; do
    require_dir "config/editions/$edition"
    require_file "config/editions/$edition/package-lists/50-desktop.list.chroot"
    require_file "config/editions/$edition/includes.chroot/etc/lightdm/lightdm.conf.d/50-arashios.conf"
done
for arch in amd64 arm64; do
    require_dir "config/arches/$arch/package-lists"
done

printf '\nBranding dan token:\n'
require_file branding/tokens.json
require_file branding/logo/arashios-mark.svg
require_file branding/logo/arashios-wordmark.svg
require_file branding/wallpaper/kage-sumi.svg
require_file branding/grub/theme.txt
require_file branding/grub/background.png
require_file branding/plymouth/arashios.plymouth
require_file branding/plymouth/arashios.script
require_file branding/plymouth/logo.png
require_file scripts/generate-tokens.py
require_file scripts/generate-brand-assets.py

for name in nw n ne w c e sw s se; do
    require_file "branding/grub/select_${name}.png"
done

printf '\nHak eksekusi:\n'
require_exec build.sh
for file in scripts/check-env.sh scripts/validate-config.sh scripts/check-docs.sh \
            scripts/generate-tokens.py scripts/generate-brand-assets.py \
            tests/qemu-boot.sh tests/smoke.sh tests/verify-artifact.sh tests/config-matrix.sh; do
    require_exec "$file"
done
for file in "$ROOT"/config/common/hooks/live/*.chroot; do
    if [ -x "$file" ]; then
        ok "hook executable: ${file#"$ROOT/"}"
    else
        fail "hook tidak executable: ${file#"$ROOT/"}"
    fi
done
require_exec config/common/includes.chroot/usr/local/bin/arashios-wallpaper
require_exec config/common/includes.chroot/lib/live/config/9990-arashios-shell

printf '\nMetadata sistem:\n'
if grep -q '^ID=arashios$' "$ROOT/config/common/includes.chroot/etc/os-release"; then
    ok "os-release ID=arashios"
else
    fail "os-release tidak memiliki ID=arashios"
fi
if grep -q '^ID_LIKE=debian$' "$ROOT/config/common/includes.chroot/etc/os-release"; then
    ok "os-release ID_LIKE=debian"
else
    fail "os-release tidak memiliki ID_LIKE=debian"
fi
for placeholder in '@VERSION@' '@VERSION_NUM@' '@CODENAME@'; do
    if grep -q "$placeholder" "$ROOT/config/common/includes.chroot/etc/os-release"; then
        ok "placeholder $placeholder"
    else
        fail "placeholder $placeholder hilang dari os-release"
    fi
done
require_file config/common/includes.chroot/etc/subuid
require_file config/common/includes.chroot/etc/subgid
require_file config/common/includes.chroot/etc/sysctl.d/99-arashios-hardening.conf
require_file config/common/archives/backports.list.chroot

printf '\nPaket per kombinasi:\n'
for combo in $SUPPORTED_COMBINATIONS; do
    arch="${combo%%:*}"
    edition="${combo#*:}"
    if [ "$arch" = "$combo" ] || [ -z "$edition" ]; then
        fail "format kombinasi tidak valid: $combo"
        continue
    fi
    list_files=(
        "$ROOT"/config/common/package-lists/*.list.chroot
        "$ROOT/config/editions/$edition/package-lists/"*.list.chroot
    )
    if [ -d "$ROOT/config/arches/$arch/package-lists" ]; then
        list_files+=("$ROOT"/config/arches/"$arch"/package-lists/*.list.chroot)
    fi

    packages="$(mktemp)"
    TMP_FILES+=("$packages")
    for file in "${list_files[@]}"; do
        [ -f "$file" ] || continue
        while IFS= read -r package; do
            if [[ ! "$package" =~ ^[a-z0-9][a-z0-9+.-]*$ ]]; then
                fail "nama paket tidak valid di ${file#"$ROOT/"}: $package"
                continue
            fi
            printf '%s\n' "$package"
        done < <(read_list "$file") >> "$packages"
    done

    duplicates="$(sort "$packages" | uniq -d)"
    if [ -n "$duplicates" ]; then
        fail "paket duplikat pada $edition/$arch: $(printf '%s' "$duplicates" | tr '\n' ' ')"
    fi

    total="$(sort -u "$packages" | wc -l | tr -d ' ')"
    if [ "$total" -lt 50 ]; then
        fail "jumlah paket terlalu sedikit pada $edition/$arch: $total"
    fi
    info "$edition/$arch: $total paket unik"
done

printf '\nKebijakan repositori dan layanan:\n'
if grep -R -i -q --include='*.list.chroot' --include='*.list.binary' 'kali' "$ROOT/config"; then
    fail "repository Kali ditemukan di config"
else
    ok "tidak ada repository Kali"
fi
if grep -R -q --include='*.list.chroot' '^openssh-server$' "$ROOT/config"; then
    fail "openssh-server ditemukan di package list"
else
    ok "openssh-server tidak dipasang"
fi

printf '\nValidasi JSON dan XML:\n'
if python3 - "$ROOT/branding/tokens.json" <<'PY'
import json
import sys
with open(sys.argv[1], encoding="utf-8") as handle:
    json.load(handle)
PY
then
    ok "branding/tokens.json valid"
else
    fail "branding/tokens.json tidak valid"
fi

if python3 - "$ROOT" <<'PY'
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
root = Path(sys.argv[1])
failed = []
for path in sorted(root.glob("**/*.svg")):
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        failed.append(f"{path.relative_to(root)}: {exc}")
if failed:
    print("\n".join(failed), file=sys.stderr)
    raise SystemExit(1)
PY
then
    ok "semua SVG valid"
else
    fail "SVG tidak valid"
fi

printf '\nSinkronisasi artefak:\n'
if "$ROOT/scripts/generate-tokens.py" --check >/dev/null 2>&1; then
    ok "token desain sinkron"
else
    fail "token desain kedaluwarsa, jalankan scripts/generate-tokens.py"
fi
if "$ROOT/scripts/generate-brand-assets.py" --check >/dev/null 2>&1; then
    ok "aset raster sinkron"
else
    fail "aset raster kedaluwarsa, jalankan scripts/generate-brand-assets.py"
fi

printf '\n'
if [ "$ERRORS" -gt 0 ]; then
    printf 'Status: GAGAL dengan %s masalah.\n' "$ERRORS" >&2
    exit 1
fi

printf 'Status: konfigurasi valid.\n'
