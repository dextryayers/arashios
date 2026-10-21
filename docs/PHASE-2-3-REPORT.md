# Laporan Fase 2 dan Fase 3

Status: implementasi statis selesai. Exit gate runtime belum lulus karena ISO
belum dapat dibangun pada host ini.

Tanggal: 2026-10-21

## 1. Ringkasan

Fase 2 menghasilkan identitas boot dan tema Kage yang dapat dibangun ulang.
Fase 3 menghasilkan konfigurasi Cinnamon, XFCE, dan LXQt yang memakai tema,
wallpaper, panel, dan terminal yang sama. Pekerjaan ini diverifikasi dengan
pemeriksaan statis, parser toolkit, kompilasi dconf, dan pembangunan paket
lokal.

Yang belum ada:

1. ISO amd64, arm64, atau i386.
2. Boot GRUB dan Plymouth pada firmware nyata.
3. Login LightDM dan sesi desktop.
4. Screenshot Cinnamon, XFCE, dan LXQt.
5. Rendering Kvantum pada aplikasi Qt.
6. Pengujian panel pada nama monitor dan resolusi berbeda.

## 2. Deliverable Fase 2

### 2.1 Tema

| Item | Hasil |
|---|---|
| Varian | `ArashiKage`, `ArashiKage-HC` |
| File manifest | 164 entri, 165 file termasuk `manifest.json` |
| File per varian | 80 file |
| Aset XFWM per varian | 70 PNG |
| Toolkit | GTK2, GTK3, GTK4 dan libadwaita, Cinnamon, Muffin dan Metacity, XFCE, Openbox, Kvantum |
| Manifest | SHA-256 di `build/theme/manifest.json` |
| Paket | `build/packages/arashios-branding_1.10.21-1_all.deb` |

Template berada di `branding/theme/templates/`. Generator berada di
`scripts/generate-theme.py`. File hasil generate tidak diedit manual.

### 2.2 Wallpaper dan Ikon

| Item | Hasil |
|---|---|
| Wallpaper PNG | `kage-sumi`, `kage-shuriken`, `kage-bamboo`, `kage-washi`, `kage-storm` |
| Resolusi | 3840x2160 |
| Sumber | SVG di `branding/wallpaper/` |
| Ukuran PNG terbesar | 268460 byte |
| Ikon | SVG, ICO, dan PNG 16 sampai 256px |

### 2.3 Boot

| Item | Hasil |
|---|---|
| GRUB live | `config/common/bootloaders/grub-pc/config.cfg` dan tema `live-theme` Kage |
| GRUB terpasang | `/usr/share/grub/themes/arashios` |
| Timeout | 5 detik |
| Resolusi | 1024x768, fallback 800x600 dan otomatis |
| Suara boot | Tidak ada |
| Plymouth | Logo, wordmark, progress line 320x2 |
| LightDM | Tema, wallpaper, font, ikon, kursor, panel atas |

Progress Plymouth memakai `Plymouth.SetBootProgressFunction`. Hanya progress
line yang bergerak.

### 2.4 Paket Branding

| Field | Nilai |
|---|---|
| Package | `arashios-branding` |
| Version | `1.10.21-1` |
| Architecture | `all` |
| Ukuran | 723368 byte |
| File payload | 214 file |
| Maintainer | `maintainers@arashios.example` |
| Reproducible | Ya, dengan `SOURCE_DATE_EPOCH` |
| Hash contoh | `40f6c22e39ea57912758ecfa6e1377400837a30515a0b390d80457d8292ccb4d` |

Paket berisi tema, wallpaper, ikon, aset GRUB, aset Plymouth, token, manifest,
dokumentasi lisensi termasuk `NOTICE`, dan changelog. Paket tidak memasang
desktop atau window manager.

## 3. Deliverable Fase 3

### 3.1 Cinnamon

1. Panel atas 30px dengan menu, grouped window list, kalender, workspace
   switcher, systray, notifikasi, keyboard, suara, dan power.
2. Empat workspace.
3. Nemo list view, thumbnail nonaktif, dan ikon desktop nonaktif.
4. Automount dan autorun dimatikan.
5. GNOME Terminal memakai profil `Kage` dengan palet token.
6. Toolkit accessibility aktif.
7. Screensaver aktif dengan lock delay 0.
8. Muffin dan border jendela memakai tema `ArashiKage`; helper aksesibilitas
   ikut mengganti tema Muffin saat mode kontras diubah.

### 3.2 XFCE

1. Panel atas 30px dengan 11 plugin.
2. Whisker Menu, tasklist, jam, tray, PulseAudio, power manager, notifikasi,
   dan pager.
3. xfwm4 memakai tema ArashiKage dan compositor dengan shadow.
4. Thunar list view dan volume management.
5. Desktop tanpa ikon, home, filesystem, removable, atau trash.
6. Wallpaper `kage-sumi.png` dengan mode zoom.
7. XFCE Terminal memakai palet token.

### 3.3 LXQt

1. Panel atas 30px dengan menu, quick launch, taskbar, desktop switch,
   status notifier, tray, volume, jam, dan show desktop.
2. Quick launch berisi QTerminal, PCManFM-Qt, dan Firefox ESR.
3. Openbox memakai border aktif vermilion 2px, title layout `IMC`, dan empat
   workspace.
4. PCManFM-Qt list view, wallpaper Kage, tanpa desktop shortcut.
5. Kvantum ArashiKage untuk aplikasi Qt.
6. QTerminal memakai palet token.

### 3.4 Aksesibilitas

Perintah `arashios-accessibility` menyediakan:

1. `contrast on`, `off`, dan `toggle`.
2. `motion on` dan `off`.
3. `status` untuk desktop, tema, dan status animasi.

Tema kontras tinggi mencakup GTK, Cinnamon, XFCE, Openbox, dan Kvantum.
Perubahan tema tidak memulai ulang aplikasi yang sedang berjalan.

### 3.5 Terminal

| Terminal | Konfigurasi |
|---|---|
| GNOME Terminal | Profil dconf `Kage`, font JetBrains Mono 11 |
| XFCE Terminal | `terminalrc`, font JetBrains Mono 11, palet token |
| QTerminal | `qterminal.ini`, font JetBrains Mono 11, palet token |

## 4. Hasil Verifikasi

### 4.1 Pemeriksaan Statis

| Pemeriksaan | Hasil |
|---|---|
| Dokumen dan kebijakan teks | 117 file lulus |
| Traceability | 58 requirement, 52 test case |
| Token dan aset raster | Sinkron |
| Tema | 2237 pemeriksaan lulus |
| Parser CSS GTK3 | Lulus untuk kedua varian |
| Parser CSS GTK4 | Lulus untuk kedua varian |
| Integrasi desktop | 287 pemeriksaan lulus |
| Helper aksesibilitas | Lulus dengan `HOME` sementara |
| Paket branding | Lulus, 214 file, reproducible |
| Validasi konfigurasi | Lulus, termasuk GRUB dan dconf |
| XML dan SVG | Semua dapat diparse |
| dconf Cinnamon | `dconf compile` lulus |

Pemeriksaan tambahan memuat tema pada sesi Cinnamon 6.6 di host LMDE 7 dengan
Xephyr dan HOME sementara. Panel atas 30px, GTK, Muffin, Nemo, dan terminal
tampil dengan tema Kage. Uji ini menemukan default tema Muffin yang belum
diatur; konfigurasi dan helper aksesibilitas sudah diperbaiki. Sesi host
memakai Cinnamon 6.6, bukan target Debian 12, sehingga hasil ini bukan bukti
exit gate runtime.

### 4.2 Ketersediaan Paket Bookworm

Audit nama paket terhadap indeks bookworm:

| Kombinasi | Paket unik | Hilang |
|---|---:|---:|
| amd64 cinnamon | 240 | 0 |
| amd64 xfce | 240 | 0 |
| amd64 lxqt | 249 | 0 |
| arm64 xfce | 236 | 0 |
| arm64 lxqt | 245 | 0 |
| i386 lxqt | 229 | 0 |
| i386 xfce | 220 | 0 |

Audit ini memeriksa ketersediaan nama paket, bukan resolusi dependensi penuh
atau konflik versi.

### 4.3 Dry Run Live-Build

Dry run dijalankan untuk tujuh kombinasi dengan `live-build` bookworm yang
diekstrak ke direktori sementara. Host pengembangan adalah LMDE 7 dan tidak
memiliki toolchain ISO lengkap, jadi hasil ini memvalidasi konfigurasi, bukan
membuktikan ISO dapat dibangun.

| Kombinasi | Hasil |
|---|---|
| amd64 cinnamon | Lulus |
| amd64 xfce | Lulus |
| amd64 lxqt | Lulus |
| arm64 xfce | Lulus |
| arm64 lxqt | Lulus |
| i386 lxqt | Lulus |
| i386 xfce | Lulus |

Setiap dry run memeriksa paket branding, splash GRUB, tema live GRUB beserta
pixmap nine-slice, splash syslinux, konfigurasi GTK, MIME, sesi LightDM, kernel
flavour, dan metadata build.

### 4.4 Perintah

```bash
./tests/theme.sh
./tests/desktop-matrix.sh
./tests/branding-package.sh
./scripts/validate-config.sh
make lint
make config-matrix
```

## 5. Penyimpangan dan Risiko

1. Pekerjaan statis Fase 2 dan Fase 3 dilanjutkan sebelum exit gate runtime
   Fase 1 lulus. Hal ini dilakukan karena toolchain ISO tidak tersedia. Host
   LMDE 7 bukan acuan rilis Debian 12, sehingga build ISO tetap harus dijalankan
   pada host bookworm. Exit gate runtime tetap terbuka.
2. Parser CSS GTK4 memakai GTK 4.18 pada host pengembangan. Target bookworm
   memakai GTK 4.8. CSS perlu diuji ulang pada ISO.
3. Patch default applet Cinnamon berada di hook dan dapat tertimpa pembaruan
   paket Cinnamon.
4. Aplikasi yang berjalan tidak dimulai ulang setelah tema diganti.
5. Nama monitor XFCE dapat berbeda pada perangkat keras nyata.
6. Shippori Mincho dan Starship tidak tersedia di bookworm. Wordmark memakai
   aset vektor dan prompt memakai fallback Zsh.
7. Maintainer memakai domain `.example` sampai domain proyek diverifikasi.
8. Autologin masih aktif pada sistem terpasang sampai Fase 7.
9. Kvantum belum dijalankan pada sesi Qt nyata.
10. Screenshot dan pengukuran waktu boot belum tersedia.

## 6. Exit Gate Runtime

Fase 2 dan Fase 3 belum dapat ditutup sampai:

1. ISO amd64 dibangun dan diverifikasi checksum.
2. Boot UEFI dan BIOS berhasil pada QEMU.
3. GRUB menampilkan tema tanpa logo Debian.
4. Plymouth menampilkan logo dan progress line.
5. LightDM menampilkan sesi yang benar.
6. Login Cinnamon, XFCE, dan LXQt berhasil.
7. Panel atas 30px tampil pada ketiga edisi.
8. Wallpaper dan ikon desktop sesuai.
9. Nemo, Thunar, dan PCManFM-Qt memakai tema Kage.
10. GNOME Terminal, XFCE Terminal, dan QTerminal memakai palet Kage.
11. Openbox dan Kvantum tampil tanpa artefak.
12. Mode kontras tinggi dan reduced motion diuji pada sesi nyata.
13. Screenshot before dan after disimpan.
14. Waktu boot dan penggunaan RAM diukur.

## 7. Langkah Berikutnya

1. Pasang toolchain `live-build`, `debootstrap`, `xorriso`, syslinux, GRUB,
   QEMU, dan OVMF.
2. Bangun ISO amd64 Cinnamon sebagai artefak pertama.
3. Jalankan verifikasi artefak dan boot QEMU UEFI serta BIOS.
4. Jalankan smoke test live.
5. Ambil screenshot dan catat waktu boot.
6. Perbaiki temuan runtime, lalu ulangi untuk XFCE dan LXQt.
7. Setelah amd64 stabil, validasi arm64 dan i386 pada Fase 10.
