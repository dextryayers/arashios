# Wayland Eksperimental

Wayland disediakan sebagai sesi eksperimental pada pasca v1.

## 1. Kompositor

1. Labwc untuk LXQt.
2. Sway untuk pengguna tingkat lanjut.

## 2. Lingkup

1. Sesi Wayland opsional.
2. X11 tetap default.
3. Tidak semua tool GUI diuji pada Wayland.

## 3. Konfigurasi

Berkas konfigurasi berada di `config/wayland/`. Setiap kompositor
memiliki berkas konfigurasi dasar.

## 4. Batasan

1. Beberapa aplikasi memerlukan XWayland.
2. Screen sharing memerlukan portal tambahan.
3. Tidak ada dukungan penuh sampai v2.
