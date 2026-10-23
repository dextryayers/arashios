# Evaluasi Basis

ArashiOS v1 tetap berbasis Debian 12 bookworm. Evaluasi basis berikutnya
dilakukan tanpa mengubah basis v1.

## 1. Tujuan

1. Menjaga stabilitas pada Debian 12.
2. Mengevaluasi basis berikutnya pada waktu yang tepat.
3. Mempertahankan kompatibilitas konfigurasi pengguna.

## 2. Alur

1. Audit paket yang berubah atau dihapus.
2. Perbarui pin snapshot.
3. Bangun image uji.
4. Jalankan matriks boot dan smoke test.
5. Publikasikan sebagai major baru jika siap.

## 3. Risiko

1. Perubahan ABI.
2. Paket yang dihapus upstream.
3. Perubahan konfigurasi desktop.

## 4. Konfigurasi

Berkas konfigurasi berada di `config/rebase/`.
