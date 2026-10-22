# ArashiOS

ArashiOS adalah distribusi Linux berbasis Debian 12 bookworm untuk pekerjaan red team, pengembangan perangkat lunak, dan penggunaan harian. Prioritas produk: keamanan lebih dulu, coding kedua, kenyamanan harian ketiga.

Nama Arashi berarti badai. Arah visual Kage memakai minimalisme Jepang, ruang kosong yang disengaja, dan aksen vermilion yang terukur. Tidak ada telemetry, tidak ada akun online, dan tidak ada repository pihak ketiga permanen pada sistem terpasang.

## Status

| Fase | Isi | Status |
|---|---|---|
| 0 | Fondasi repository, kebijakan, ADR, design token, CI | Selesai, dua butir eksternal terbuka |
| 1 | Baseline live ISO amd64, branding, smoke test, QEMU harness | Implementasi selesai, menunggu build host |
| 2 | Tema desktop penuh dan integrasi Kage | Implementasi statis selesai, validasi runtime menunggu ISO |
| 3 | Tiga edisi desktop dan matriks QA | Integrasi statis selesai, QA runtime menunggu ISO |
| 4 | Arsenal tool keamanan, termasuk tool vendored | Implementasi statis selesai, artefak T1 dan runtime menunggu ISO |
| 5 | Toolchain coding lengkap dan container | Implementasi statis selesai, runtime menunggu ISO |
| 6 | Aplikasi harian, jaringan, audio, daya, cetak, dan locale | Implementasi statis selesai, QA hardware menunggu ISO |
| 7 | Calamares, enkripsi, persistence, dan recovery | Implementasi statis selesai, skenario instalasi menunggu ISO |
| 8 | Update, repository, dan mirror | Direncanakan |
| 9 | Hardening rilis, signing, dan supply chain | Direncanakan |
| 10 | arm64, i386, dan aksesibilitas | Direncanakan |
| 11 | Dokumentasi publik, situs, dan komunitas | Direncanakan |
| 12 | RC, rilis, dan pemeliharaan | Direncanakan |

Fase 1 menargetkan ISO live yang dapat boot pada QEMU UEFI dan BIOS. Fase 2 dan Fase 3 sudah memiliki tema, paket branding, dan konfigurasi tiga desktop pada tingkat statis. Fase 4 dan Fase 5 menambahkan katalog tool 215 entri, 41 manifest tool tier 1 dengan sumber terkunci, Arsenal, wordlist, toolchain user level dengan checksum, template proyek, dan container rootless pada tingkat statis. Installer Calamares, artefak binary tier 1, signing produksi, dan validasi boot belum aktif. Rencana lengkap ada di [plan.md](plan.md). Status terperinci ada di [laporan Fase 0 dan 1](docs/PHASE-0-1-REPORT.md), [laporan Fase 2 dan 3](docs/PHASE-2-3-REPORT.md), dan [laporan Fase 4 dan 5](docs/PHASE-4-5-REPORT.md).

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

Setiap artefak memiliki checksum SHA-256 dan SHA-512. Build wrapper mendukung tanda tangan minisign opsional; signing produksi diaktifkan pada Fase 9.

## Prasyarat Build

Host build yang didukung adalah Debian 12 atau turunan Debian yang kompatibel. Host LMDE 7 dengan basis Debian 13 dapat dipakai untuk pengembangan, tetapi hasil build harus diuji pada QEMU dan, untuk rilis, pada host Debian 12 yang bersih.

Perangkat minimum:

- 4 core CPU
- 8 GB RAM, 16 GB lebih baik
- 25 GB ruang disk kosong
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
make theme
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

Validasi konfigurasi semua kombinasi:

```bash
make config-matrix
```

Pemeriksaan tema, desktop, toolstack, dan coding:

```bash
make theme-check
make desktop-check
make package-check
make toolstack-check
make coding-check
```

Lint dan validasi statis:

```bash
make lint
```

`make lint` menghasilkan ulang tema, menjalankan shellcheck, pemeriksaan sintaks Python, pemeriksaan dokumen, traceability requirement, validasi token, validasi konfigurasi live-build, parser CSS GTK3 dan GTK4, pemeriksaan desktop, pemeriksaan paket branding, pemeriksaan toolstack, dan pemeriksaan lingkungan coding. `make package` membangun paket branding lokal secara terpisah.

## Penggunaan Harian dan Installer

```bash
arashios-daily                 diagnosis jaringan, audio, daya, cetak, locale, firmware
arashios-hardware-report        laporan QA hardware dalam JSON atau Markdown
arashios-dualboot-check         pemeriksaan Windows, BitLocker, Fast Startup, Secure Boot
arashios-persistence            partisi persistensi untuk sesi live
arashios-recovery               mount, LUKS, LVM, GRUB, dan pemulihan EFI
```

Installer memakai Calamares dengan branding Kage, enkripsi LUKS2, partisi EFI
512 MiB, dan-ext4 sebagai filesystem bawaan. Modul LVM disiapkan manual
karena Calamares 3.2 belum menyediakannya, dan langkahnya terdokumentasi di
[docs/INSTALL.md](docs/INSTALL.md).

## Toolstack dan Arsenal

Katalog tool adalah sumber kebenaran tunggal di `tools/catalog.yaml`. Katalog
runtime, manifest per tool, dan katalog toolchain dibuat dari berkas itu.

```bash
arashios-arsenal list --workflow WF-05
arashios-arsenal info nuclei
arashios-arsenal verify --tier T1 --strict
arashios-arsenal doctor
arashios-tool-smoke --tier T0 --output build/toolstack-smoke.json
```

Arsenal memasang tool tier 0 dari Debian, tool tier 1 dari cache vendor dengan
verifikasi checksum, tool tier 2 secara manual, dan tool tier 3 sebagai
container dengan digest terkunci. Tidak ada repository pihak ketiga yang
ditambahkan ke sistem terpasang.

## Lingkungan Coding

```bash
arashios-toolchain list
arashios-toolchain install uv
arashios-new-project create python ~/proyek/analisis
arashios-coding-smoke
arashios-container build python
```

Toolchain user level dipasang tanpa sudo ke `~/.local/share/arashios` dan
setiap unduhan diverifikasi dengan checksum yang dikunci di
`toolchains/lock.yaml`.

## Struktur Repository

```text
.
├── branding/                 Logo, wallpaper, GRUB, Plymouth, token, template tema
├── config/
│   ├── arches/               Overlay paket khusus arsitektur
│   ├── common/               Paket, archive, include, hook bersama
│   └── editions/             Overlay Cinnamon, XFCE, LXQt
├── docs/                     Arsitektur, build, desain, legal, ADR, laporan fase
├── tools/                    Katalog tool dan pin sumber upstream
├── toolchains/               Katalog toolchain user level dan lock checksum
├── vendor/                   Manifest tool tier 1 per tool
├── scripts/                  Generator token, aset, tema, validator, pemeriksaan host
├── tests/                    QEMU harness, verifikasi artefak, smoke test, tema, paket
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

Aset raster GRUB, Plymouth, dan wallpaper dihasilkan oleh `scripts/generate-brand-assets.py` agar tidak bergantung pada renderer SVG di host. Tema GTK2, GTK3, GTK4, Cinnamon, Muffin dan Metacity, XFCE, Openbox, dan Kvantum dihasilkan oleh `scripts/generate-theme.py` dari template dan token yang sama. Semua tema dikemas dalam paket lokal `arashios-branding`.

## Keamanan

- Tidak ada telemetry dan tidak ada panggilan jaringan otomatis ke server proyek.
- Tidak ada repository Kali permanen pada sistem terpasang.
- `openssh-server` tidak dipasang dan unit SSH dimask.
- UFW aktif dengan kebijakan deny incoming dan allow outgoing.
- AppArmor aktif.
- sysctl hardening diterapkan melalui `/etc/sysctl.d/99-arashios-hardening.conf`.
- Autologin hanya untuk sesi live. Calamares akan menghapus konfigurasi autologin pada Fase 7.
- Tool yang membutuhkan repository pihak ketiga di-vendor dengan manifest, commit terkunci, dan checksum. Daftar tool yang boleh masuk image ada di `tools/catalog.yaml`.

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
- [Laporan Fase 2 dan 3](docs/PHASE-2-3-REPORT.md)
- [Integrasi desktop](docs/DESKTOP.md)
- [Toolstack keamanan](docs/TOOLSTACK.md)
- [Arsenal](docs/ARSENAL.md)
- [Lingkungan coding](docs/CODING.md)
- [Container dan lab](docs/CONTAINERS.md)
- [Kebijakan vendoring](docs/VENDORING.md)
- [Matriks lisensi](docs/LICENSES.md)
- [Penggunaan harian](docs/DAILY.md)
- [Dukungan hardware](docs/HARDWARE.md)
- [Panduan instalasi](docs/INSTALL.md)
- [Persistensi sesi live](docs/PERSISTENCE.md)
- [Pemulihan sistem](docs/RECOVERY.md)
- [Laporan Fase 6 dan 7](docs/PHASE-6-7-REPORT.md)
- [Laporan Fase 4 dan 5](docs/PHASE-4-5-REPORT.md)
- [Architecture Decision Records](docs/adr/README.md)
- [Kontribusi](CONTRIBUTING.md)
- [Kode etik](CODE_OF_CONDUCT.md)
- [Changelog](CHANGELOG.md)

## Batasan Saat Ini

- Build yang divalidasi adalah amd64. arm64 dan i386 disiapkan pada konfigurasi dan diuji pada Fase 10.
- ISO belum dibangun pada host ini karena toolchain `lb`, `debootstrap`, `xorriso`, dan QEMU belum tersedia.
- Boot GRUB, Plymouth, LightDM, login desktop, panel XFCE, Openbox, dan rendering Kvantum belum diuji pada sesi nyata.
- Installer Calamares sudah dikonfigurasi dengan branding Kage, tetapi belum dijalankan karena ISO belum dibangun.
- Checklist hardware tiga mesin dan skenario instalasi belum dijalankan.
- Artefak binary tool T1 belum dibangun, sehingga `artifact.sha256` pada manifest masih kosong.
- Signing produksi belum aktif.
- Repository ArashiOS dan mekanisme update mandiri belum aktif.
- Pengujian dilakukan pada QEMU. Uji perangkat keras nyata masuk checklist RC.

## Lisensi

GPL-3.0-or-later untuk kode. CC-BY-SA-4.0 untuk aset visual. CC-BY-4.0 untuk dokumentasi. Lihat [LICENSE](LICENSE) dan [docs/LEGAL.md](docs/LEGAL.md).
