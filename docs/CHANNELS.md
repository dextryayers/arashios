# Kanal Rilis

ArashiOS memiliki tiga kanal rilis.

## 1. stable

1. Frekuensi 4 minggu.
2. Stabilitas tinggi.
3. Untuk penggunaan produksi.
4. Default pada sistem terpasang.

## 2. edge

1. Frekuensi 1 minggu.
2. Stabilitas sedang.
3. Untuk pengguna awal dan pengujian.
4. Memakai repo terpisah.

## 3. nightly

1. Frekuensi harian.
2. Stabilitas rendah.
3. Untuk kontributor dan QA.
4. Artefak disimpan 90 hari.

## 4. Konfigurasi Klien

Berkas sumber APT berada di `config/channels/`. Setiap kanal memiliki
prioritas pinning sesuai `docs/REPOSITORY.md`.

## 5. Perpindahan Kanal

Gunakan `scripts/channel-switch.sh` untuk berpindah kanal. Perpindahan
dari nightly ke stable memerlukan konfirmasi pengguna.

## 6. Pemeriksaan

`tests/channel-check.sh` memverifikasi bahwa setiap kanal memiliki berkas
sumber dan prioritas yang benar.
