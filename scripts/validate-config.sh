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
require_file scripts/generate-theme.py
require_file scripts/check-theme.py
require_file scripts/check-desktop.py
require_file scripts/build-branding-package.sh
require_file scripts/generate-toolstack.py
require_file scripts/check-toolstack.py
require_file scripts/generate-toolchain.py
require_file scripts/check-wordlists.py
require_file scripts/check-licenses.py
require_file scripts/refresh-toolchain-lock.py
require_file scripts/refresh-source-pins.py
require_file scripts/build-vendor-tools.sh
require_file scripts/check-glibc.py
require_file tools/catalog.yaml
require_file tools/source-pins.yaml
require_file toolchains/catalog.yaml
require_file toolchains/lock.yaml
require_file docs/TOOLSTACK.md
require_file docs/CODING.md
require_file docs/ARSENAL.md
require_file docs/CONTAINERS.md
require_file docs/VENDORING.md
require_file docs/LICENSES.md
require_file branding/theme/templates/gtk-3.0/gtk.css.in
require_file branding/theme/templates/gtk-4.0/gtk.css.in
require_file branding/theme/templates/cinnamon/cinnamon.css.in
require_file branding/theme/templates/kvantum/ArashiKage.kvconfig.in
for wallpaper in kage-sumi kage-shuriken kage-bamboo kage-washi kage-storm; do
    require_file "branding/wallpaper/$wallpaper.png"
done

for name in nw n ne w c e sw s se; do
    require_file "branding/grub/select_${name}.png"
done

printf '\nHak eksekusi:\n'
require_exec build.sh
for file in scripts/check-env.sh scripts/validate-config.sh scripts/check-docs.sh \
            scripts/generate-tokens.py scripts/generate-brand-assets.py \
            scripts/generate-theme.py scripts/check-theme.py scripts/check-desktop.py \
            scripts/build-branding-package.sh \
            tests/qemu-boot.sh tests/smoke.sh tests/verify-artifact.sh tests/config-matrix.sh \
            tests/theme.sh tests/desktop-matrix.sh tests/branding-package.sh; do
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
require_exec config/common/includes.chroot/usr/local/bin/arashios-accessibility
require_exec config/common/includes.chroot/usr/local/bin/kage-contrast
require_exec config/common/includes.chroot/usr/local/bin/arashios-arsenal
require_exec config/common/includes.chroot/usr/local/bin/arashios-tool-smoke
require_exec config/common/includes.chroot/usr/local/bin/arashios-lab
require_exec config/common/includes.chroot/usr/local/bin/arashios-container
require_exec config/common/includes.chroot/usr/local/bin/arashios-toolchain
require_exec config/common/includes.chroot/usr/local/bin/arashios-new-project
require_exec config/common/includes.chroot/usr/local/bin/arashios-coding-smoke
require_exec config/common/includes.chroot/usr/local/bin/arashios-doctor
require_exec config/common/includes.chroot/usr/local/bin/arashios-help
require_exec config/common/includes.chroot/lib/live/config/9990-arashios-shell
require_file config/common/includes.chroot/usr/local/lib/arashios/toolstack.py
require_file config/common/includes.chroot/usr/share/arashios/toolstack/catalog.json
require_file config/common/includes.chroot/usr/share/arashios/toolchain/catalog.json
require_file config/common/includes.chroot/usr/share/arashios/labs.json
require_file config/common/includes.chroot/usr/share/wordlists/arashios/manifest.json
require_file config/common/includes.chroot/etc/containers/containers.conf
require_file config/common/includes.chroot/etc/containers/policy.json
require_file config/common/includes.chroot/etc/containers/registries.conf

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
paths = list(root.glob("**/*.svg")) + list(root.glob("config/**/*.xml"))
for path in sorted(set(paths)):
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        failed.append(f"{path.relative_to(root)}: {exc}")
if failed:
    print("\n".join(failed), file=sys.stderr)
    raise SystemExit(1)
PY
then
    ok "semua SVG dan XML konfigurasi valid"
else
    fail "SVG atau XML tidak valid"
fi

if command -v grub-script-check >/dev/null 2>&1; then
    if grub-script-check config/common/bootloaders/grub-pc/config.cfg >/dev/null 2>&1; then
        ok "konfigurasi GRUB dapat diparse"
    else
        fail "konfigurasi GRUB tidak dapat diparse"
    fi
else
    info "grub-script-check tidak tersedia, pemeriksaan GRUB dilewati"
fi

if command -v dconf >/dev/null 2>&1; then
    dconf_tmp="$(mktemp)"
    TMP_FILES+=("$dconf_tmp")
    if dconf compile "$dconf_tmp" "$ROOT/config/editions/cinnamon/includes.chroot/etc/dconf/db/local.d" >/dev/null 2>&1; then
        ok "database dconf Cinnamon valid"
    else
        fail "database dconf Cinnamon tidak valid"
    fi
else
    info "dconf tidak tersedia, kompilasi database dilewati"
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
if "$ROOT/scripts/generate-theme.py" --check >/dev/null 2>&1; then
    ok "tema desktop sinkron"
else
    fail "tema desktop kedaluwarsa atau hilang, jalankan scripts/generate-theme.py"
fi
if "$ROOT/scripts/generate-toolstack.py" --check >/dev/null 2>&1; then
    ok "katalog toolstack sinkron"
else
    fail "katalog toolstack kedaluwarsa, jalankan scripts/generate-toolstack.py"
fi
if "$ROOT/scripts/generate-toolchain.py" --check >/dev/null 2>&1; then
    ok "katalog toolchain sinkron"
else
    fail "katalog toolchain kedaluwarsa, jalankan scripts/generate-toolchain.py"
fi

printf '\n'
if [ "$ERRORS" -gt 0 ]; then
    printf 'Status: GAGAL dengan %s masalah.\n' "$ERRORS" >&2
    exit 1
fi

printf 'Status: konfigurasi valid.\n'
