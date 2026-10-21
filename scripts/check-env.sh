#!/usr/bin/env bash
# Check the ArashiOS build host and report missing packages.
# Default mode is advisory. --strict exits nonzero when a required tool is missing.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRICT=0
MISSING_BUILD=()
MISSING_TEST=()
WARNINGS=()

export PATH="$PATH:/usr/sbin:/sbin"

usage() {
    cat <<EOF
Pemakaian: $0 [--strict]

  --strict   Keluar dengan status 1 jika tool build atau test wajib hilang.
  -h, --help Tampilkan bantuan ini.
EOF
}

for arg in "$@"; do
    case "$arg" in
        --strict) STRICT=1 ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'ERROR: argumen tidak dikenal: %s\n' "$arg" >&2; exit 2 ;;
    esac
done

have() {
    command -v "$1" >/dev/null 2>&1
}

check_command() {
    local command_name="$1"
    local package_name="$2"
    local group="$3"
    if have "$command_name"; then
        printf '  OK    %-22s %s\n' "$command_name" "$(command -v "$command_name")"
    else
        printf '  MISS  %-22s paket: %s\n' "$command_name" "$package_name"
        if [ "$group" = "build" ]; then
            MISSING_BUILD+=("$package_name")
        else
            MISSING_TEST+=("$package_name")
        fi
    fi
}

printf 'ArashiOS build host check\n'
printf 'Workspace: %s\n\n' "$ROOT"

if [ -r /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    printf 'Host: %s %s (%s)\n' "${NAME:-unknown}" "${VERSION_ID:-unknown}" "${ID:-unknown}"
else
    WARNINGS+=("Tidak dapat membaca /etc/os-release")
fi

printf '\nTool build:\n'
check_command lb live-build build
check_command debootstrap debootstrap build
check_command xorriso xorriso build
check_command mksquashfs squashfs-tools build
check_command grub-mkimage grub-common build
check_command isohybrid syslinux-utils build
check_command mcopy mtools build
check_command mkfs.vfat dosfstools build

printf '\nModul bootloader:\n'
if [ -f /usr/lib/ISOLINUX/isolinux.bin ]; then
    printf '  OK    %-22s %s\n' isolinux.bin /usr/lib/ISOLINUX/isolinux.bin
else
    printf '  MISS  %-22s paket: %s\n' isolinux.bin isolinux
    MISSING_BUILD+=("isolinux")
fi
if [ -d /usr/lib/syslinux/modules/bios ]; then
    printf '  OK    %-22s %s\n' syslinux-modules /usr/lib/syslinux/modules/bios
else
    printf '  MISS  %-22s paket: %s\n' syslinux-modules syslinux-common
    MISSING_BUILD+=("syslinux-common")
fi
if [ -d /usr/lib/grub/x86_64-efi ]; then
    printf '  OK    %-22s %s\n' grub-efi-modules /usr/lib/grub/x86_64-efi
else
    printf '  MISS  %-22s paket: %s\n' grub-efi-modules grub-efi-amd64-bin
    MISSING_BUILD+=("grub-efi-amd64-bin")
fi

printf '\nTool test:\n'
check_command qemu-system-x86_64 qemu-system-x86 test
check_command qemu-img qemu-utils test

printf '\nTool opsional:\n'
for tool in shellcheck minisign git rsync; do
    if have "$tool"; then
        printf '  OK    %-22s %s\n' "$tool" "$(command -v "$tool")"
    else
        printf '  WARN  %-22s tidak terpasang\n' "$tool"
    fi
done

printf '\nFirmware UEFI:\n'
OVMF_CODE=""
OVMF_VARS=""
for pair in \
    "/usr/share/OVMF/OVMF_CODE_4M.fd:/usr/share/OVMF/OVMF_VARS_4M.fd" \
    "/usr/share/OVMF/OVMF_CODE.fd:/usr/share/OVMF/OVMF_VARS.fd" \
    "/usr/share/edk2/ovmf/OVMF_CODE.fd:/usr/share/edk2/ovmf/OVMF_VARS.fd"; do
    code="${pair%%:*}"
    vars="${pair##*:}"
    if [ -f "$code" ] && [ -f "$vars" ]; then
        OVMF_CODE="$code"
        OVMF_VARS="$vars"
        break
    fi
done

if [ -n "$OVMF_CODE" ]; then
    printf '  OK    OVMF code %s\n' "$OVMF_CODE"
    printf '  OK    OVMF vars %s\n' "$OVMF_VARS"
else
    printf '  MISS  OVMF firmware, paket: ovmf\n'
    MISSING_TEST+=("ovmf")
fi

printf '\nSumber daya:\n'
memory_mib="$(awk '/MemTotal/ {printf "%d", $2 / 1024}' /proc/meminfo)"
printf '  RAM    %s MiB\n' "$memory_mib"
if [ "$memory_mib" -lt 8192 ]; then
    WARNINGS+=("RAM kurang dari 8 GiB. Build dapat gagal atau sangat lambat.")
fi

disk_mib="$(df -Pm "$ROOT" | awk 'NR==2 {print $4}')"
printf '  Disk   %s MiB bebas di %s\n' "$disk_mib" "$ROOT"
if [ "$disk_mib" -lt 25600 ]; then
    WARNINGS+=("Ruang disk kurang dari 25 GiB. Build amd64 dapat membutuhkan 15 sampai 25 GiB.")
fi

cpus="$(nproc)"
printf '  CPU    %s thread\n' "$cpus"
if [ "$cpus" -lt 2 ]; then
    WARNINGS+=("CPU kurang dari 2 thread. Build akan lambat.")
fi

if [ -r /dev/kvm ] && [ -w /dev/kvm ]; then
    printf '  KVM    tersedia\n'
else
    printf '  KVM    tidak tersedia, QEMU akan memakai TCG dan lambat\n'
    WARNINGS+=("Akses /dev/kvm tidak tersedia.")
fi

if grep -q '^squashfs$' /proc/filesystems 2>/dev/null; then
    printf '  FS     squashfs tersedia\n'
else
    printf '  FS     squashfs tidak terdeteksi\n'
    WARNINGS+=("Kernel tidak melaporkan squashfs. Muat modul squashfs.")
fi

if [ -e /dev/loop-control ]; then
    printf '  Loop   /dev/loop-control tersedia\n'
else
    WARNINGS+=(" /dev/loop-control tidak tersedia. Build mungkin membutuhkan modul loop.")
fi

if [ -n "${APT_PROXY:-}" ]; then
    printf '\nAPT proxy: %s\n' "$APT_PROXY"
    if have apt-cacher-ng; then
        printf '  OK    apt-cacher-ng terpasang\n'
    else
        WARNINGS+=("APT_PROXY diset tetapi apt-cacher-ng tidak terdeteksi di host.")
    fi
fi

printf '\n'
if [ "${#MISSING_BUILD[@]}" -gt 0 ] || [ "${#MISSING_TEST[@]}" -gt 0 ]; then
    printf 'Paket yang perlu dipasang:\n'
    printf '  sudo apt update\n'
    printf '  sudo apt install -y live-build debootstrap xorriso squashfs-tools \\\n'
    printf '    isolinux syslinux-common syslinux-utils syslinux-efi \\\n'
    printf '    grub-pc-bin grub-efi-amd64-bin mtools dosfstools \\\n'
    printf '    qemu-system-x86 qemu-utils ovmf apt-cacher-ng shellcheck\n'
    printf '\n'
fi

if [ "${#WARNINGS[@]}" -gt 0 ]; then
    printf 'Peringatan:\n'
    for warning in "${WARNINGS[@]}"; do
        printf '  - %s\n' "$warning"
    done
    printf '\n'
fi

if [ "${#MISSING_BUILD[@]}" -eq 0 ] && [ "${#MISSING_TEST[@]}" -eq 0 ]; then
    printf 'Status: siap membangun dan menguji ISO.\n'
    exit 0
fi

if [ "$STRICT" -eq 1 ]; then
    printf 'Status: GAGAL, ada tool wajib yang hilang.\n' >&2
    exit 1
fi

printf 'Status: belum siap, tetapi mode advisory tidak menggagalkan pemeriksaan.\n'
exit 0
