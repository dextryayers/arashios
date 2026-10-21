# ArashiOS

Distribusi Linux berbasis Debian 12 (bookworm) untuk red team, coding, dan penggunaan harian. Tiga edisi desktop: Cinnamon, XFCE, LXQt. Design system: Kage.

Status: Fase 0 sampai 2 dalam pengerjaan. ISO belum dirilis.

## Prasyarat

Host build: Debian 12 atau turunannya, 16 GB RAM, 25 GB ruang disk, akses KVM untuk pengujian.

```bash
sudo apt update
sudo apt install -y live-build debootstrap xorriso squashfs-tools \
  isolinux syslinux-common syslinux-efi grub-pc-bin grub-efi-amd64-bin \
  mtools dosfstools qemu-system-x86 qemu-utils ovmf apt-cacher-ng \
  shellcheck python3
```

## Build

```bash
./scripts/check-env.sh
./build.sh --edition cinnamon --arch amd64
```

Hasil ada di `out/ArashiOS-amd64-V1.10.21.iso` beserta checksum.

Edisi dan arsitektur yang didukung:

| Edisi | amd64 | arm64 | i386 |
|---|---|---|---|
| Cinnamon | Tier 1 | - | - |
| XFCE | Tier 1 | Tier 1 | Tier 3 |
| LXQt | Tier 1 | Tier 2 | Tier 3 |

## Uji

```bash
./tests/qemu-boot.sh out/ArashiOS-amd64-V1.10.21.iso uefi
./tests/qemu-boot.sh out/ArashiOS-amd64-V1.10.21.iso bios
./tests/verify-artifact.sh out/ArashiOS-amd64-V1.10.21.iso
```

## Struktur

```
config/common        konfigurasi lintas edisi
config/editions      overlay per desktop
branding             logo, wallpaper, GRUB, Plymouth, LightDM
packages             paket .deb ArashiOS
vendor               paket dan binari pihak ketiga yang dikunci
scripts              utilitas build dan validasi
tests                uji boot QEMU dan verifikasi artefak
docs                 arsitektur, desain, QA, keamanan
```

## Dokumen

Rencana lengkap ada di [plan.md](plan.md). Dokumen teknis ada di [docs/](docs/).

## Lisensi

Kode: GPL-3.0-or-later. Aset visual: CC-BY-SA-4.0. Dokumentasi: CC-BY-4.0.
