# Laporan Fase 10 dan Fase 11

Status: implementasi statis selesai. Exit gate runtime belum lulus karena ISO
belum dapat dibangun pada host ini.

Tanggal: 2026-10-23

## 1. Ringkasan

Fase 10 menyiapkan rilis dan distribusi secara mandiri: tata kelola versi,
matriks build, verifikasi artefak, mirror, torrent, kanal rilis, komunitas,
pemantauan, kandidat rilis, dan audit pasca rilis.

Fase 11 menyiapkan pasca v1: image ARM SBC, Secure Boot, Wayland
eksperimental, Arsenal GUI, image cloud dan WSL, kebijakan i386, evaluasi
basis, dukungan hardware, lokalisasi, dan dukungan jangka panjang.

Yang belum ada:

1. Image ISO sehingga boot, runtime, dan scan CVE belum dijalankan.
2. Mirror publik karena domain final belum ditetapkan.
3. Pengujian pada perangkat nyata.

## 2. Sub-fase Fase 10

### 10.1 Tata kelola versi dan changelog

CHANGELOG.md dan release notes diperbarui. Tag Git bertanda tangan
disiapkan untuk rilis.

### 10.2 Matriks build dan pabrik artefak

Tujuh kombinasi artefak didokumentasikan di `docs/RELEASE.md`. Build
memakai `build.sh`.

### 10.3 Verifikasi artefak dan signing

`tests/verify-artifact.sh` memeriksa nama, ukuran, struktur ISO, bootloader,
checksum, SBOM, dan tanda tangan.

### 10.4 Mirror, torrent, dan distribusi

`scripts/publish-mirror.sh`, `scripts/generate-torrent.sh`,
`tests/mirror-check.sh`, dan `docs/MIRROR.md` disediakan.

### 10.5 Situs web dan dokumentasi publik

Situs statis di `site/` dan dokumentasi di `docs/` disediakan.

### 10.6 Kanal rilis

Berkas sumber untuk stable, edge, dan nightly berada di
`config/channels/`. `scripts/channel-switch.sh` dan
`tests/channel-check.sh` disediakan.

### 10.7 Komunitas dan dukungan

`SUPPORT.md`, `GOVERNANCE.md`, `MAINTAINERS.md`, dan `docs/COMMUNITY.md`
disiapkan. Template issue dan pull request tersedia.

### 10.8 Pemantauan, hotfix, dan rollback

`scripts/monitor-release.sh`, `docs/MONITORING.md`, dan
`docs/HOTFIX.md` disiapkan.

### 10.9 Kandidat rilis dan rilis final

`scripts/rc-check.sh` dan `docs/RC-PROCESS.md` disiapkan.

### 10.10 Audit pasca rilis

`scripts/check-release.sh` dan `docs/RELEASE.md` menyediakan daftar
pemeriksaan akhir.

## 3. Sub-fase Fase 11

### 11.1 Image ARM SBC

Konfigurasi untuk Raspberry Pi 4, Raspberry Pi 5, dan Pine64 berada di
`config/sbc/`. Build memakai `scripts/build-sbc-image.sh`.

### 11.2 Secure Boot

Konfigurasi dan kebijakan signing berada di `config/secureboot/`.
Verifikasi memakai `scripts/verify-secureboot.sh`.

### 11.3 Wayland eksperimental

Konfigurasi Labwc dan Sway berada di `config/wayland/`.

### 11.4 Arsenal GUI

Rancangan awal berada di `ui/arsenal-gui/` dan `docs/ARSENAL-GUI.md`.

### 11.5 Image cloud dan rootfs WSL

Konfigurasi cloud-init dan wsl.conf berada di `config/cloud/` dan
`config/wsl/`. Build memakai `scripts/build-cloud-image.sh`.

### 11.6 Kebijakan i386

`docs/I386-POLICY.md` menjelaskan evaluasi dan deprecation.

### 11.7 Evaluasi basis

`docs/BASIS-EVALUATION.md` dan `config/rebase/evaluation.env` menyimpan
evaluasi basis tanpa mengubah Debian 12 pada v1.

### 11.8 Dukungan hardware dan firmware

`docs/HARDWARE-ENABLEMENT.md` menjelaskan proses.

### 11.9 Lokalisasi dan aksesibilitas v2

`docs/LOCALIZATION.md` menjelaskan rencana.

### 11.10 Dukungan jangka panjang

`docs/LTS.md` menjelaskan kebijakan kanal dan rotasi kunci.

## 4. Hasil Verifikasi

| Pemeriksaan | Hasil |
|---|---|
| Dokumen baru | lulus pemeriksaan kebijakan |
| Konfigurasi baru | struktur valid |
| Skrip baru | sintaks bash valid |
| Kanal rilis | 3 kanal valid |
| Mirror | struktur disiapkan |

## 5. Langkah Berikutnya

1. Bangun tujuh artefak ISO.
2. Jalankan matriks boot dan smoke suite.
3. Publikasikan mirror dan torrent.
4. Uji image SBC dan cloud pada perangkat nyata.
