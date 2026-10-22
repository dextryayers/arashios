# Penggunaan Harian ArashiOS

Dokumen ini menjelaskan konfigurasi penggunaan harian pada ArashiOS: aplikasi,
jaringan, audio, daya, cetak dan pindai, locale, serta firmware.

## 1. Aplikasi harian

| Kategori | Aplikasi | Paket |
|---|---|---|
| Peramban | Firefox ESR dengan locale Indonesia dan Jepang | firefox-esr, firefox-esr-l10n-id, firefox-esr-l10n-ja |
| Surel | Thunderbird dengan locale Indonesia dan Jepang | thunderbird, thunderbird-l10n-id, thunderbird-l10n-ja |
| Kantor | LibreOffice Writer, Calc, Impress, dan Draw | libreoffice, libreoffice-l10n-id, libreoffice-l10n-ja |
| Konversi dokumen | Pandoc | pandoc |
| Media | VLC, mpv, playerctl, GIMP, Inkscape | vlc, mpv, playerctl, gimp, inkscape |
| Berkas | File Roller, Evince, PCManFM, Thunar, Nemo | file-roller, evince |
| Cuplikan layar | Flameshot | flameshot |
| Kredensial | KeePassXC, Seahorse | keepassxc, seahorse |
| Pemeliharaan | Timeshift, GParted, GNOME Disk Utility, smartmontools | timeshift, gparted, gnome-disk-utility, gsmartcontrol |
| Transfer | Remmina, FileZilla, qBittorrent | remmina, filezilla, qbittorrent |
| Cetak | CUPS, filter, pemindai | cups, cups-filters, system-config-printer, sane-utils, xsane |

Semua paket berasal dari Debian bookworm dan tersedia pada amd64, arm64, dan
i386. Pemeriksaan ketersediaan ada di `scripts/check-packages-bookworm.py`.

## 2. Jaringan

| Aspek | Konfigurasi |
|---|---|
| Manajer jaringan | NetworkManager dengan plugin ifupdown dan keyfile |
| Resolver | systemd-resolved bawaan Debian |
| WiFi | wpa_supplicant, pemindaian MAC acak stabil, hemat daya level 2 |
| Bluetooth | blueman, layanan diaktifkan |
| Penemuan jaringan | avahi-daemon dan avahi-utils |
| Diagnostik | mtr-tiny, traceroute, iproute2 |

Berkas `/etc/NetworkManager/conf.d/99-arashios.conf` berisi kebijakan:

1. DNS memakai resolver bawaan sistem.
2. Pengecekan konektivitas daring dimatikan agar tidak ada permintaan
   otomatis ke server luar.
3. Alamat MAC kloning bersifat stabil untuk bloody di jaringan tetap.
4. Tidak ada kredensial bersama di tingkat sistem. Rahasia disimpan di keyring.

## 3. Audio

| Edisi | Server | Komponen |
|---|---|---|
| Cinnamon | PipeWire | pipewire, pipewire-pulse, wireplumber |
| LXQt | PipeWire | pipewire, pipewire-pulse, wireplumber |
| XFCE | PulseAudio | pulseaudio |

Semua edisi memakai `pavucontrol` untuk mixer dan `alsa-utils` untuk
perangkat terminal. Perintah `arashios-daily audio` memeriksa sink, source, dan
server yang aktif.

## 4. Daya dan panas

| Komponen | Peran | Konfigurasi |
|---|---|---|
| TLP | Manajemen daya | /etc/tlp.conf |
| zram | Swap terkompresi | /etc/default/zramswap |
| earlyoom | Penghentian proses boros | /etc/default/earlyoom |
| thermald | Kontrol fan dan suhu | paket amd64 dan i386 |

Kebijakan TLP: pengisian mulai 75 persen dan berhenti 80 persen, governor
`powersave` pada baterai, ASPM PCIe aktif, dan suspend runtime aktif.
zram memakai zstd dengan ukuran 25 persen memori. earlyoom memberi tahu
pengguna sebelum kernel OOM killer memilih proses acak.

## 5. Cetak dan pindai

1. CUDS berjalan melalui `cups.socket` dan hanya aktif saat ada printer.
2. `cups.service` dinonaktifkan agar tidak ada daemon berjalan terus.
3. Filter cups, printer PDF, dan `xsane` tersedia untuk pindai.
4. `arashios-daily print` memeriksa status CUPS, daftar printer, dan perangkat
   pindai.

## 6. Locale

| Locale | Status | Paket pendukung |
|---|---|---|
| en_US.UTF-8 | utama | locale, fonts |
| id_ID.UTF-8 | aktif | hunspell-id, firefox-esr-l10n-id, libreoffice-l10n-id |
| ja_JP.UTF-8 | aktif | fonts-noto-cjk, firefox-esr-l10n-ja, libreoffice-l10n-ja |

Berkas `/etc/locale.gen` memuat ketiga locale dan hook build menjalankan
`locale-gen`. Zona waktu bawaan adalah UTC dan dapat diubah di sistem
terpasang.

## 7. Firmware

1. Firmware bebas, iwlwifi, Realtek, Atheros, Broadcom, AMD, Intel, dan
   non-free terpasang dari Debian.
2. `firmware-sof-signed` menangani firmware Intel Sound Open Firmware.
3. fwupd aktif untuk pembaruan firmware dari vendor.
4. Secure Boot diperiksa dengan mokutil. ArashiOS belum menandatangani
   kernel, sehingga Secure Boot harus dinonaktifkan sebelum instalasi.

## 8. Diagnosis harian

```bash
arashios-daily              # seluruh area
arashios-daily network      # satu area
arashios-daily --json       # keluaran JSON
arashios-daily --strict     # keluar dengan status 1 bila ada masalah
arashios-hardware-report --format markdown --output laporan.md
```

Area yang diperiksa: network, audio, power, print, locale, firmware.
Perintah tidak mengubah status sistem dan tidak menghubungi jaringan.

## 9. Checklist QA hardware

Checklist tiga mesin dan sepuluh kali suspend ada di [HARDWARE.md](HARDWARE.md).
Laporan yang dikumpulkan memakai `arashios-hardware-report`.

## 10. Pemeriksaan yang dijalankan

```bash
python3 scripts/check-daily.py
python3 scripts/check-packages-bookworm.py --index-dir <indeks>
./tests/daily.sh
```

## 11. Batasan saat ini

1. Pengujian hardware nyata belum dilakukan karena tidak ada akses ke tiga
   mesin uji.
2. Audio belum diuji pada sesi desktop nyata.
3. Printer dan pindai belum diuji pada perangkat nyata.
4. Pemeriksaan powertop belum dijalankan pada host build.
