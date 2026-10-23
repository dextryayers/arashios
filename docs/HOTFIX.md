# Prosedur Hotfix

## 1. Kriteria

Hotfix diterbitkan untuk:

1. Gagal boot pada arsitektur tier 1.
2. Gagal instalasi pada skenario utama.
3. Kerentanan keamanan critical atau high.
4. Kehilangan data pada installer.

## 2. Alur

1. Buat issue pelacak dengan label hotfix.
2. Perbaiki pada branch hotfix.
3. Bangun artefak baru dengan versi tanggal baru.
4. Jalankan verifikasi artefak dan smoke test.
5. Publikasikan ke kanal stable.
6. Umumkan di forum dan Matrix.

## 3. Batasan

1. Hotfix tidak menambah fitur.
2. Hotfix tidak mengubah konfigurasi desktop.
3. Hotfix tidak mengubah daftar paket utama.

## 4. Komunikasi

Setiap hotfix disertai catatan rilis singkat yang menjelaskan masalah
dan perbaikan.
