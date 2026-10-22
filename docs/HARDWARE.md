# Hardware ArashiOS

Dokumen ini menjelaskan dukungan hardware, checklist QA, dan cara mengumpulkan
bukti kompatibilitas untuk ArashiOS.

## 1. Ruang Lingkup

| Komponen | Status v1 |
|---|---|
| amd64 | Investigasi penuh, UEFI dan BIOS |
| arm64 | Investigasi penuh, UEFI saja |
| i386 | Investigasi terbatas, BIOS saja |
| WiFi | wpa_supplicant, dukungan vendor melalui firmware non-free |
| Bluetooth | blueman dan bluez |
| Audio | PipeWire pada Cinnamon dan LXQt, PulseAudio pada XFCE |
| GPU | Mesa dan driver kernel Debian, tanpa driver proprietary secara bawaan |
| Cetak | CUPS dengan filter cups dan dukungan PDF |
| Pindai | sane-utils dan xsane |
| Daya | TLP, zram, earlyoom, thermald pada amd64 dan i386 |

## 2. Paket firmware

| Paket | Perangkat |
|---|---|
| firmware-linux-free | Firmware bebas |
| firmware-iwlwifi | Intel WiFi |
| firmware-realtek | Realtek |
| firmware-atheros | Atheros |
| firmware-brcm80211 | Broadcom |
| firmware-amd-graphics | AMD |
| firmware-intel-sound | Intel Sound |
| firmware-misc-nonfree | Lain-lain yang tidak bebas |
| firmware-sof-signed | Intel Sound Open Firmware |

Pembaruan firmware dari vendor dilakukan lewat fwupd. Perintah `arashios-daily
firmware` memeriksa status fwupd, Secure Boot, dan jumlah vendor firmware
yang terpasang.

## 3. Checklist tiga mesin

Checklist wajib untuk setiap rilis. Setiap mesin harus mencatat model, CPU,
RAM, GPU, dan media penyimpanan.

### 3.1 Target minimum

| Profil | CPU | RAM | Disk |ayar |
|---|---|---|---|---|
| Ringan | dua inti x86_64 | 2 GB | 15 GB | 1366 x 768 |
| Sedang | empat inti | 8 GB | 40 GB | 1920 x 1080 |
| Berat | delapan inti | 16 GB | 80 GB | 2560 x 1440 |

### 3.2 Pemeriksaan per mesin

| ID | Pemeriksaan | Cara | Lolos bila |
|---|---|---|---|
| HW-01 | Boot UEFI | `make test BOOT_MODE=uefi` | sampai ke desktop |
| HW-02 | Boot BIOS | `make test BOOT_MODE=bios` | sampai ke desktop |
| HW-03 | WiFi | `nmcli device wifi list` | tersambung dan ping berhasil |
| HW-04 | Bluetooth | `bluetoothctl show` | perangkat terpasang dan terhubung |
| HW-05 | Audio | `arashios-daily audio` | sink dan source ada |
| HW-06 | Audio Bluetooth | `pavucontrol` | output perangkat terlihat |
| HW-07 | Cetak | `lpstat -t` | printer terdaftar dan test halaman berhasil |
| HW-08 | Pindai | `scanimage -L` | perangkat terlihat |
| HW-09 | Suspend dan resume | `systemctl suspend` | sepuluh dari sepuluh berhasil |
| HW-10 | Tahan baterai | `arashios-daily power` | TLP aktif, zram aktif, earlyoom aktif |
| HW-11 | Firmware | `fwupdmgr get-devices` | daftar perangkat tampil |
| HW-12 | Locale | `locale -a` | en_US, id_ID, ja_JP tersedia |
| HW-13 | Tata letak keyboard | `localectl status` | tata letak sesuai |
| HW-14 | Skala layar | login desktop | tidak ada teks terpotong |
| HW-15 | Multi monitor | xrandr | semua monitor tampil |

### 3.3 Prosedur suspend sepuluh kali

```bash
for i in $(seq 1 10); do
    printf 'uji %s: %s\n' "$i" "$(date --iso-8601=seconds)"
    systemctl suspend
    sleep 30
done
```

Setiap siklus dicatat: durasi bangun, hilang atau tidak data, error pada
journal, dan kondisi baterai. Lolos bila sepuluh siklus berhasil dan journal
tidak menunjukkan errorresume.

## 4. Pengumpulan laporan

```bash
arashios-hardware-report --format markdown --output hw-mesin-1.md
arashios-hardware-report --output hw-mesin-1.json
```

Laporan memuat sistem, CPU, memori, grafis, jaringan, audio, penyimpanan,
daya, printer, firmware, dan status suspend. Laporan tidak mengirim data ke
server mana pun.

## 5. Known issues per mesin

| Kategori | Tindakan |
|---|---|
| WiFi hilang setelah resume | `sudo systemctl restart NetworkManager` |
| Audio tidak kembali | `systemctl --user restart pipewire wireplumber` |
| Layar gelap setelah resume | `systemctl restart display-manager` |
| Fan keras setelah ulang | thermald belum terpasang pada arm64 |
| Printer tidak ditemukan | `sudo systemctl restart cups` |
| Baterai habis cepat | periksa `arashios-daily power` dan Profil TLP |
| Secure Boot aktif | matikan sebelum instalasi, kernel belum ditandatangani |

## 6. Standar penerimaan

1. Tiga mesin target mengisi seluruh checklist HW-01 sampai HW-15.
2. Suspend dan resume lulus sepuluh dari sepuluh pada setiap mesin.
3. Tidak ada regresi dibanding Debian 12 pada aplikasi yang sama.
4. Laporan hardware tersimpan di direktori rilis.

## 7. Batasan saat ini

Checklist ini belum dijalankan. Akses ke tiga mesin uji dan image ISO belum
tersedia pada host pengembangan.
