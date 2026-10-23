# Arsenal GUI

Arsenal GUI adalah Control Center berbasis GTK4 untuk mengelola tool.

## 1. Fitur

1. Daftar tool berdasarkan kategori.
2. Status instalasi.
3. Instalasi dan penghapusan tool.
4. Verifikasi checksum.

## 2. Arsitektur

1. Frontend GTK4.
2. Backend memakai `arashios-arsenal`.
3. Tidak ada akses jaringan otomatis.

## 3. Konfigurasi

Kode sumber berada di `ui/arsenal-gui/`. Desain mengikuti token Kage.

## 4. Batasan

1. Hanya tool T2 dan T3 yang diunduh saat pengguna memilih.
2. Tool T0 dan T1 sudah terpasang.
3. Verifikasi checksum wajib sebelum instalasi.
