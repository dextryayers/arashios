# ArashiOS

ArashiOS adalah distribusi Linux berbasis Debian 12 bookworm untuk pekerjaan red team, pengembangan perangkat lunak, dan penggunaan harian. Prioritas produk: keamanan lebih dulu, coding kedua, kenyamanan harian ketiga.

Nama Arashi berarti badai. Arah visual Kage memakai minimalisme Jepang, ruang kosong yang disengaja, dan aksen vermilion yang terukur. Tidak ada telemetry, tidak ada akun online, dan tidak ada repository pihak ketiga permanen pada sistem terpasang.

## Status

| Fase | Isi | Status |
|---|---|---|
| 0 | Fondasi repository, kebijakan, ADR, design token, CI | Selesai |
| 1 | Baseline live ISO amd64, branding, smoke test, QEMU harness | Implementasi selesai, menunggu build host |
| 2 | Tema desktop penuh dan integrasi Kage | Berikutnya |
| 3 | Tiga edisi desktop dan matriks QA | Direncanakan |
| 4 | Arsenal tool keamanan, termasuk tool vendored | Direncanakan |
| 5 | Toolchain coding lengkap dan container | Direncanakan |
| 6 | Aplikasi harian dan printer | Direncanakan |
| 7 | Calamares, enkripsi, persistence, recovery | Direncanakan |
| 8 | Update, repository, dan mirror | Direncanakan |
| 9 | Hardening rilis, signing, dan supply chain | Direncanakan |
| 10 | arm64, i386, dan aksesibilitas | Direncanakan |
| 11 | Dokumentasi publik, situs, dan komunitas | Direncanakan |
| 12 | RC, rilis, dan pemeliharaan | Direncanakan |

Fase 1 menghasilkan ISO live yang dapat boot pada QEMU UEFI dan BIOS. Installer Calamares, tool vendored, dan signing produksi belum aktif. Rencana lengkap ada di [plan.md](plan.md).

## Edisi

| Edisi | Posisi | Arsitektur default | Target sumber daya |
|---|---|---|---|
| Cinnamon | Flagship, pengalaman lengkap | amd64 | 4 GB RAM, 20 GB disk |
| XFCE | Ringan, stabil, cocok untuk VM | arm64 | 2 GB RAM, 15 GB disk |
| LXQt | Paling ringan untuk perangkat lama | i386 | 1 GB RAM, 12 GB disk |

Edisi default per arsitektur tidak memakai sufiks pada nama ISO. Edisi non-default memakai sufiks `-xfce` atau `-lxqt`.

## Artefak

Pola nama:

```text
ArashiOS-<arch>-<version>[-<edition>].iso
```

Contoh:

```text
ArashiOS-amd64-V1.10.21.iso
ArashiOS-amd64-V1.10.21-xfce.iso
ArashiOS-amd64-V1.10.21-lxqt.iso
ArashiOS-arm64-V1.10.21.iso
ArashiOS-arm64-V1.10.21-lxqt.iso
ArashiOS-i386-V1.10.21.iso
ArashiOS-i386-V1.10.21-xfce.iso
```

Setiap artefak memiliki checksum SHA-256 dan SHA-512. Tanda tangan minisign disiapkan pada pipeline dan diaktifkan pada Fase 9.

## Prasyarat Build

Host build yang didukung adalah Debian 12 atau turunan Debian yang kompatibel. Host LMDE 7 dengan basis Debian 13 dapat dipakai untuk pengembangan, tetapi hasil build harus diuji pada QEMU dan, untuk rilis, pada host Debian 12 yang bersih.

Perangkat minimum:

- 4 core CPU
- 8 GB RAM, 16 GB lebih baik
- 30 GB ruang disk kosong
- Koneksi internet untuk mirror Debian
- Akses `/dev/kvm` untuk pengujian QEMU

Pasang toolchain:

```bash
sudo apt update
sudo apt install -y \
  live-build debootstrap xorriso squashfs-tools \
  isolinux syslinux-common syslinux-utils syslinux-efi \
  grub-pc-bin grub-efi-amd64-bin mtools dosfstools \
  qemu-system-x86 qemu-utils ovmf apt-cacher-ng shellcheck
```

Periksa host:

```bash
make env
make env-strict
```

`make env` bersifat advisory. `make env-strict` gagal jika tool build atau test wajib belum tersedia.

## Build Cepat

```bash
make tokens
make config EDITION=xfce ARCH=amd64
make build EDITION=cinnamon ARCH=amd64 JOBS=8
```

Hasil build:

```text
out/ArashiOS-amd64-V1.10.21.iso
out/ArashiOS-amd64-V1.10.21.iso.sha256
out/ArashiOS-amd64-V1.10.21.iso.sha512
```

Build memakai `live-build` dengan image `iso-hybrid`, squashfs, `syslinux` untuk BIOS, dan `grub-efi` untuk UEFI. Kernel default mengikuti Debian bookworm. Backports tersedia tetapi tidak dipakai untuk upgrade otomatis.

Perkiraan waktu build pada 8 core dan cache kosong: 25 sampai 50 menit. Build berikutnya dengan cache paket lebih cepat.

## Opsi Build

```bash
./build.sh --edition <cinnamon|xfce|lxqt> --arch <amd64|arm64|i386> [opsi]
```

| Opsi | Keterangan |
|---|---|
| `--edition` | Edisi desktop. Wajib. |
| `--arch` | Arsitektur target. Wajib. |
| `--version` | Versi rilis, default dari `versions.env`. |
| `--jobs` | Jumlah proses `mksquashfs`, default jumlah CPU. |
| `--dry-run` | Menyiapkan konfigurasi live-build tanpa membangun ISO. |

Variabel lingkungan:

| Variabel | Fungsi |
|---|---|
| `APT_PROXY` | Proxy APT, contoh `http://127.0.0.1:3142`. |
| `DEBIAN_SNAPSHOT` | Timestamp snapshot.debian.org untuk build yang dapat direproduksi. |
| `SOURCE_DATE_EPOCH` | Timestamp metadata build. |
| `MINISIGN_KEY` | Path kunci minisign untuk menandatangani ISO. |

Contoh snapshot:

```bash
DEBIAN_SNAPSHOT=20261020T000000Z make build EDITION=xfce ARCH=amd64
```

Snapshot utama dipakai untuk bootstrap, chroot, dan binary. Arsip keamanan tetap memakai mirror aktif sampai mirror snapshot keamanan dikonfigurasi pada Fase 9.

## Pengujian

Verifikasi artefak:

```bash
make verify ISO=out/ArashiOS-amd64-V1.10.21.iso
```

Uji boot QEMU:

```bash
make test ISO=out/ArashiOS-amd64-V1.10.21.iso BOOT_MODE=uefi
make test ISO=out/ArashiOS-amd64-V1.10.21.iso BOOT_MODE=bios
```

Harness QEMU mengambil screenshot PPM dan log serial ke `out/`. Uji ini memeriksa bahwa ISO masuk ke sistem grafis, tidak mengalami kernel panic, dan tidak berhenti pada firmware.

Smoke test dijalankan di dalam sesi live sebagai user `arashi`:

```bash
arashios-smoke
```

Smoke test memeriksa identitas sistem, branding, layanan, sysctl hardening, repository, locale, tool keamanan, tool coding, aplikasi harian, desktop, dan container rootless.

Lint dan validasi statis:

```bash
make lint
```

`make lint` menjalankan shellcheck, pemeriksaan sintaks Python, pemeriksaan dokumen, traceability requirement, validasi token, dan validasi konfigurasi live-build. Token dan aset raster harus sudah dihasilkan dengan `make tokens`.

## Struktur Repository

```text
.
├── branding/                 Logo, wallpaper, GRUB, Plymouth, token
├── config/
│   ├── arches/               Overlay paket khusus arsitektur
│   ├── common/               Paket, archive, include, hook bersama
│   └── editions/             Overlay Cinnamon, XFCE, LXQt
├── docs/                     Arsitektur, build, desain, legal, ADR
├── scripts/                  Generator, validator, pemeriksaan host
├── tests/                    QEMU harness, verifikasi artefak, smoke test
├── build.sh                  Wrapper live-build
├── Makefile                  Target harian
├── plan.md                   Sumber kebenaran scope dan fase
└── versions.env              Versi, arsitektur, batas ukuran ISO
```

## Design System Kage

Token desain berada di `branding/tokens.json`. Generator menghasilkan CSS, SCSS, QSS, laporan kontras, dan preview HTML:

```bash
./scripts/generate-tokens.py
```

Kontras dihitung otomatis. Build gagal jika pasangan warna berada di bawah ambang WCAG yang ditetapkan. Palet inti:

| Token | Nilai | Penggunaan |
|---|---:|---|
| Sumi 800 | `#0A0A0C` | Latar utama |
| Washi 100 | `#EDE8DE` | Teks utama |
| Ash 400 | `#8B867D` | Teks sekunder |
| Ember 500 | `#DD785B` | Aksen dan link |
| Vermilion 500 | `#BF4432` | Aksen kuat dan seal |

Aset raster GRUB dan Plymouth dihasilkan oleh `scripts/generate-brand-assets.py` agar tidak bergantung pada renderer SVG di host.

## Keamanan

- Tidak ada telemetry dan tidak ada panggilan jaringan otomatis ke server proyek.
- Tidak ada repository Kali permanen pada sistem terpasang.
- `openssh-server` tidak dipasang dan unit SSH dimask.
- UFW aktif dengan kebijakan deny incoming dan allow outgoing.
- AppArmor aktif.
- sysctl hardening diterapkan melalui `/etc/sysctl.d/99-arashios-hardening.conf`.
- Autologin hanya untuk sesi live. Calamares akan menghapus konfigurasi autologin pada Fase 7.
- Tool yang membutuhkan repository pihak ketiga akan di-vendor dengan manifest dan checksum pada Fase 4.

Laporkan kerentanan melalui prosedur di [SECURITY.md](SECURITY.md). Jangan membuka issue publik untuk kerentanan yang belum diperbaiki.

## Privasi dan Legal

- [Kebijakan privasi](docs/PRIVACY.md)
- [Legal dan kepatuhan](docs/LEGAL.md)
- [Merek dagang](docs/TRADEMARK.md)

Kode berlisensi GPL-3.0-or-later. Aset visual berlisensi CC-BY-SA-4.0. Dokumentasi berlisensi CC-BY-4.0. Paket Debian dan tool pihak ketiga tetap memakai lisensi masing-masing.

## Dokumentasi

- [Rencana induk](plan.md)
- [Build](docs/BUILD.md)
- [Arsitektur](docs/ARCHITECTURE.md)
- [Desain](docs/DESIGN.md)
- [Laporan Fase 0 dan 1](docs/PHASE-0-1-REPORT.md)
- [Architecture Decision Records](docs/adr/README.md)
- [Kontribusi](CONTRIBUTING.md)
- [Kode etik](CODE_OF_CONDUCT.md)
- [Changelog](CHANGELOG.md)

## Batasan Fase 1

- Build yang divalidasi adalah amd64. arm64 dan i386 disiapkan pada konfigurasi dan diuji pada Fase 10.
- Calamares belum tersedia, sehingga ISO hanya berjalan sebagai live session.
- Tool T1, T2, dan T3 belum di-vendor.
- Tema desktop masih memakai basis Adwaita dan Papirus. Tema Kage penuh dikerjakan pada Fase 2.
- Signing produksi belum aktif.
- Repository ArashiOS dan mekanisme update mandiri belum aktif.
- Pengujian dilakukan pada QEMU. Uji perangkat keras nyata masuk checklist RC.

## Lisensi

GPL-3.0-or-later untuk kode. CC-BY-SA-4.0 untuk aset visual. CC-BY-4.0 untuk dokumentasi. Lihat [LICENSE](LICENSE) dan [docs/LEGAL.md](docs/LEGAL.md).
