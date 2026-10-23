# Rebase ke Debian 13

ArashiOS v2 direncanakan berbasis Debian 13 trixie.

## 1. Tujuan

1. Memperbarui basis ke Debian 13.
2. Memperbarui toolchain dan kernel.
3. Mempertahankan kompatibilitas konfigurasi pengguna.

## 2. Alur

1. Audit paket yang berubah atau dihapus.
2. Perbarui pin snapshot.
3. Bangun image uji.
4. Jalankan matriks boot dan smoke test.
5. Publikasikan sebagai major baru.

## 3. Risiko

1. Perubahan ABI.
2. Paket yang dihapus upstream.
3. Perubahan konfigurasi desktop.

## 4. Konfigurasi

Berkas konfigurasi berada di `config/rebase/`.
