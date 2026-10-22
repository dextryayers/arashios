# Laporan Fase 6 dan Fase 7

Status: implementasi statis selesai. Exit gate runtime belum lulus karena ISO
belum dapat dibangun pada host ini.

Tanggal: 2026-10-22

## 1. Ringkasan

Fase 6 membangun konfigurasi penggunaan harian: aplikasi, jaringan, audio,
daya, cetak, locale, firmware, diagnosis harian, dan laporan hardware.

Fase 7 membangun installer, persistence, dan pemulihan: konfigurasi
Calamares dengan branding Kage, profil partisi, enkripsi LUKS2, pemeriksaan
dual boot, partisi persistence, dan serangkaian perintah pemulihan.

Yang belum ada:

1. Image ISO dan boot UEFI serta BIOS.
2. Skenario instalasi yang benar-benar dijalankan.
3. Checklist hardware pada tiga mesin.
4. Pengujian suspend dan resume sepuluh kali.
5. Uji cetak, pindai, dan audio pada perangkat nyata.

## 2. Sub-fase Fase 6

### 6.1 Aplikasi harian

Daftar paket harian dipisah menjadi tiga berkas dengan satu pemilik per paket
supaya tidak ada duplikasi:

| Berkas | Isi | Jumlah paket |
|---|---|---:|
| `40-daily.list.chroot` | Peramban, surel, kantor, media, utilitas, perawatan | 26 |
| `42-daily-apps.list.chroot` | Locale aplikasi, media playback, konversi dokumen | 9 |
| `45-platform.list.chroot` | Jaringan, daya, cetak, audio, firmware, inventaris | 27 |

Paket locale Firefox, Thunderbird, dan LibreOffice untuk id_ID serta ja_JP
ditambahkan, bersama kamus ejaan Indonesia. Pemeriksaan ketersediaan paket
menyatakan 0 paket hilang pada tujuh kombinasi.

### 6.2 Jaringan

| Berkas | Isi |
|---|---|
| `/etc/NetworkManager/conf.d/99-arashios.conf` | Policy manager jaringan |
| `45-platform.list.chroot` | avahi, wpasupplicant, mtr, iw, rfkill |

Kebijakan: DNS memakai resolver sistem, pengecekan konektivitas daring
dimatikan, MAC kloning stabil, dan tidak ada kredensial bersama di tingkat
sistem.

### 6.3 Audio

Cinnamon dan LXQt memakai PipeWire dengan wireplumber. XFCE memakai
PulseAudio. Semua edisi memakai pavucontrol, alsa-utils, libasound2-plugins,
dan playerctl. Pemeriksaan otomatis menolak kombinasi yang tidak sesuai
dengan kebijakan edisi.

### 6.4 Daya

| Berkas | Isi |
|---|---|
| `/etc/tlp.conf` | Ambang pengisian 75 sampai 80 persen, governor, ASPM, runtime suspend |
| `/etc/default/zramswap` | zstd, 25 persen memori, prioritas 100 |
| `/etc/default/earlyoom` | Ambang memori 15 persen dan swap 10 persen |
| `40-daily.list.chroot` | thermald pada overlay amd64 dan i386 |

Hook `0400-platform.chroot` mengaktifkan tlp, zram, earlyoom, fwupd, bluetooth,
avahi, dan cups.socket pada sesi live maupun sistem terpasang.

### 6.5 Cetak dan pindai

CUPS berjalan melalui socket, service dinonaktifkan agar tidak ada daemon
berjalan terus. Filter cups, printer PDF, sane-utils, dan xsane tersedia.
Pemeriksaan harian mencatat daftar printer dan perangkat pindai.

### 6.6 Locale

`/etc/locale.gen` memuat en_US.UTF-8, id_ID.UTF-8, dan ja_JP.UTF-8. Hook
platform menjalankan `locale-gen` dan menambahkan locale yang belum ada.
Font CJK, kamus ejaan Indonesia, serta locale Firefox, Thunderbird, dan
LibreOffice untuk kedua bahasa tersedia.

### 6.7 Firmware

Paket firmware bebas dan non-free tetap terpasang, `firmware-sof-signed`
ditambahkan untuk Intel Sound, fwupd aktif, dan mokutil dipakai untuk
memeriksa Secure Boot.

### 6.8 QA hardware

`arashios-hardware-report` mengumpulkan laporan JSON dan Markdown berisi
sistem, CPU, memori, grafis, jaringan, audio, penyimpanan, daya, printer,
firmware, dan status suspend. Checklist tiga mesin dengan lima belas
pemeriksaan dan prosedur suspend sepuluh kali ada di `docs/HARDWARE.md`.

### 6.9 Dokumentasi

`docs/DAILY.md` menjelaskan konfigurasi harian dan `docs/HARDWARE.md`
menjelaskan dukungan hardware serta checklist QA.

## 3. Sub-fase Fase 7

### 7.1 Calamares dan branding

| Berkas | Isi |
|---|---|
| `/etc/calamares/settings.conf` | Pengaturan global installer |
| `/etc/calamares/modules.conf` | Urutan 17 modul |
| `/etc/calamares/modules/*.conf` | Konfigurasi 8 modul |
| `/usr/share/calamares/branding/arashios/branding.desc` | Branding Kage |
| `/usr/share/calamares/branding/arashios/stylesheet.qss` | Warna sidebar installer |
| `/usr/share/calamares/branding/arashios/show.qml` | Slideshow installer |
| `/usr/share/calamares/branding/arashios/slides/*.md` | Lima slide installer |

Pengaturan installer memakai palet Kage, wallpaper yang sama dengan desktop,
banner dan gambar selamat datang yang dihasilkan oleh generator aset, dan
pengunggahan log dimatikan. Aset banner berukuran 1024 x 128 piksel dan gambar
selamat datang 480 x 240 piksel, keduanya dibuat tanpa renderer eksternal.

Konfigurasi divalidasi terhadap skema Calamares 3.2 yang diambil dari paket
Debian bookworm, termasuk kunci fstab, bootloader, displaymanager, packages,
dan services-systemd.

### 7.1a Urutan modul

| Modul | Peran |
|---|---|
| welcome | Halaman pembuka dan tautan dokumentasi |
| locale, localecfg | Bahasa dan penulisan locale pada sistem target |
| keyboard | Tata letak keyboard |
| partition, mount, luksbootkeyfile | Partisi, mount, dan kunci boot |
| users | Pembuatan akun tanpa autologin |
| displaymanager | LightDM sebagai display manager |
| packages | Tidak ada paket tambahan |
| fstab, hwclock | Tabel partisi dan jam perangkat keras |
| bootloader | Pemasangan GRUB dengan tema Kage |
| services-systemd | Layanan, target, timer, dan mask |
| removeuser | Penghapusan user live dari sistem target |
| finished | Ringkasan akhir |
| shellprocess | Post install ArashiOS |

### 7.2 Profil partisi

Tiga profil tersedia dari modul partisi: erase disk, alongside, dan manual.
Default: ext4, partisi EFI 512 MiB di /boot/efi, swap memakai zram sehingga
tidak ada partisi swap, dan disk minimum 8 GiB.

### 7.3 LUKS dan LVM

Enkripsi LUKS2 tersedia dan aktif secara bawaan dengan nama volume
`cryptroot`. Modul `luksbootkeyfile` tetap dipakai agar opsi kunci boot
tersedia. Calamares 3.2 belum menyediakan modul LVM, sehingga LVM disiapkan
manual dan langkahnya terdokumentasi di `docs/INSTALL.md`. Perintah
`arashios-recovery lvm-scan` mengaktifkan dan menampilkan volume LVM.

### 7.4 Dual boot Windows

`arashios-dualboot-check` memeriksa partisi Windows, Fast Startup, BitLocker,
sistem Linux lain, dan Secure Boot sebelum partisi dimulai. os-prober terpasang
dan `GRUB_DISABLE_OS_PROBER=false` disetel pada `/etc/default/grub` sehingga
GRUB mendeteksi sistem lain.

### 7.5 Persistence

`arashios-persistence` menyiapkan partisi berlabel `persistence` dengan
berkas `persistence.conf` berisi direktif `/ union`, memeriksa isinya, dan
menampilkan status partisi. Contoh konfigurasi tersedia di
`/usr/share/arashios/persistence/README`.

### 7.6 Recovery

`arashios-recovery` menyediakan diagnose, journal, list-disks, luks-open,
lvm-scan, chroot, grub-install, grub-update, backup-efi, dan restore-efi.
Timeshift terpasang dan membuat snapshot pertama saat instalasi selesai.

### 7.7 Secure Boot

Status Secure Boot dideteksi dengan mokutil dan dilaporkan oleh
`arashios-dualboot-check` serta `arashios-recovery diagnose`. Karena kernel
ArashiOS belum ditandatangani, Secure Boot harus dinonaktifkan sebelum
instalasi. Kondisi ini terdokumentasi di `docs/INSTALL.md`.

### 7.8 QA instalasi

`tests/installer.sh` memvalidasi konfigurasi Calamares, branding, urutan
modul, dan perilaku perintah installer. `docs/INSTALL.md` memuat checklist
sepuluh skenario untuk tiga edisi. Skenario nyata menunggu image ISO.

### 7.9 Dokumentasi

`docs/INSTALL.md`, `docs/PERSISTENCE.md`, dan `docs/RECOVERY.md` memuat prosedur lengkap.

## 4. Hasil Verifikasi

### 4.1 Pemeriksaan Statis

| Pemeriksaan | Hasil |
|---|---|
| Konfigurasi penggunaan harian | 88 pemeriksaan lulus |
| Konfigurasi installer, persistence, dan pemulihan | 148 pemeriksaan lulus |
| Audit paket bookworm | 2131 nama paket, 0 hilang pada 7 kombinasi |
| Katalog toolstack | 6732 pemeriksaan lulus |
| Validasi konfigurasi live-build | lulus |
| Testsuite harian | lulus |
| Testsuite installer | lulus |
| Pemeriksaan dokumen | 401 berkas lulus |

### 4.2 Ketersediaan Paket Bookworm

| Kombinasi | Paket unik | Hilang |
|---|---:|---:|
| amd64 cinnamon | 308 | 0 |
| amd64 xfce | 308 | 0 |
| amd64 lxqt | 317 | 0 |
| arm64 xfce | 303 | 0 |
| arm64 lxqt | 312 | 0 |
| i386 lxqt | 296 | 0 |
| i386 xfce | 287 | 0 |

### 4.3 Perintah

```bash
python3 scripts/check-daily.py
python3 scripts/check-installer.py
python3 scripts/check-packages-bookworm.py --index-dir <indeks>
./tests/daily.sh
./tests/installer.sh
make lint
```

## 5. Penyimpangan dan Risiko

1. Skenario instalasi belum dijalankan karena image ISO belum dibangun.
2. Modul LVM bawaan Calamares belum ada di versi 3.2, LVM disiapkan manual.
3. Secure Boot belum didukung, hanya deteksi dan dokumentasi.
4. Checklist hardware tiga mesin belum dijalankan.
5. Suspend dan resume sepuluh kali belum diuji.
6. Cetak, pindai, dan audio belum diuji pada perangkat nyata.
7. Pemeriksaan audio pada host pengembangan memakai PulseAudio sehingga
   kombinasi edisi lain dilaporkan sebagai catatan, bukan kegagalan.
8. Nama partisi dan label dapat berbeda antar perangkat, pemeriksaan
   persistensi dan dual boot sudah menangani kedua kemungkinan.

## 6. Exit Gate Runtime

Fase 6 dan Fase 7 belum dapat ditutup sampai:

1. ISO amd64 dibangun dan diverifikasi checksum.
2. Boot UEFI dan BIOS berhasil pada QEMU.
3. Installer Calamares terbuka dengan branding Kage di image.
4. Skenario INST-01 sampai INST-10 dijalankan pada tiga edisi.
5. Autologin mati pada sistem terpasang dan installer terhapus.
6. Snapshot Timeshift pertama dibuat.
7. Volume LUKS2 dapat dibuka kembali setelah reboot.
8. GRUB mendeteksi Windows dan Linux lain.
9. Partisi persistence bertahan setelah reboot.
10. Checklist hardware HW-01 sampai HW-15 lulus pada tiga mesin.
11. Suspend dan resume lulus sepuluh dari sepuluh.
12. Cetak dan pindai lulus pada perangkat nyata.

## 7. Langkah Berikutnya

1. Pasang toolchain ISO lengkap pada host Debian 12.
2. Bangun ISO amd64 Cinnamon dan jalankan smoke test.
3. Jalankan installer pada virtual disk dan periksa autologin, timeframe, dan
   penghapusan installer.
4. Uji partisi LUKS2 dan persistence.
5. Lengkapi checklist hardware pada tiga mesin.
6. Lanjutkan ke Fase 8 setelah exit gate runtime Fase 6 dan Fase 7 lulus.
