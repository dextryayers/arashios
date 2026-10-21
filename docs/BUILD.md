# Panduan Build ArashiOS

Dokumen ini menjelaskan cara menyiapkan host, membangun ISO, memverifikasi artefak, dan menjalankan pengujian Fase 1. Panduan ini ditulis untuk build amd64. arm64 dan i386 memakai konfigurasi yang sama, tetapi validasi penuh dilakukan pada Fase 10.

## 1. Status

| Butir | Status |
|---|---|
| Pipeline `live-build` | Selesai |
| Konfigurasi common, edisi, arsitektur | Selesai |
| Build ISO amd64 | Belum dijalankan pada host ini |
| Verifikasi artefak | Selesai, menunggu ISO |
| QEMU UEFI dan BIOS | Selesai, menunggu ISO |
| Smoke test runtime | Selesai, menunggu sesi live |
| Installer Calamares | Belum, Fase 7 |
| Signing produksi | Belum, Fase 9 |

Klaim build dan boot hanya boleh dibuat setelah `make build`, `make verify`, dan `make test` lulus pada host Debian 12 yang bersih.

## 2. Host yang Didukung

| Komponen | Minimum | Disarankan |
|---|---|---|
| Distribusi host | Debian 12 bookworm | Debian 12 bersih |
| CPU | 4 core | 8 core atau lebih |
| RAM | 8 GiB | 16 GiB |
| Disk kosong | 25 GiB | 40 GiB |
| Koneksi | Mirror Debian | Mirror lokal atau apt-cacher-ng |
| Virtualisasi | Tidak wajib untuk build | `/dev/kvm` untuk uji QEMU |

Host turunan Debian seperti LMDE 7 dapat dipakai untuk pengembangan, tetapi bukan acuan rilis. Perbedaan versi `live-build`, `debootstrap`, dan `xorriso` dapat mengubah isi ISO. Build rilis harus mencatat versi host pada `/etc/arashios/build-info`.

## 3. Toolchain Host

| Paket | Perintah | Fungsi |
|---|---|---|
| `live-build` | `lb` | Menyusun config, chroot, squashfs, ISO |
| `debootstrap` | `debootstrap` | Membuat rootfs Debian |
| `xorriso` | `xorriso` | Menulis ISO 9660 dan El Torito |
| `squashfs-tools` | `mksquashfs` | Kompresi rootfs |
| `isolinux` | `isolinux.bin` | Bootloader BIOS |
| `syslinux-common` | modul syslinux | Modul BIOS |
| `syslinux-utils` | `isohybrid` | MBR hybrid ISO |
| `syslinux-efi` | modul EFI syslinux | Dukungan EFI opsional |
| `grub-pc-bin` | modul GRUB BIOS | Cadangan boot BIOS |
| `grub-efi-amd64-bin` | modul GRUB EFI | Bootloader UEFI amd64 |
| `mtools` | `mcopy` | Menyalin berkas ke image FAT EFI |
| `dosfstools` | `mkfs.vfat` | Membuat filesystem EFI |
| `qemu-system-x86` | `qemu-system-x86_64` | Uji boot UEFI dan BIOS |
| `qemu-utils` | `qemu-img` | Utilitas image |
| `ovmf` | firmware OVMF | UEFI virtual |
| `apt-cacher-ng` | `apt-cacher-ng` | Cache paket opsional |
| `shellcheck` | `shellcheck` | Lint shell |

Pasang:

```bash
sudo apt update
sudo apt install -y \
  live-build debootstrap xorriso squashfs-tools \
  isolinux syslinux-common syslinux-utils syslinux-efi \
  grub-pc-bin grub-efi-amd64-bin mtools dosfstools \
  qemu-system-x86 qemu-utils ovmf apt-cacher-ng shellcheck
```

Verifikasi:

```bash
./scripts/check-env.sh
./scripts/check-env.sh --strict
./scripts/check-env.sh --release
```

`check-env.sh` memeriksa perintah, modul bootloader, firmware OVMF, RAM, disk, CPU, KVM, squashfs, dan loop device. Mode `--strict` keluar dengan status 1 jika tool wajib hilang. Mode `--release` juga mewajibkan host Debian 12 bookworm dan dipakai oleh workflow rilis.

## 4. Cache Paket Opsional

apt-cacher-ng mempercepat build berulang dan mengurangi beban mirror.

```bash
sudo systemctl enable --now apt-cacher-ng
```

Build memakai cache:

```bash
APT_PROXY=http://127.0.0.1:3142 make build EDITION=cinnamon ARCH=amd64
```

Aturan cache:

1. Cache hanya untuk mirror Debian tepercaya.
2. Jangan mengarahkan cache ke repository pihak ketiga.
3. Bersihkan cache setiap 30 hari.
4. Build rilis sebaiknya memakai cache kosong atau snapshot untuk memastikan input dapat direproduksi.

## 5. Build Cepat

```bash
# 1. Periksa host
make env

# 2. Hasilkan token dan aset brand
make tokens

# 3. Validasi konfigurasi tanpa membangun ISO
make config EDITION=cinnamon ARCH=amd64

# 4. Build ISO
make build EDITION=cinnamon ARCH=amd64 JOBS=8
```

Output:

```text
out/ArashiOS-amd64-V1.10.21.iso
out/ArashiOS-amd64-V1.10.21.iso.sha256
out/ArashiOS-amd64-V1.10.21.iso.sha512
```

Log build:

```text
build/cinnamon-amd64/build.log
```

Perkiraan waktu:

| Kondisi | Waktu |
|---|---|
| Cache kosong, 8 core | 25 sampai 50 menit |
| Cache hangat, 8 core | 10 sampai 25 menit |
| Cache kosong, 4 core | 45 sampai 80 menit |

Jika waktu melebihi 90 menit, periksa mirror, cache, dan ruang disk.

## 6. Referensi Perintah

```bash
./build.sh --edition <cinnamon|xfce|lxqt> --arch <amd64|arm64|i386> [opsi]
```

| Opsi | Wajib | Default | Keterangan |
|---|---|---|---|
| `--edition` | Ya | Tidak ada | Edisi desktop |
| `--arch` | Ya | Tidak ada | Arsitektur target |
| `--version` | Tidak | `ARASHIOS_VERSION` | Versi rilis |
| `--jobs` | Tidak | `nproc` | Proses `mksquashfs` |
| `--dry-run` | Tidak | Mati | Siapkan config tanpa build |
| `-h`, `--help` | Tidak | | Bantuan |

Contoh:

```bash
# Konfigurasi saja
./build.sh --edition xfce --arch amd64 --dry-run

# Build edisi non-default
./build.sh --edition xfce --arch amd64

# Build i386
./build.sh --edition lxqt --arch i386 --jobs 4
```

`build.sh` menolak edisi, arsitektur, versi, dan jumlah job yang tidak valid. Build sebagai root memberi peringatan. Jalankan sebagai user biasa.

## 7. Variabel Lingkungan

| Variabel | Default | Fungsi |
|---|---|---|
| `APT_PROXY` | Kosong | Proxy APT, contoh `http://127.0.0.1:3142` |
| `DEBIAN_SNAPSHOT` | Kosong | Timestamp snapshot.debian.org |
| `SOURCE_DATE_EPOCH` | Waktu build | Timestamp metadata build |
| `MINISIGN_KEY` | Kosong | Kunci minisign untuk tanda tangan |
| `MKSQUASHFS_OPTIONS` | Diisi `build.sh` | Opsi tambahan `mksquashfs` |

Jika `MINISIGN_KEY` disetel, perintah `minisign` wajib tersedia. Build berhenti dengan pesan yang jelas bila perintah tersebut tidak ditemukan.

Contoh snapshot:

```bash
DEBIAN_SNAPSHOT=20261020T000000Z make build EDITION=xfce ARCH=amd64
```

Snapshot mengganti mirror bootstrap, chroot, dan binary. Arsip keamanan tetap memakai mirror aktif pada Fase 1. Untuk build rilis yang sepenuhnya terkunci, konfigurasi snapshot keamanan harus ditambahkan pada Fase 9.

Contoh timestamp tetap:

```bash
SOURCE_DATE_EPOCH=1792540800 make build EDITION=cinnamon ARCH=amd64
```

## 8. Pipeline Build

```text
1. Validasi argumen, versi, edisi, arsitektur, job
2. Periksa perintah wajib
3. Hapus dan buat build/<edition>-<arch>
4. lb config dengan opsi proyek
5. Salin config/common
6. Salin config/editions/<edition>
7. Salin config/arches/<arch> jika ada
8. Tulis /etc/arashios/{version,edition,arch,build-info}
9. Ganti placeholder os-release, lsb-release, issue
10. Generate token dan aset raster
11. Pasang branding, theme, dokumentasi, smoke test
12. lb build
13. Pindahkan ISO ke out/
14. Hitung SHA-256 dan SHA-512
15. Tanda tangan minisign jika kunci tersedia
```

Urutan overlay bersifat menimpa. File dengan nama sama di edisi akan menggantikan file common. File arsitektur menggantikan file edisi.

### 8.1 Metadata Build

`/etc/arashios/build-info` mencatat:

| Kunci | Isi |
|---|---|
| `ARASHIOS_VERSION` | Versi rilis |
| `ARASHIOS_CODENAME` | Nama kode, `Shizukesa` |
| `ARASHIOS_EDITION` | Edisi desktop |
| `ARASHIOS_ARCH` | Arsitektur |
| `ARASHIOS_DESIGN` | Nama design system |
| `DEBIAN_CODENAME` | `bookworm` |
| `DEBIAN_SNAPSHOT` | Snapshot atau `none` |
| `GIT_COMMIT` | Commit pendek |
| `BUILD_DATE` | Waktu UTC |
| `BUILD_JOBS` | Jumlah proses |
| `ISO_VOLUME` | Volume ID |
| `CONFIG_HASH` | Hash isi `config/`, `branding/`, `versions.env` |
| `HOST_OS` | Nama host |
| `HOST_KERNEL` | Kernel host |
| `HOST_ARCH` | Arsitektur host |
| `LIVE_BUILD_VERSION` | Versi `live-build` |

Metadata ini dapat dibaca dari sesi live:

```bash
cat /etc/arashios/build-info
```

## 9. Nama dan Edisi

| Arsitektur | Edisi default | Sufiks | Contoh |
|---|---|---|---|
| amd64 | Cinnamon | Tanpa sufiks | `ArashiOS-amd64-V1.10.21.iso` |
| amd64 | XFCE | `-xfce` | `ArashiOS-amd64-V1.10.21-xfce.iso` |
| amd64 | LXQt | `-lxqt` | `ArashiOS-amd64-V1.10.21-lxqt.iso` |
| arm64 | XFCE | Tanpa sufiks | `ArashiOS-arm64-V1.10.21.iso` |
| arm64 | LXQt | `-lxqt` | `ArashiOS-arm64-V1.10.21-lxqt.iso` |
| i386 | LXQt | Tanpa sufiks | `ArashiOS-i386-V1.10.21.iso` |
| i386 | XFCE | `-xfce` | `ArashiOS-i386-V1.10.21-xfce.iso` |

Volume ID dihitung dari versi:

```text
ARASHIOS_V1_10_21
```

Panjang volume ID dibatasi 32 karakter. Build gagal jika melebihi batas.

## 10. Verifikasi Artefak

```bash
make verify ISO=out/ArashiOS-amd64-V1.10.21.iso
```

Pemeriksaan:

1. Nama sesuai pola dan edisi default.
2. Ukuran tidak melebihi batas di `versions.env`.
3. Primary volume descriptor ISO 9660 ada.
4. Volume ID sesuai versi.
5. Direktori `/live` dan kernel atau initrd ada.
6. `isolinux.bin` ada untuk amd64 dan i386.
7. `BOOTX64.EFI`, `BOOTIA32.EFI`, atau `BOOTAA64.EFI` ada sesuai arsitektur.
8. Checksum SHA-256 dan SHA-512 cocok.
9. Tanda tangan minisign valid jika berkas `.sig` ada.

Batas ukuran:

| Edisi | Batas |
|---|---:|
| Cinnamon | 4300 MiB |
| XFCE | 4000 MiB |
| LXQt | 3600 MiB |

Batas ini adalah anggaran, bukan target. Jika ISO melebihi batas, audit paket dan pertimbangkan memindahkan tool ke Fase 4.

## 11. Uji Boot QEMU

```bash
make test ISO=out/ArashiOS-amd64-V1.10.21.iso BOOT_MODE=uefi
make test ISO=out/ArashiOS-amd64-V1.10.21.iso BOOT_MODE=bios
```

Atau langsung:

```bash
./tests/qemu-boot.sh out/ArashiOS-amd64-V1.10.21.iso uefi 120
./tests/qemu-boot.sh out/ArashiOS-amd64-V1.10.21.iso bios 120 --keep
```

Parameter:

| Parameter | Nilai | Default |
|---|---|---|
| ISO | Path ISO | Wajib |
| Mode | `uefi` atau `bios` | `uefi` |
| Timeout | Detik, minimal 20 | 120 |
| `--keep` | Simpan direktori sementara | Mati |

Perilaku:

1. Memilih OVMF yang tersedia pada host.
2. Menyalin `OVMF_VARS` agar firmware dapat menulis variabel.
3. Memakai KVM jika `/dev/kvm` dapat diakses.
4. Mematikan jaringan virtual.
5. Mengambil screenshot PPM melalui monitor QEMU.
6. Memeriksa log serial terhadap kernel panic dan boot failure.
7. Memeriksa screenshot tidak gelap total dan tidak kosong.

Output:

```text
out/qemu-amd64-uefi.ppm
out/qemu-amd64-uefi.log
```

Uji ini membuktikan firmware dapat memuat bootloader dan kernel serta mencapai layar grafis. Uji ini tidak membuktikan kompatibilitas perangkat keras, audio, Wi-Fi, atau suspend.

## 12. Smoke Test Runtime

Di dalam sesi live, jalankan sebagai user `arashi`:

```bash
arashios-smoke
```

Jangan jalankan sebagai root. Pemeriksaan Podman rootless akan gagal jika dijalankan sebagai root.

Cakupan:

1. Identitas sistem dan versi.
2. Berkas branding, tema, dan boot.
3. LightDM, NetworkManager, SSH, UFW, dan AppArmor.
4. sysctl hardening.
5. Tidak ada repository Kali.
6. Locale dan timezone.
7. Tool keamanan.
8. Tool coding.
9. Aplikasi harian.
10. Komponen desktop sesuai edisi.
11. Autologin live.
12. Skeleton dan dotfile.
13. Podman rootless dan user namespace.

Smoke test mengembalikan status 1 jika ada pemeriksaan gagal. Simpan output ke berkas untuk laporan:

```bash
arashios-smoke 2>&1 | tee ~/arashios-smoke.log
```

## 13. Lint dan Validasi

```bash
make lint
```

Perintah ini menjalankan:

1. `bash -n` untuk semua skrip shell.
2. `python3 -m py_compile` untuk generator.
3. `shellcheck -x` untuk semua skrip.
4. `scripts/check-docs.sh` untuk gaya dan tautan dokumentasi.
5. `scripts/check-traceability.py` untuk requirement dan test case.
6. `scripts/validate-config.sh` untuk struktur, paket, hook, metadata, token, dan SVG.

Validasi individual:

```bash
./scripts/check-docs.sh
./scripts/check-traceability.py
./scripts/validate-config.sh
./scripts/generate-tokens.py --check
./scripts/generate-brand-assets.py --check
```

Validasi konfigurasi `live-build` untuk semua kombinasi:

```bash
make config-matrix
```

Perintah ini menjalankan `build.sh --dry-run` untuk tujuh kombinasi di `SUPPORTED_COMBINATIONS`, lalu memeriksa `os-release`, metadata build, sesi LightDM, bootloader, dan kernel flavour. Perintah ini memerlukan `live-build` dan tidak memerlukan akses root.

## 14. Reproducibility

Reproducibility penuh belum aktif pada Fase 1. Yang sudah tersedia:

1. `SOURCE_DATE_EPOCH` untuk metadata build.
2. `DEBIAN_SNAPSHOT` untuk mirror utama.
3. `CONFIG_HASH` untuk melacak input konfigurasi.
4. Generator token dan aset yang deterministik.
5. Versi host dan `live-build` dicatat pada build-info.

Yang belum tersedia:

1. Normalisasi timestamp seluruh rootfs.
2. UUID ISO deterministik.
3. Snapshot arsip keamanan.
4. `diffoscope` antara dua build.
5. Signature dan attestation.

Jangan mengklaim reproducible build sebelum dua build pada host dan snapshot yang sama menghasilkan hash identik.

## 15. CI dan Rilis

CI berjalan pada push ke `main`, pull request, dan manual. Pekerjaan lint berjalan pada Ubuntu 24.04. Pekerjaan config matrix berjalan pada container Debian 12 dan menguji tujuh kombinasi arsitektur dan edisi yang didukung.

Release workflow berjalan manual pada self-hosted runner dengan label `arashios-builder`. Matriks rilis:

| Arsitektur | Edisi | Boot test |
|---|---|---|
| amd64 | Cinnamon | UEFI dan BIOS |
| amd64 | XFCE | UEFI dan BIOS |
| amd64 | LXQt | UEFI dan BIOS |
| arm64 | XFCE | Tidak ada |
| arm64 | LXQt | Tidak ada |
| i386 | LXQt | BIOS |
| i386 | XFCE | BIOS |

Setiap artefak diverifikasi sebelum diunggah. Release job menggabungkan checksum dan menerbitkan GitHub Release jika input `publish` bernilai true.

## 16. Troubleshooting

| Gejala | Kemungkinan penyebab | Tindakan |
|---|---|---|
| `lb: command not found` | live-build belum dipasang | Pasang `live-build` |
| `isohybrid: not found` | `syslinux-utils` belum dipasang | Pasang `syslinux-utils` |
| `mkfs.vfat: not found` | `dosfstools` belum dipasang | Pasang `dosfstools` |
| `mcopy: not found` | `mtools` belum dipasang | Pasang `mtools` |
| `grub-mkimage: not found` | `grub-common` belum dipasang | Pasang `grub-pc-bin` atau `grub-efi-amd64-bin` |
| Paket tidak ditemukan | Nama paket salah atau arsip tidak aktif | Periksa daftar paket dan komponen APT |
| Konflik dependency | Versi backports bercampur | Audit pinning dan paket backports |
| ISO tidak boot UEFI | Modul GRUB EFI hilang | Periksa `/usr/lib/grub/x86_64-efi` |
| ISO tidak boot BIOS | `isolinux.bin` hilang | Periksa paket `isolinux` |
| QEMU keluar sebelum timeout | Firmware atau ISO gagal dimuat | Jalankan dengan `--keep`, baca `qemu.err` |
| Screenshot gelap | Kernel panic atau driver grafis | Baca log serial, coba `nomodeset` |
| Build kehabisan disk | Cache dan workdir menumpuk | Hapus `build/`, cek `df -h` |
| Build lambat | Tidak ada cache | Aktifkan apt-cacher-ng |
| Smoke test Podman gagal | Dijalankan sebagai root | Jalankan sebagai user `arashi` |
| Smoke test AppArmor gagal | Profil tidak dimuat | Periksa `aa-status` dan unit `apparmor` |

Debug build:

```bash
tail -f build/cinnamon-amd64/build.log
```

Bersihkan:

```bash
make clean
```

`make clean` menghapus `build/` dan `out/`. Sumber, token, dan aset yang sudah di-commit tidak dihapus.

## 17. Menambah Paket

1. Tentukan edisi dan arsitektur.
2. Tambahkan nama paket Debian ke daftar yang sesuai.
3. Jangan menambahkan repository baru tanpa ADR.
4. Verifikasi ketersediaan paket pada bookworm:

```bash
apt-cache policy nama-paket
```

5. Jalankan `./scripts/validate-config.sh`.
6. Build ulang dan jalankan smoke test.
7. Catat perubahan di `CHANGELOG.md`.

Aturan penamaan paket:

1. Satu paket per baris.
2. Komentar memakai `#`.
3. Tidak ada wildcard.
4. Tidak ada paket dari repository Kali.
5. Paket yang hanya tersedia di backports harus diberi komentar dan alasan.

## 18. Menambah Edisi atau Arsitektur

Edisi baru memerlukan:

1. `config/editions/<nama>/package-lists/50-desktop.list.chroot`.
2. `config/editions/<nama>/includes.chroot/etc/lightdm/lightdm.conf.d/50-arashios.conf`.
3. Entri di `SUPPORTED_EDITIONS`, `DEFAULT_EDITION_*`, dan `SUPPORTED_COMBINATIONS` pada `versions.env`.
4. Matriks CI dan rilis.
5. Test case desktop baru.
6. Dokumentasi dan ADR jika mengubah keputusan produk.

Arsitektur baru memerlukan:

1. Overlay `config/arches/<arch>/`.
2. Kernel flavour dan bootloader di `build.sh`.
3. Validasi ketersediaan paket.
4. Harness boot QEMU atau perangkat nyata.
5. Entri di `SUPPORTED_ARCHES` dan `SUPPORTED_COMBINATIONS`.
6. Pembaruan traceability dan dokumentasi.

`build.sh` menolak kombinasi arsitektur dan edisi yang tidak tercantum di `SUPPORTED_COMBINATIONS`. Matriks rilis berisi tujuh artefak; Fase 1 membangun dan menguji amd64, sedangkan arm64 dan i386 divalidasi konfigurasinya dan dibangun pada Fase 10.

## 19. Keamanan Build

1. Build host harus bersih dan hanya dipakai untuk build.
2. Jangan menjalankan build sebagai root kecuali terpaksa.
3. Jangan menambahkan repository tanpa verifikasi kunci.
4. Periksa checksum artefak sebelum distribusi.
5. Tanda tangan produksi belum aktif. Jangan mengklaim ISO resmi sebelum Fase 9.
6. Simpan log build dan `build-info` untuk audit.
7. Tool vendored pada Fase 4 harus memiliki manifest, checksum, dan sumber.

## 20. Exit Gate Fase 1

| Kriteria | Status |
|---|---|
| ISO boot ke desktop di UEFI | Menunggu build |
| ISO boot ke desktop di BIOS | Menunggu build |
| Build dingin maksimal 60 menit | Menunggu pengukuran |
| Build hangat maksimal 20 menit | Menunggu pengukuran |
| Nama artefak sesuai pola | Lulus validasi statis |
| Checksum tersedia | Diimplementasikan, menunggu ISO |
| Tidak ada dependency error | Menunggu log build |
| Boot log serial tersedia | Diimplementasikan, menunggu ISO |

Fase 1 belum selesai sampai seluruh baris berstatus lulus.

## 21. Referensi

- [plan.md](../plan.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [DESIGN.md](DESIGN.md)
- [PHASE-0-1-REPORT.md](PHASE-0-1-REPORT.md)
- [ADR index](adr/README.md)
- [README](../README.md)
